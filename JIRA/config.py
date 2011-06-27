###
# Copyright (c) 2011, Jesse Zhang
# All rights reserved.
###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    conf.registerPlugin("JIRA", True)

default_fields = ("status", "resolution", "created", "updated", "reporter",
    "assignee")

class FieldOfIssue(registry.OnlySomeStrings):
    """That is not a valid field of issue."""
    validStrings = default_fields

class AcceptedFieldsOfIssue(registry.SpaceSeparatedListOfStrings):
    Value = FieldOfIssue

JIRA = conf.registerPlugin("JIRA")
conf.registerGlobalValue(JIRA, "soap_url",
        registry.String("", "SOAP URL of the JIRA install, e.g. " \
                "http://issues.foresightlinux.org/jira/rpc/soap/jirasoapservice-v2?wsdl"))
conf.registerGlobalValue(JIRA, "username",
        registry.String("", "Username to login the JIRA install", private=True))
conf.registerGlobalValue(JIRA, "password",
        registry.String("", "Password to login the JIRA install", private=True))
conf.registerChannelValue(JIRA, "issue_format",
        AcceptedFieldsOfIssue(default_fields,
            "The fields to list when describing an issue. " \
            "Possible values include: %s." % " ".join(default_fields)))
conf.registerChannelValue(JIRA, "show_url",
        registry.String("", "The URL to prepend to an issue number and format " \
                "a link to the issue, e.g. http://issues.foresightlinux.org/jira/browse/. " \
                "Disabled if empty."))
