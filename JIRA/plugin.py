###
# Copyright (c) 2011, Jesse Zhang
# All rights reserved.
###

import suds

from supybot import conf
from supybot import ircutils
from supybot import registry
from supybot.commands import wrap
from supybot.utils.structures import TimeoutQueue

from snarfer_plugin import PluginSnarfer
import jira

class JIRA(PluginSnarfer):
    """This plugin provides the ability to interact with Jira installs.
    """

    threaded = True

    def __init__(self, irc):
        super(JIRA, self).__init__(irc)

        self.jiras = {}
        for name in self.registryValue("installs"):
            self.register_jira(name, base=conf.supybot.plugins.JIRA.installs)
            self.connect_jira(name)

        # A timeout list, so that if an issue is mentioned several times in a
        # row, the bot won't flood the channel.
        self.snarfer_timeout_list = ircutils.IrcDict()

    def register_jira(self, handle, base):
        group = conf.registerGroup(base, handle)
        conf.registerGlobalValue(group, "url",
                registry.String("", "URL of the JIRA install, e.g. " \
                        "http://issues.foresightlinux.org/jira"))
        conf.registerGlobalValue(group, "username",
                registry.String("", "Username to login the JIRA install",
                    private=True))
        conf.registerGlobalValue(group, "password",
                registry.String("", "Password to login the JIRA install",
                    private=True))

    def configure_jira(self, name, url, username, password):
        install = "installs.%s" % name
        self.setRegistryValue('%s.url' % install, url)
        self.setRegistryValue('%s.username' % install, username)
        self.setRegistryValue('%s.password' % install, password)

    def register_regexp(self, jira_name):
        keys = self.jiras[jira_name].get_projects_keys()
        # A project key followed by some numbers, e.g. FL-1234.
        pattern = r"\b(?:%s)-\d+\b" % "|".join(keys)
        # It's strange that if we use when="always", and if the msg is
        # addressed, the user will get two replies. The bot would first give a
        # 'invalid command', then call the snarf method. So we don't use
        # 'always'.
        self.add_snarfer(pattern, when="addressed", method='snarf_issue',
                jira_name=jira_name)
        self.add_snarfer(pattern, when="unaddressed", method='snarf_issue',
                jira_name=jira_name)

    def connect_jira(self, name):
        install = "installs.%s." % name

        url = self.registryValue(install + "url")
        username = self.registryValue(install + "username")
        password = self.registryValue(install + "password")
        if not (url and username and password):
            return

        soap_url = url + "/rpc/soap/jirasoapservice-v2?wsdl"
        self.jiras[name] = jira.JiraClient(soap_url, username, password)

        self.register_regexp(name)

    def add(self, irc, msg, args, name, url, username, password):
        """add <name> <url> <username> <password>

        Let the bot know about a new JIRA install. Name is how the install will
        be referred to. URL is where it's located, e.g.
        http://issues.foresightlinux.org/jira. Username and password are used
        to login to JIRA.
        """
        name = name.lower()
        self.register_jira(name, base=conf.supybot.plugins.JIRA.installs)

        installs = self.registryValue("installs")
        installs.append(name)
        self.setRegistryValue('installs', installs)

        self.configure_jira(name, url, username, password)
        self.connect_jira(name)
        irc.replySuccess()

    add = wrap(add, ["admin", "private", "somethingWithoutSpaces", "url",
        "somethingWithoutSpaces", "somethingWithoutSpaces"])

    def list(self, irc, msg, args):
        """list

        List the JIRA installs the bot knows about.
        """
        if not self.jiras:
            irc.reply("I don't know about any JIRA install.")

        for j in self.jiras:
            reply = "%s: URL = %s; matches %s." % (
                    ircutils.bold(j),
                    self.registryValue("installs.%s.url" % j),
                    self.jiras[j].get_projects_keys())
            irc.reply(reply)

    list = wrap(list)

    def format_issue_time(self, time):
        # E.g. 'Sun 2011-05-29 14:33'
        return time.strftime("%a %Y-%m-%d %H:%M")

    def query_issue(self, jira_name, issue_id, channel):

        def format_url():
            base = self.registryValue("installs.%s.url" % jira_name)
            if base.endswith("/"):
                base = base[:-1]
            return "%s/browse/%s" % (base, issue_id)

        jiraclient = self.jiras[jira_name]

        issue = None
        try:
            issue = jiraclient.query_issue(issue_id)
        except suds.WebFault:
            pass

        if not issue:
            return None

        # Transform the fields into displayable strings
        issue.status = jiraclient.get_status_string(issue.status)
        issue.resolution = jiraclient.get_resolution_string(issue.resolution)
        issue.created = self.format_issue_time(issue.created)
        issue.updated = self.format_issue_time(issue.updated)
        issue.reporter = jiraclient.get_user_fullname(issue.reporter)
        issue.assignee = jiraclient.get_user_fullname(issue.assignee)

        msg = "%s: %s." % (ircutils.bold(issue_id), issue.summary)
        # Append requested fields to the message
        for field in self.registryValue("issue_format", channel):
            msg += " %s: %s." % (ircutils.bold(field.capitalize()),
                    getattr(issue, field))

        # Append the URL
        if self.registryValue("show_link", channel):
            msg += " " + format_url()

        msg = msg.encode("utf-8")
        return msg

    def bug(self, irc, msg, args, jira_name, text):
        """<jira-name> <issue-id> [<issue-id> ...]

        Report the summary of the specified issues.
        """

        if not jira_name in self.jiras:
            irc.reply("I know nothing about %s." % jira_name)

        channel = msg.args[0]
        for issue_id in text.split():
            reply = self.query_issue(jira_name, issue_id.upper(), channel)
            if not reply:
                reply = "%s doesn't seem to exist." % issue_id
            irc.reply(reply)

    bug = wrap(bug, ["somethingWithoutSpaces", "text"])

    def issue_blocked(self, issue_id, channel):
        # Add channel to the timeout list.
        if channel not in self.snarfer_timeout_list:
            timeout = self.registryValue("snarfer_timeout", channel)
            self.snarfer_timeout_list[channel] = TimeoutQueue(timeout)

        if issue_id in self.snarfer_timeout_list[channel]:
            # The timeout hasn't expired yet.
            ret = True
        else:
            # The timeout expired. Add the issue to the queue again.
            self.snarfer_timeout_list[channel].enqueue(issue_id)
            ret = False

        return ret

    def snarf_issue(self, irc, msg, match, jira_name):
        channel = msg.args[0]
        issue_id = match.group(0).upper()

        reply = None
        if self.issue_blocked(issue_id, channel):
            if msg.addressed:
                reply = "%s was already queried within the last %s seconds." % (
                        issue_id,
                        self.registryValue("snarfer_timeout", channel))
        else:
            summary = self.query_issue(jira_name, issue_id, channel)
            if summary:
                reply = summary
            elif msg.addressed:
                reply = "%s doesn't seem to exist." % issue_id

        if reply:
            irc.reply(reply, prefixNick=False)

Class = JIRA
