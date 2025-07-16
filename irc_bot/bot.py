#!/usr/bin/env python
# -*- coding: utf-8 -*-

from irc.client import SimpleIRCClient
import time
import sys

message = sys.argv[1]

class IrcClient(SimpleIRCClient):

    def __init__(self, nick):
        self.nick = nick
        self.loading = False
        SimpleIRCClient.__init__(self)

    def on_welcome(self, c, e):
        c.join("#gentoo-kernelci")

    def on_join(self, c, e):
        while True:
            c.privmsg('#gentoo-kernelci', message)
            time.sleep(2)
            c.disconnect()


client = IrcClient("ArisuBot")
client.connect("irc.libera.chat", 6667, "ArisuBot")
client.start()
