###
# Copyright (c) 2011, Jesse Zhang
# All rights reserved.
###

"""
Interact with JIRA installations
"""

import supybot
import supybot.world as world

__version__ = "git"
__author__ = supybot.Author("Jesse Zhang", "jesse", "zh.jesse@gmail.com")
__contributors__ = {}
__url__ = 'githut.com'

import config
import plugin
import jira
reload(plugin) # In case we're being reloaded.
reload(jira)

if world.testing:
    import test

Class = plugin.Class
configure = config.configure
