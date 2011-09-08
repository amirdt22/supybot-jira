"""
Interact with JIRA installations
"""

import supybot
import supybot.world as world

__version__ = "git"
__author__ = supybot.Author("Jesse Zhang", "jesse", "zh.jesse@gmail.com")
__contributors__ = {}
__url__ = 'https://github.com/zhangsen/supybot-jira'

import config
import plugin
import jira
import snarfer_plugin
reload(plugin) # In case we're being reloaded.
reload(jira)
reload(snarfer_plugin)

if world.testing:
    import test

Class = plugin.Class
configure = config.configure
