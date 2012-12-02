#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    A pure python ping implementation using raw sockets.

    Note that ICMP messages can only be send from processes running as root
    (in Windows, you must run this script as 'Administrator').

    :homepage: https://github.com/alexlouden/python-ping/
    :copyleft: 1989-2012 by the python-ping team, see AUTHORS for more details.
    :license: GNU GPL v2, see LICENSE for more details.
"""

from ping import Ping, defaults
import time

class Pinger(object):
    def __init__(self, hostname,
            buffer_size = defaults.buffer_size,
            timeout = defaults.timeout,
            continous = False,
            count = defaults.pinger_count,
            interval = defaults.interval):

        self.hostname = hostname

        self.delays = []
        self.ping = Ping(hostname, buffer_size, timeout)

        start_time = defaults.timer()

        if not continous and not count:
            return

        i = 0
        while True:

            try:

                # Wait, to run do() every interval seconds
                time.sleep(start_time + i*interval - defaults.timer())

                # Do ping
                self.ping.do()
                self.delays.append(self.ping.delay)
                print self.ping

            # Catch Ctrl + C
            except KeyboardInterrupt:
                print ""
                print self.statistics()
                # Exit sucessfully if loss is less than 50%
                return

            # Increment count
            i += 1

            # Break out of loop
            if count and i >= count:
                break

        print self.statistics()
        # Exit sucessfully if loss is less than 50%
        return

    def statistics(self):
        self.lost = self.ping.sent - self.ping.received
        self.loss = self.lost / self.ping.sent
        self.dmin = min(self.delays)
        self.dmax = max(self.delays)

        average = lambda x: sum(x) / len(x)

        # Average delay
        self.davg = average(self.delays)

        # Calculate standard deviation of the delays
        self.jitter = average([(d - self.davg)**2 for d in self.delays])**0.5

        return """Ping statistics for {0.hostname}:
        Packets: Sent = {0.ping.sent}, Received = {0.ping.received}, Lost = {0.lost} ({0.loss:.2f}% loss),
        Approximate round trip times in milli-seconds:
        Minimum = {0.dmin:.2f}ms, Maximum = {0.dmax:.2f}ms
        Average = {0.davg:.2f}ms, Jitter = {0.jitter:.2f}ms""".format(self)

