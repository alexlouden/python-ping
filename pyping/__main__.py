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

import argparse
import sys

from ping import Ping, defaults
from pinger import Pinger

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Python pinger')

    # Hostname - positional argument
    parser.add_argument('hostname', type=str)

    # Buffer size
    parser.add_argument('-l', dest='size', type=int, default=defaults.buffer_size,
                       help='Send buffer size.')

    # Timeout (ms)
    parser.add_argument('-w', dest='timeout', type=int, default=defaults.timeout,
                       help='Timeout in milliseconds to wait for each reply.')

    # Continuous flag (default is False)
    parser.add_argument('-t', dest='continuous', action="store_true",
                       help='Ping the specified host until stopped.')

    # Number of pings
    parser.add_argument('-n', dest='count', type=int,
                       help='Number of echo requests to send.')

    # Interval between pings (for Continous is True or Count > 1)
    parser.add_argument('-i', dest='interval', type=int, default=defaults.interval,
                       help='Wait interval seconds between sending each packet.')

    args = parser.parse_args()

    # If multiple pings, user Pinger()
    if args.continuous or args.count:
        sys.exit(Pinger(args.hostname, args.size, args.timeout, args.continuous, args.count, args.interval))

    # Otherwise, just use single ping
    else:
        p = Ping(args.hostname, args.size, args.timeout)
        delay = p.do()
        print p
        print delay
