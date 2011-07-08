# The original PluginRegexp lacks a way to add regexps programmatically.

import re

from supybot.callbacks import Plugin, SimpleProxy, Error

class PluginSnarfer(Plugin):

    flags = re.I
    Proxy = SimpleProxy

    def __init__(self, irc):
        Plugin.__init__(self, irc)
        self._res = []
        self._addressedRes = []
        self._unaddressedRes = []

    def _callRegexp(self, name, irc, msg, m, extra_args):
        method = getattr(self, name)
        try:
            method(irc, msg, m, **extra_args)
        except Error, e:
            irc.error(str(e))
        except Exception, e:
            self.log.exception('Uncaught exception in _callRegexp:')

    def invalidCommand(self, irc, msg, tokens):
        s = ' '.join(tokens)
        for (r, name, args) in self._addressedRes:
            for m in r.finditer(s):
                self._callRegexp(name, irc, msg, m, args)

    def doPrivmsg(self, irc, msg):
        if msg.isError:
            return
        proxy = self.Proxy(irc, msg)
        if not msg.addressed:
            for (r, name, args) in self._unaddressedRes:
                for m in r.finditer(msg.args[1]):
                    self._callRegexp(name, proxy, msg, m, args)
        for (r, name, args) in self._res:
            for m in r.finditer(msg.args[1]):
                self._callRegexp(name, proxy, msg, m, args)

    def add_snarfer(self, pattern, when, method, **extra_args):
        """Register a regexp pattern

        'when' can be always, addressed, or unaddressed.
          'always': method is called whether the message is addressed or not.
          'addressed': method is called only when the message is addressed.
          'unaddressed': method is called only when the message is not
                         addressed.
        'method' is the name of the method to call if the pattern is found.
        'extra_args' is the extra arguments to pass to method.
        """
        assert(when in ["always", "addressed", "unaddressed"])

        r = re.compile(pattern, self.flags)
        if when == "always":
            self._res.append((r, method, extra_args))
        elif when == "addressed":
            self._addressedRes.append((r, method, extra_args))
        elif when == "unaddressed":
            self._unaddressedRes.append((r, method, extra_args))
