A plugin for supybot to interact with JIRA installations

License: GPLv2

For now the only function is to get the summary of an issue. It can accept a
"bug <jira-name> <issue-ids>" command, and can also recognize when people
mention an issue in their messages.

It supports multiple JIRA installs, and the displaying format is configurable.

Dependencies
------------
The plugin depends on the suds library since it uses the SOAP service to
interact with JIRA. I'm using supybot-0.83.4.1 and suds-0.4.

Quick Start
-------------

    load JIRA
    jira add <name> <URL> <username> <password>
    # e.g. jira add fits http://issues.foresightlinux.org/jira <user> <pass>
    jira add <name1> <URL1> <username1> <password1>
    # more...

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
