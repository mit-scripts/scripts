#!/usr/bin/env python
#
#   Copyright Hari Sekhon 2008
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 

"""Nagios plugin to test the status of a Subversion (SVN) server. Requires
   the subversion client "svn" to be installed somewhere in the path"""

# Standard Nagios return codes
OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = 3

import os
import re
import sys
import signal
import time
try:
    from subprocess import Popen, PIPE, STDOUT
except ImportError:
    print "UNKNOWN: Failed to import python subprocess module.",
    print "Perhaps you are using a version of python older than 2.4?"
    sys.exit(CRITICAL)
from optparse import OptionParser

__author__      = "Hari Sekhon"
__title__       = "Nagios Plugin for Subversion"
__version__     = 0.4

DEFAULT_TIMEOUT = 10


def end(status, message):
    """Prints a message and exits. First arg is the status code
    Second Arg is the string message"""
    
    check_name = "SVN "
    if status == OK:
        print "%sOK: %s" % (check_name, message)
        sys.exit(OK)
    elif status == WARNING:
        print "%sWARNING: %s" % (check_name, message)
        sys.exit(WARNING)
    elif status == CRITICAL:
        print "%sCRITICAL: %s" % (check_name, message)
        sys.exit(CRITICAL)
    else:
        # This one is intentionally different
        print "UNKNOWN: %s" % message
        sys.exit(UNKNOWN)


# Pythonic version of "which", inspired by my beloved *nix core utils
# although I've decided it makes more sense to fetch a non-executable
# program and alert on it rather than say it wasn't found in the path 
# at all from a user perspective.
def which(executable):
    """Takes an executable name as a string and tests if it is in the path.
    Returns the full path of the executable if it exists in path, or None if it
    does not"""

    for basepath in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(basepath, executable)
        if os.path.isfile(path):
            if os.access(path, os.X_OK):
                return path
            else:
                #print >> sys.stderr, "Warning: '%s' in path is not executable"
                end(UNKNOWN, "svn utility '%s' is not executable" % path)

    return None


BIN = which("svn")
if not BIN:
    end(UNKNOWN, "'svn' cannot be found in path. Please install the " \
               + "subversion client or fix your PATH environment variable")


class SvnTester:
    """Holds state for the svn test"""

    def __init__(self):
        """Initializes all variables to their default states"""

        self.directory  = ""
        self.http       = False
        self.https      = False
        self.password   = ""
        self.port       = ""
        self.protocol   = "svn"
        self.server     = ""
        self.timeout    = DEFAULT_TIMEOUT
        self.username   = ""
        self.verbosity  = 0


    def validate_variables(self):
        """Runs through the validation of all test variables
        Should be called before the main test to perform a sanity check
        on the environment and settings"""

        self.validate_host()
        self.validate_protocol()
        self.validate_port()
        self.validate_timeout()


    def validate_host(self):
        """Exits with an error if the hostname 
        does not conform to expected format"""

        # Input Validation - Rock my regex ;-)
        re_hostname = re.compile("^[a-zA-Z0-9]+[a-zA-Z0-9-]*((([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6})?$")
        re_ipaddr   = re.compile("^((25[0-5]|2[0-4]\d|[01]\d\d|\d?\d)\.){3}(25[0-5]|2[0-4]\d|[01]\d\d|\d?\d)$")

        if self.server == None:
            end(UNKNOWN, "You must supply a server hostname or ip address. " \
                       + "See --help for details")

        if not re_hostname.match(self.server) and \
           not re_ipaddr.match(self.server):
            end(UNKNOWN, "Server given does not appear to be a valid " \
                       + "hostname or ip address")
    

    def validate_protocol(self):
        """Determines the protocol to use and sets it in the object"""

        if self.http and self.https:
            end(UNKNOWN, "cannot choose both http and https, they are " \
                       + "mutually exclusive")
        elif self.http:    
            self.protocol = "http"
        elif self.https:
            self.protocol = "https"
        else:
            self.protocol = "svn"


    def validate_port(self):
        """Exits with an error if the port is not valid"""

        if self.port == None:
            self.port = ""
        else:
            try:
                self.port = int(self.port)
                if not 1 <= self.port <= 65535:
                    raise ValueError
            except ValueError:
                end(UNKNOWN, "port number must be a whole number between " \
                           + "1 and 65535")


    def validate_timeout(self):
        """Exits with an error if the timeout is not valid"""

        if self.timeout == None:
            self.timeout = DEFAULT_TIMEOUT
        try:
            self.timeout = int(self.timeout)
            if not 1 <= self.timeout <= 65535:
                end(UNKNOWN, "timeout must be between 1 and 3600 seconds")
        except ValueError:
            end(UNKNOWN, "timeout number must be a whole number between " \
                       + "1 and 3600 seconds")

        if self.verbosity == None:
            self.verbosity = 0


    def run(self, cmd):
        """runs a system command and returns a tuple containing 
        the return code and the output as a single text block"""

        if cmd == "" or cmd == None:
            end(UNKNOWN, "Internal python error - " \
                       + "no cmd supplied for run function")
        
        self.vprint(3, "running command: %s" % cmd)

        try:
            process = Popen( cmd.split(), 
                             shell=False, 
                             stdin=PIPE, 
                             stdout=PIPE, 
                             stderr=STDOUT )
        except OSError, error:
            error = str(error)
            if error == "No such file or directory":
                end(UNKNOWN, "Cannot find utility '%s'" % cmd.split()[0])
            else:
                end(UNKNOWN, "Error trying to run utility '%s' - %s" \
                                                      % (cmd.split()[0], error))

        stdout, stderr = process.communicate()

        if stderr == None:
            pass

        if stdout == None or stdout == "":
            end(UNKNOWN, "No output from utility '%s'" % cmd.split()[0])
        
        returncode = process.returncode

        self.vprint(3, "Returncode: '%s'\nOutput: '%s'" % (returncode, stdout))
        return (returncode, str(stdout))


    def set_timeout(self):
        """Sets an alarm to time out the test"""

        if self.timeout == 1:
            self.vprint(2, "setting plugin timeout to 1 second")
        else:
            self.vprint(2, "setting plugin timeout to %s seconds"\
                                                                % self.timeout)

        signal.signal(signal.SIGALRM, self.sighandler)
        signal.alarm(self.timeout)


    def sighandler(self, discarded, discarded2):
        """Function to be called by signal.alarm to kill the plugin"""

        # Nop for these variables
        discarded = discarded2
        discarded2 = discarded

        if self.timeout == 1:
            timeout = "(1 second)"
        else:
            timeout = "(%s seconds)" % self.timeout

        end(CRITICAL, "svn plugin has self terminated after exceeding " \
                    + "the timeout %s" % timeout)


    def generate_uri(self):
        """Creates the uri and returns it as a string"""

        if self.port == "" or self.port == None:
            port = ""
        else:
            port = ":" + str(self.port)

        if self.directory == None:
            directory = ""
        else:
            directory = "/" + str(self.directory).lstrip("/")

        uri = self.protocol + "://"  \
              + str(self.server)     \
              + str(port)            \
              + str(directory)

        return str(uri)


    def test_svn(self):
        """Performs the test of the subversion server"""

        self.validate_variables()
        self.set_timeout()

        self.vprint(2, "now running subversion test")

        uri = self.generate_uri()

        self.vprint(3, "subversion server address is '%s'" % uri)

        cmd = BIN + " ls " + uri + " --no-auth-cache --non-interactive"
        if self.username:
            cmd += " --username=%s" % self.username
        if self.password:
            cmd += " --password=%s" % self.password

        result, output = self.run(cmd)
        
        if result == 0:
            if len(output) == 0:
                return (WARNING, "Test passed but no output was received " \
                               + "from svn program, abnormal condition, "  \
                               + "please check.")
            else:
                if self.verbosity >= 1:
                    return(OK, "svn repository online - directory listing: %s" \
                                        % output.replace("\n", " ").rstrip(" "))
                else:
                    return (OK, "svn repository online - " \
                              + "directory listing successful")
        else:
            if len(output) == 0:
                return (CRITICAL, "Connection failed. " \
                                + "There was no output from svn")
            else:
                if output == "svn: Can't get password\n":
                    output = "password required to access this repository but" \
                           + " none was given or cached"
                output = output.lstrip("svn: ")
                return (CRITICAL, "Error connecting to svn server - %s " \
                                        % output.replace("\n", " ").rstrip(" "))
 

    def vprint(self, threshold, message):
        """Prints a message if the first arg is numerically greater than the
        verbosity level"""

        if self.verbosity >= threshold:
            print "%s" % message


def main():
    """Parses args and calls func to test svn server"""

    tester = SvnTester()
    parser = OptionParser()
    parser.add_option( "-H",
                       "-S",
                       "--host",
                       "--server",
                       dest="server",
                       help="The Hostname or IP Address of the subversion "    \
                          + "server")

    parser.add_option( "-p",
                       "--port",
                       dest="port",
                       help="The port on the server to test if not using the " \
                          + "default port which is 3690 for svn://, 80 for "   \
                          + "http:// or 443 for https://.")

    parser.add_option( "--http",
                       action="store_true",
                       dest="http",
                       help="Connect to the server using the http:// " \
                          + "protocol (Default is svn://)")

    parser.add_option( "--https",
                       action="store_true",
                       dest="https",
                       help="Connect to the server using the https:// " \
                          + "protocol (Default is svn://)")

    parser.add_option( "--dir",
                       "--directory",
                       dest="directory",
                       help="The directory on the host. Optional but usually " \
                          + "necessary if using http/https, eg if using an "   \
                          + "http WebDAV repository "                          \
                          + "http://somehost.domain.com/repos/svn so this "    \
                          + "would be --dir /repos/svn. Not usually needed "   \
                          + "for the default svn:// unless you want to test "  \
                          + "a specific directory in the repository")

    parser.add_option( "-U",
                       "--username",
                       dest="username",
                       help="The username to use to connect to the subversion" \
                          + " server.")

    parser.add_option( "-P",
                       "--password",
                       dest="password",
                       help="The password to use to connect to the subversion" \
                          + " server.")

    parser.add_option( "-t",
                       "--timeout",
                       dest="timeout",
                       help="Sets a timeout after which the the plugin will"   \
                          + " self terminate. Defaults to %s seconds." \
                                                              % DEFAULT_TIMEOUT)

    parser.add_option( "-T",
                       "--timing",
                       action="store_true",
                       dest="timing",
                       help="Enable timer output")

    parser.add_option(  "-v",
                        "--verbose",
                        action="count",
                        dest="verbosity",
                        help="Verbose mode. Good for testing plugin. By "     \
                           + "default only one result line is printed as per" \
                           + " Nagios standards")

    parser.add_option( "-V",
                        "--version",
                        action = "store_true",
                        dest = "version",
                        help = "Print version number and exit" )

    (options, args) = parser.parse_args()

    if args:
        parser.print_help()
        sys.exit(UNKNOWN)

    if options.version:
        print "%s %s" % (__title__, __version__)
        sys.exit(UNKNOWN)

    tester.directory  = options.directory
    tester.http       = options.http
    tester.https      = options.https
    tester.password   = options.password
    tester.port       = options.port
    tester.server     = options.server
    tester.timeout    = options.timeout
    tester.username   = options.username
    tester.verbosity  = options.verbosity

    if options.timing:
        start_time = time.time()

    returncode, output = tester.test_svn()

    if options.timing:
        finish_time = time.time()
        total_time = finish_time - start_time
        
        output += ". Test completed in %.3f seconds" % total_time

    end(returncode, output)
    sys.exit(UNKNOWN)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Caught Control-C..."
        sys.exit(CRITICAL)
