# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.six.moves import shlex_quote
from ansible.plugins.action import ActionBase
from datetime import datetime


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)

        path = self._task.args.get('path')

        try:
            getcap = self._low_level_execute_command(cmd='getcap %s' % shlex_quote(path))
            # N.B. We don't check rc or stderr here, so missing files will be skipped.
            if len(getcap['stdout']) > 0:
                result['changed'] = True
                if not self._play_context.check_mode:
                    result.update(self._low_level_execute_command(cmd='setcap -r %s' % shlex_quote(path)))
        except AnsibleAction as e:
            result.update(e.result)

        return result

