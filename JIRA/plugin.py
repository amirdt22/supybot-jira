###
# Copyright (c) 2011, Jesse Zhang
# All rights reserved.
###

import re

import suds

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import jira

class MyPluginRegexp(callbacks.PluginRegexp):
    # The original PluginRegexp lacks a way to add regexps programmatically.
    def add_regexp(self, pattern, method_name, when="always"):
        """Register a regexp pattern

        'when' can be always, addressed, or unaddressed.
          'always': method is called whether the message is addressed or not.
          'addressed': method is called only when the message is addressed.
          'unaddressed': method is called only when the message is not
                         addressed.
        """
        assert(when in ["always", "addressed", "unaddressed"])

        if when == "always":
            r = re.compile(pattern, self.flags)
            self.res.append((r, method_name))
        elif when == "addressed":
            r = re.compile(pattern, self.flags)
            self.addressedRes.append((r, method_name))
        elif when == "unaddressed":
            r = re.compile(pattern, self.flags)
            self.unaddressedRes.append((r, method_name))

class JIRA(MyPluginRegexp):
    """This plugin provides the ability to interact with Jira installs.
    """

    threaded = True

    def __init__(self, irc):
        super(JIRA, self).__init__(irc)

        soap_url = self.registryValue("soap_url")
        username = self.registryValue("username")
        password = self.registryValue("password")
        if not (soap_url and username and password):
            return

        self.jira_client = jira.JiraClient(soap_url, username, password)

        pattern = r"(?:%s)-\d+" % "|".join(self.jira_client.projects_keys)
        # It's strange that if we use when="always", and if the msg is
        # addressed, the user will get two replies. The bot would first give a
        # 'invalid command', then call the snarf method. So we don't use
        # 'always'.
        self.add_regexp(pattern, 'snarf_issue', when="addressed")
        self.add_regexp(pattern, 'snarf_issue', when="unaddressed")

    def query_issue(self, issue_id):
        msg = None
        try:
            msg = self.jira_client.query_issue(issue_id)
        except suds.WebFault:
            pass

        return msg

    def bug(self, irc, msg, args, text):
        """issue-id [<issue-id> ...]

        Report the summary of the specified issues.
        """

        for issue_id in text.split():
            msg = self.query_issue(issue_id.upper())
            if msg:
                irc.reply(msg)

    bug = wrap(bug, ["text"])

    def snarf_issue(self, irc, msg, match):
        issue_id = match.group(0).upper()
        msg = self.query_issue(issue_id)
        if msg:
            irc.reply(msg, prefixNick=False)

Class = JIRA
