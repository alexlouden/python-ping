A pure python ping implementation using raw sockets.

Note that ICMP messages can only be sent from processes running as root
(in Windows, you must run this script as 'Administrator').

Original Version from [Matthew Dixon Cowles](ftp://ftp.visi.com/users/mdc/ping.py)
  
* copyleft 1989-2011 by the python-ping team, see [AUTHORS](https://github.com/alexlouden/python-ping/blob/master/AUTHORS) for more details.
* license: GNU GPL v2, see [LICENSE](https://github.com/alexlouden/python-ping/blob/master/LICENSE) for more details.

Usage
=====

Python-ping is designed to work both via commandline arguments and as a Python module.

Commandline:
------------

**Single ping:**

```bash
>python -m pyping google.com
Pinging google.com with 32 bytes of data: time=61.12ms, ttl=55, icmp_seq=1
61.1217238846
```

**Multiple ping:**

```bash
>python -m pyping google.com -n 4
Pinging google.com with 32 bytes of data: time=62.12ms, ttl=55, icmp_seq=1
Pinging google.com with 32 bytes of data: time=56.59ms, ttl=55, icmp_seq=2
Pinging google.com with 32 bytes of data: time=56.21ms, ttl=55, icmp_seq=3
Pinging google.com with 32 bytes of data: time=56.65ms, ttl=55, icmp_seq=4
Ping statistics for google.com:
        Packets: Sent = 4, Received = 4, Lost = 0 (0.00% loss),
        Approximate round trip times in milli-seconds:
        Minimum = 56.21ms, Maximum = 62.12ms
        Average = 57.89ms, Jitter = 2.45ms
```

**Infinite ping:**

```bash
>python -m pyping google.com -t
Pinging google.com with 32 bytes of data: time=61.72ms, ttl=55, icmp_seq=1
Pinging google.com with 32 bytes of data: time=56.77ms, ttl=55, icmp_seq=2
Pinging google.com with 32 bytes of data: time=56.14ms, ttl=55, icmp_seq=3
(Ctrl+C pressed)
Ping statistics for google.com:
        Packets: Sent = 3, Received = 3, Lost = 0 (0.00% loss),
        Approximate round trip times in milli-seconds:
        Minimum = 56.14ms, Maximum = 61.72ms
        Average = 58.21ms, Jitter = 2.50ms
```

**Help:**

```bash
>python -m pyping --help
usage: __main__.py [-h] [-l SIZE] [-w TIMEOUT] [-t] [-n COUNT] [-i INTERVAL] hostname

Python pinger

positional arguments:
  hostname

optional arguments:
  -h, --help   show this help message and exit
  -l SIZE      Send buffer size.
  -w TIMEOUT   Timeout in milliseconds to wait for each reply.
  -t           Ping the specified host until stopped.
  -n COUNT     Number of echo requests to send.
  -i INTERVAL  Wait interval seconds between sending each packet.
```
  
Package:
--------

**Simple:**

```python
>>> from pyping import Ping
>>> Ping('google.com').do()
60.97527671346604
```

**Multiple, formatted:**

```python
>>> from pyping import Ping
>>> ping = Ping('google.com')
>>> ping.do()
56.08755970538937
>>> ping.do()
55.906975664505865
>>> print ping
Pinging google.com with 32 bytes of data: time=55.91ms, ttl=55, icmp_seq=2
>>> ping.do()
56.48832655602831
>>> print ping
Pinging google.com with 32 bytes of data: time=56.49ms, ttl=55, icmp_seq=3
```

**Pinger:**

```python
>>> from pyping import Pinger
>>> pinger = Pinger('google.com')
Pinging google.com with 32 bytes of data: time=56.38ms, ttl=55, icmp_seq=1
Pinging google.com with 32 bytes of data: time=56.54ms, ttl=55, icmp_seq=2
Pinging google.com with 32 bytes of data: time=56.33ms, ttl=55, icmp_seq=3
Pinging google.com with 32 bytes of data: time=56.37ms, ttl=55, icmp_seq=4
Ping statistics for google.com:
        Packets: Sent = 4, Received = 4, Lost = 0 (0.00% loss),
        Approximate round trip times in milli-seconds:
        Minimum = 56.33ms, Maximum = 56.54ms
        Average = 56.40ms, Jitter = 0.08ms
>>> pinger.delays
[56.37806446679683, 56.53816638583464, 56.334369273541185, 56.367482037179784]
>>> pinger.jitter
0.07882605342640134
>>> pinger.loss 
0
>>> print pinger.statistics()
Ping statistics for google.com:
        Packets: Sent = 4, Received = 4, Lost = 0 (0.00% loss),
        Approximate round trip times in milli-seconds:
        Minimum = 56.33ms, Maximum = 56.54ms
        Average = 56.40ms, Jitter = 0.08ms
```

TODO
====

* Unit testing
* Ensure cross-platform compatibility (Windows 7 checked, OS X and Linux TBA)
* Ensure thread safety
* Ensure py3k compatibility

Contribute
==========

[Fork this repo](http://help.github.com/fork-a-repo/) on [GitHub](https://github.com/alexlouden/python-ping/) and [send pull requests](http://help.github.com/send-pull-requests/). Thank you.

Revision history
================

Dec. 2, 2012
------------

[Cleanup by Alex Louden](https://github.com/alexlouden/python-ping)
* Major refactor -
 * Made into a module (pyping)
 * Seperated code into two files - pinger.py, and ping.py
 * Made private methods start with underscore - i.e. _send and _recieve 
 * Removed IP address validation and lookup (unnecessary, but could be added in again if desired)
* Added jitter
* Added argument parsing using the argparse module (follows Windows ping syntax roughly)

Oct. 17, 2011
-------------

* [Bugfix if host is unknown](https://github.com/jedie/python-ping/pull/6)

Oct. 12, 2011
-------------

Merge sources and create a seperate github repository:
* https://github.com/jedie/python-ping

Add a simple CLI interface.

September 12, 2011 
------------------

Bugfixes + cleanup by Jens Diemer
Tested with Ubuntu + Windows 7

September 6, 2011
-----------------

[Cleanup by Martin Falatic.](http://www.falatic.com/index.php/39/pinging-with-python)
Restored lost comments and docs. Improved functionality: constant time between
pings, internal times consistently use milliseconds. Clarified annotations
(e.g., in the checksum routine). Using unsigned data in IP & ICMP header
pack/unpack unless otherwise necessary. Signal handling. Ping-style output
formatting and stats.

August 3, 2011
--------------
Ported to py3k by Zach Ware. Mostly done by 2to3; also minor changes to
deal with bytes vs. string changes (no more ord() in checksum() because
>source_string< is actually bytes, added .encode() to data in
send_one_ping()).  That's about it.

March 11, 2010
--------------

changes by Samuel Stauffer:
replaced time.clock with default_timer which is set to
time.clock on windows and time.time on other systems.

November 8, 2009
----------------

Fixes by [George Notaras](http://www.g-loaded.eu/2009/10/30/python-ping/),
reported by [Chris Hallman](http://cdhallman.blogspot.com): 

Improved compatibility with GNU/Linux systems.

Changes in this release:

Re-use time.time() instead of time.clock(). The 2007 implementation
worked only under Microsoft Windows. Failed on GNU/Linux.
time.clock() behaves differently under [the two OSes](http://docs.python.org/library/time.html#time.clock).

May 30, 2007
------------

little [rewrite by Jens Diemer](http://www.python-forum.de/post-69122.html#69122):
 * change socket asterisk import to a normal import
 * replace time.time() with time.clock()
 * delete "return None" (or change to "return" only)
 * in checksum() rename "str" to "source_string"

December 4, 2000
----------------

Changed the struct.pack() calls to pack the checksum and ID as
unsigned. My thanks to Jerome Poincheval for the fix.

November 22, 1997
-----------------

Initial hack. Doesn't do much, but rather than try to guess
what features I (or others) will want in the future, I've only
put in what I need now.

December 16, 1997
-----------------
 
For some reason, the checksum bytes are in the wrong order when
this is run under Solaris 2.X for SPARC but it works right under
Linux x86. Since I don't know just what's wrong, I'll swap the
bytes always and then do an htons().

Links
=====

[Sourcecode at GitHub](https://github.com/jedie/python-ping)
[Python Package Index](http://pypi.python.org/pypi/python-ping/)