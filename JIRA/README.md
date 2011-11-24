A supybot plugin to interact with the JIRA issue tracking system

License: GPLv2

Features
--------

* Detect when an issue is mentioned and print the summary of the issue
* Support multiple JIRA installs
* Format of issue summary is configurable

Dependencies
------------
The plugin depends on the suds library since it uses the SOAP service to
interact with JIRA. I'm using supybot-0.83.4.1 and suds-0.4.

Quick Start
-------------

    load JIRA
    jira add <name> <URL> <username> <password>
    jira add <name1> <URL1> <username1> <password1>

Example `jira add`:

    jira add fits http://issues.foresightlinux.org/ <user> <pass>

Usage
-----------------------

* Add a JIRA install: `jira add <name> <URL> <username> <password>`
    * `name`: how the bot will address this install. Should be unique between
      all JIRA installs known to the bot.
    * `username` and `password`: the bot needs to log into the JIRA.
* The bot will automatically recognize issue numbers (Can't be turned off for now).

Configuration
-------------

* `plugins.jira.show_link`: show issue URL at the end of the summary
* `plugins.jira.issue_format`: Possible (and default) values: status resolution
  created updated reporter assignee
* `plugins.jira.snarfer_timeout`: Seconds to wait before automatically
  responding to an issue again. (Doesn't apply when the bot is explicitly addressed.)
* `plugins.jira.installs`: list of all JIRA installs
* information of a JIRA install: `plugins.jira.installs.name.url`,
  `plugins.jira.installs.name.username`, `plugins.jira.installs.name.password`.
  (as specified in the `jira add` call)

Use `config help` to read more about a configuration option.

A bug
-----

Supybot needs one patch to work well with suds.

    --- src/log.py        2011-06-25 00:48:08.903280326 -0400
    +++ src/log.py        2011-06-25 00:26:11.454604769 -0400
    @@ -85,7 +85,7 @@
             # self.error('Exception string: %s', eStrId)

         def _log(self, level, msg, args, exc_info=None):
    -        msg = format(msg, *args)
    +        msg = format(str(msg), *args)
             logging.Logger._log(self, level, msg, (), exc_info=exc_info)

supybot has its own logging processing. But it can't handle when a non-string
(e.g. an object of a class) is passed to the log functions.

      File "build/bdist.linux-x86_64/egg/suds/client.py", line 648, in send
        log.error(self.last_sent())
      File "/usr/lib64/python2.6/logging/__init__.py", line 1082, in error
        self._log(ERROR, msg, args, **kwargs)
      File "/home/jesse/.root/lib/python2.6/site-packages/supybot/log.py", line 88, in _log
        msg = format(msg, *args)
      File "/home/jesse/.root/lib/python2.6/site-packages/supybot/utils/str.py", line 437, in format
        return _formatRe.sub(sub, s)
    TypeError: expected string or buffer

Another bug
-----------

suds-0.4 needs this oneliner in order to return time correctly when in
Daylight Saving Time.

    https://bitbucket.org/mirror/suds/changeset/9e91e1cec4b1#chg-suds/sax/date.py

TODO
----

* Don't respond if the user is another bot
* Add option to disable snarfer
