"""
Wrappers around subprocess functionality that simulate an actual shell.
"""

import subprocess
import logging
import sys
import os
import errno

class Shell(object):
    """
    An advanced shell that performs logging.  If ``dry`` is ``True``,
    no commands are actually run.
    """
    def __init__(self, dry = False):
        self.dry = dry
        self.cwd = None
    def call(self, *args, **kwargs):
        """
        Performs a system call.  The actual executable and options should
        be passed as arguments to this function.  Several keyword arguments
        are also supported:

        :param input: input to feed the subprocess on standard input.
        :param interactive: whether or not directly hook up all pipes
            to the controlling terminal, to allow interaction with subprocess.
        :param strip: if ``True``, instead of returning a tuple,
            return the string stdout output of the command with trailing newlines
            removed.  This emulates the behavior of backticks and ``$()`` in Bash.
            Prefer to use :meth:`eval` instead (you should only need to explicitly
            specify this if you are using another wrapper around this function).
        :param log: if True, we log the call as INFO, if False, we log the call
            as DEBUG, otherwise, we detect based on ``strip``.
        :param stdout:
        :param stderr:
        :param stdin: a file-type object that will be written to or read from as a pipe.
        :returns: a tuple of strings ``(stdout, stderr)``, or a string ``stdout``
            if ``strip`` is specified.

        >>> sh = Shell()
        >>> sh.call("echo", "Foobar")
        ('Foobar\\n', '')
        >>> sh.call("cat", input='Foobar')
        ('Foobar', '')
        """
        self._wait()
        kwargs.setdefault("interactive", False)
        kwargs.setdefault("strip", False)
        kwargs.setdefault("python", None)
        kwargs.setdefault("log", None)
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stdin", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
        msg = "Running `" + ' '.join(args) + "`"
        if kwargs["strip"] and not kwargs["log"] is True or kwargs["log"] is False:
            logging.debug(msg)
        else:
            logging.info(msg)
        if self.dry:
            if kwargs["strip"]:
                return ''
            return None, None
        kwargs.setdefault("input", None)
        if kwargs["interactive"]:
            stdout=sys.stdout
            stdin=sys.stdin
            stderr=sys.stderr
        else:
            stdout=kwargs["stdout"]
            stdin=kwargs["stdin"]
            stderr=kwargs["stderr"]
        # XXX: There is a possible problem here where we can fill up
        # the kernel buffer if we have 64KB of data.  This shouldn't
        # be a problem, and the fix for such case would be to write to
        # temporary files instead of a pipe.
        # Another possible way of fixing this is converting from a
        # waitpid() pump to a select() pump, creating a pipe to
        # ourself, and then setting up a
        # SIGCHILD handler to write a single byte to the pipe to get
        # us out of select() when a subprocess exits.
        proc = subprocess.Popen(args, stdout=stdout, stderr=stderr, stdin=stdin, cwd=self.cwd, )
        if self._async(proc, args, **kwargs):
            return proc
        stdout, stderr = proc.communicate(kwargs["input"])
        # can occur if we were doing interactive communication; i.e.
        # we didn't pass in PIPE.
        if stdout is None:
            stdout = ""
        if stderr is None:
            stderr = ""
        if not kwargs["interactive"]:
            if kwargs["strip"]:
                self._log(None, stderr)
            else:
                self._log(stdout, stderr)
        if proc.returncode:
            raise CallError(proc.returncode, args, stdout, stderr)
        if kwargs["strip"]:
            return str(stdout).rstrip("\n")
        return (stdout, stderr)
    def _log(self, stdout, stderr):
        """Logs the standard output and standard input from a command."""
        if stdout:
            logging.debug("STDOUT:\n" + stdout)
        if stderr:
            logging.debug("STDERR:\n" + stderr)
    def _wait(self):
        pass
    def _async(self, *args, **kwargs):
        return False
    def callAsUser(self, *args, **kwargs):
        """
        Performs a system call as a different user.  This is only possible
        if you are running as root.  Keyword arguments
        are the same as :meth:`call` with the following additions:

        :param user: name of the user to run command as.
        :param uid: uid of the user to run command as.

        .. note::

            The resulting system call internally uses :command:`sudo`,
            and as such environment variables will get scrubbed.  We
            manually preserve :envvar:`SSH_GSSAPI_NAME`.
        """
        user = kwargs.pop("user", None)
        uid = kwargs.pop("uid", None)
        if not user and not uid: return self.call(*args, **kwargs)
        if os.getenv("SSH_GSSAPI_NAME"):
            # This might be generalized as "preserve some environment"
            args = list(args)
            args.insert(0, "SSH_GSSAPI_NAME=" + os.getenv("SSH_GSSAPI_NAME"))
        if uid: return self.call("sudo", "-u", "#" + str(uid), *args, **kwargs)
        if user: return self.call("sudo", "-u", user, *args, **kwargs)
    def safeCall(self, *args, **kwargs):
        """
        Checks if the owner of the current working directory is the same
        as the current user, and if it isn't, attempts to sudo to be
        that user.  The intended use case is for calling Git commands
        when running as root, but this method should be used when
        interfacing with any moderately complex program that depends
        on working directory context.  Keyword arguments are the
        same as :meth:`call`.
        """
        if os.getuid():
            return self.call(*args, **kwargs)
        uid = os.stat(os.getcwd()).st_uid
        # consider also checking ruid?
        if uid != os.geteuid():
            kwargs['uid'] = uid
            return self.callAsUser(*args, **kwargs)
        else:
            return self.call(*args, **kwargs)
    def eval(self, *args, **kwargs):
        """
        Evaluates a command and returns its output, with trailing newlines
        stripped (like backticks in Bash).  This is a convenience method for
        calling :meth:`call` with ``strip``.

            >>> sh = Shell()
            >>> sh.eval("echo", "Foobar") 
            'Foobar'
        """
        kwargs["strip"] = True
        return self.call(*args, **kwargs)
    def setcwd(self, cwd):
        """
        Sets the directory processes are executed in. This sets a value
        to be passed as the ``cwd`` argument to ``subprocess.Popen``.
        """
        self.cwd = cwd

class ParallelShell(Shell):
    """
    Modifies the semantics of :class:`Shell` so that
    commands are queued here, and executed in parallel using waitpid
    with ``max`` subprocesses, and result in callback execution
    when they finish.

    .. method:: call(*args, **kwargs)

        Enqueues a system call for parallel processing.  If there are
        no openings in the queue, this will block.  Keyword arguments
        are the same as :meth:`Shell.call` with the following additions:

        :param on_success: Callback function for success (zero exit status).
            The callback function should accept two arguments,
            ``stdout`` and ``stderr``.
        :param on_error: Callback function for failure (nonzero exit status).
            The callback function should accept one argument, the
            exception that would have been thrown by the synchronous
            version.
        :return: The :class:`subprocess.Proc` object that was opened.

    .. method:: callAsUser(*args, **kwargs)

        Enqueues a system call under a different user for parallel
        processing.  Keyword arguments are the same as
        :meth:`Shell.callAsUser` with the additions of keyword
        arguments from :meth:`call`.

    .. method:: safeCall(*args, **kwargs)

        Enqueues a "safe" call for parallel processing.  Keyword
        arguments are the same as :meth:`Shell.safeCall` with the
        additions of keyword arguments from :meth:`call`.

    .. method:: eval(*args, **kwargs)

        No difference from :meth:`call`.  Consider having a
        non-parallel shell if the program you are shelling out
        to is fast.

    """
    def __init__(self, dry = False, max = 10):
        super(ParallelShell, self).__init__(dry=dry)
        self.running = {}
        self.max = max # maximum of commands to run in parallel
    @staticmethod
    def make(no_parallelize, max):
        """Convenience method oriented towards command modules."""
        if no_parallelize:
            return DummyParallelShell()
        else:
            return ParallelShell(max=max)
    def _async(self, proc, args, python, on_success, on_error, **kwargs):
        """
        Gets handed a :class:`subprocess.Proc` object from our deferred
        execution.  See :meth:`Shell.call` source code for details.
        """
        self.running[proc.pid] = (proc, args, python, on_success, on_error)
        return True # so that the parent function returns
    def _wait(self):
        """
        Blocking call that waits for an open subprocess slot.  This is
        automatically called by :meth:`Shell.call`.
        """
        # XXX: This API sucks; the actual call/callAsUser call should
        # probably block automatically (unless I have a good reason not to)
        # bail out immediately on initial ramp up
        if len(self.running) < self.max: return
        # now, wait for open pids.
        try:
            self.reap(*os.waitpid(-1, 0))
        except OSError as e:
            if e.errno == errno.ECHILD: return
            raise
    def join(self):
        """Waits for all of our subprocesses to terminate."""
        try:
            while True:
                self.reap(*os.waitpid(-1, 0))
        except OSError as e:
            if e.errno == errno.ECHILD: return
            raise
    def reap(self, pid, status):
        """Reaps a process."""
        # ooh, zombie process. reap it
        proc, args, python, on_success, on_error = self.running.pop(pid)
        # XXX: this is slightly dangerous; should actually use
        # temporary files
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        self._log(stdout, stderr)
        if status:
            on_error(CallError(proc.returncode, args, stdout, stderr))
            return
        on_success(stdout, stderr)

# Setup a convenience global instance
shell = Shell()
call = shell.call
callAsUser = shell.callAsUser
safeCall = shell.safeCall
eval = shell.eval

class DummyParallelShell(ParallelShell):
    """Same API as :class:`ParallelShell`, but doesn't actually
    parallelize (i.e. all calls to :meth:`wait` block.)"""
    def __init__(self, dry = False):
        super(DummyParallelShell, self).__init__(dry=dry, max=1)

class CallError:
    """Indicates that a subprocess call returned a nonzero exit status."""
    #: The exit code of the failed subprocess.
    code = None
    #: List of the program and arguments that failed.
    args = None
    #: The stdout of the program.
    stdout = None
    #: The stderr of the program.
    stderr = None
    def __init__(self, code, args, stdout, stderr):
        self.code = code
        self.args = args
        self.stdout = stdout
        self.stderr = stderr
    def __str__(self):
        compact = self.stderr.rstrip().split("\n")[-1]
        return "%s (exited with %d)\n%s" % (compact, self.code, self.stderr)
