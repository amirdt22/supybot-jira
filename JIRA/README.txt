A plugin for supybot to interact with JIRA installations

For now the only function is to get the summary of an issue. It can accept a
"bug <issue-ids>" command, and can also recognize when people mention an issue
in their messages.

Necessary configuration:

    config supybot.plugins.JIRA.soap_url <URL to the JIRA SOAP service, e.g. http://issues.foresightlinux.org/jira/rpc/soap/jirasoapservice-v2?wsdl>
    config supybot.plugins.JIRA.username <username-to-log-into-JIRA>
    config supybot.plugins.JIRA.password <password-to-log-into-JIRA>
    reload JIRA
