JSON Lines Ansible callback plugin
==================================

This Ansible callback plugin will output play data as [JSON Lines](https://jsonLines.org/).

I needed something that would print JSON Lines for me as each task was being performed, without having to wait for the full JSON output at the end of the play as the JSON callback plugin does it.

This plugin is limited, but will return JSON Lines for most things:

```js
// Plays
{"type": "play", "name": "hello i am a testo play"}

// Tasks
{"type": "task", "name": "skip me", "host": "localhost", "state": "skipped", "result": {"_ansible_no_log": false}}
{"type": "task", "name": "doing a thing", "host": "localhost", "state": "ok", "result": {"_ansible_verbose_always": true, "changed": false, "msg": "yay", "_ansible_no_log": false}}
{"type": "task", "name": "Make a temp file", "host": "localhost", "state": "changed", "result": {"changed": true, "path": "/tmp/ansible.1kds1nvv", "uid": 1000, "gid": 1000, "owner": "vincent", "group": "vincent", "mode": "0600", "state": "file", "size": 0, "invocation": {"module_args": {"state": "file", "prefix": "ansible.", "suffix": "", "path": null}}, "_ansible_no_log": false}}

// Handlers
{"type": "handler", "name": "start handler"}
{"type": "task", "name": "start handler", "host": "localhost", "state": "ok", "result": {"msg": "hi i am handler", "_ansible_verbose_always": true, "_ansible_no_log": false}}

// Host matching
{"type": "play", "name": "fake play"}
{"type": "skip_play", "reason": "no hosts matched", "play_name": "fake play"}

// Recap
{"type": "play_recap", "hosts": {"localhost": {"ok": 5, "failures": 0, "unreachable": 0, "changed": 1, "skipped": 1, "rescued": 0, "ignored": 0}}}
```

## Note: this does not output pure jsonl!

The actual JSON Lines spec requires that Each Line is a Valid JSON Value.

This plugin does not currently filter out any of Ansible's own debug and warning output. So upon parsing incoming lines, ensure that you perform a check if the line is valid JSON first.

## To enable

Copy the plugin to a location Ansible checks.
Add the following lines to your ansible.cfg:

```ini
stdout_callback=jsonl
bin_ansible_callbacks=true
```