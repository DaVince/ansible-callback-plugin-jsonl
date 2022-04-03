# (c) 2022, Vincent Beers <vincentbeers@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.utils.color import hostcolor
import json

DOCUMENTATION = '''
    name: jsonl
    type: stdout
    short_description: JSON Lines Ansible screen output
    description:
        - This callback plugin outputs each task as a valid JSON line.
'''


class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'jsonl'

    task_colors = {
        'changed': C.COLOR_CHANGED,
        'ok': C.COLOR_OK,
        'skipped': C.COLOR_SKIP,
        'unreachable': C.COLOR_UNREACHABLE,
        'failed': C.COLOR_ERROR
    }

    def display_task_result(self, result, state):
        '''Display result for a task'''
        color = self.task_colors[state]

        status_json = {
            "type": "task",
            "name": result.task_name.strip(),
            "host": self.host_label(result),
            "state": state
        }

        # Display more data on higher verbosity
        if self._display.verbosity > 1:
            status_json["check_mode"] = result._task.check_mode

        # Add result to dict
        status_json["result"] = result._result

        self._display.display(json.dumps(status_json), color=color)

    def v2_playbook_on_play_start(self, play):
        '''Display play information when play starts'''
        play_json = {
            "type": "play",
            "name": play.get_name().strip()
        }
        if self._display.verbosity > 1:
            play_json["vars"] = play.get_vars()

        self.current_play = play_json
        self._display.display(json.dumps(play_json))

    def v2_playbook_on_no_hosts_matched(self):
        play_skip_json = {
            "type": "skip_play",
            "reason": "no hosts matched",
            "play_name": self.current_play["name"]
        }
        self._display.display(json.dumps(play_skip_json), color=C.COLOR_SKIP)

    def v2_runner_on_ok(self, result):
        '''For both ok and changed tasks'''
        self._clean_results(result._result, result._task.action)
        self._handle_warnings(result._result)
        state = 'changed' if result.is_changed() else 'ok'
        self.display_task_result(result, state)

    def v2_runner_on_skipped(self, result):
        self._clean_results(result._result, result._task.action)
        self.display_task_result(result, 'skipped')

    def v2_runner_on_unreachable(self, result):
        self._clean_results(result._result, result._task.action)
        self._handle_exception(result._result, use_stderr=True)
        self.display_task_result(result, 'unreachable')

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._clean_results(result._result, result._task.action)
        self._handle_exception(result._result, use_stderr=True)
        self._handle_warnings(result._result)
        self.display_task_result(result, 'failed')

    def v2_playbook_on_handler_task_start(self, task):
        status_json = {
            "type": "handler",
            "name": task.get_name().strip()
        }
        self._display.display(json.dumps(status_json))

    def v2_playbook_on_stats(self, stats):
        '''Display play recap'''
        recap_json = {
            "type": "play_recap",
            "hosts": {}
        }
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            recap_json["hosts"][h] = stats.summarize(h)
        self._display.display(json.dumps(recap_json))

    def _handle_warnings(self, res):
        if C.ACTION_WARNINGS:
            if 'warnings' in res and res['warnings']:
                for warning in res['warnings']:
                    self._display.warning(warning)
                del res['warnings']
            if 'deprecations' in res and res['deprecations']:
                for warning in res['deprecations']:
                    self._display.deprecated(**warning)
                del res['deprecations']
