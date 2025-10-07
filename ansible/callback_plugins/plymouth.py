#!/usr/bin/python

# Ansible callback plugin to show progress in Plymouth
# Based on the default stdout callback with added Plymouth messaging

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: plymouth
    type: stdout
    short_description: Plymouth integration for showing progress
    description:
        - This shows playbook progress in the Plymouth boot splash
    extends_documentation_fragment:
      - default_callback
'''

import subprocess
from ansible.plugins.callback.default import CallbackModule as DefaultCallbackModule

class CallbackModule(DefaultCallbackModule):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'plymouth'

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._plymouth_available = self._check_plymouth()

    def _check_plymouth(self):
        try:
            result = subprocess.run(['plymouth', '--ping'], capture_output=True)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def plymouth_message(self, message):
        if self._plymouth_available:
            try:
                subprocess.run(['plymouth', 'display-message', '--text', message], 
                               capture_output=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

    def v2_playbook_on_play_start(self, play):
        super(CallbackModule, self).v2_playbook_on_play_start(play)
        name = play.get_name().strip()
        if name:
            msg = "PLAY: %s" % name
        else:
            msg = "PLAY"
        self.plymouth_message(msg)

    def v2_playbook_on_task_start(self, task, is_conditional):
        super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)
        self.plymouth_message(f"TASK: {task.get_name()}")

    def v2_runner_on_ok(self, result, **kwargs):
        super(CallbackModule, self).v2_runner_on_ok(result, **kwargs)
        self.plymouth_message(f"OK: {result._host.get_name()}")

    def v2_runner_on_failed(self, result, **kwargs):
        super(CallbackModule, self).v2_runner_on_failed(result, **kwargs)
        self.plymouth_message(f"FAILED: {result._host.get_name()}")

    def v2_playbook_on_stats(self, stats):
        super(CallbackModule, self).v2_playbook_on_stats(stats)
        hosts = sorted(stats.processed.keys())
        summary = []
        for h in hosts:
            s = stats.summarize(h)
            summary.append(f"{h}: ok={s['ok']}, changed={s['changed']}, failed={s['failures']}")
        
        self.plymouth_message("PLAY SUMMARY: " + ", ".join(summary))