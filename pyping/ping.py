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

import array
import os
import select
import signal
import socket
import struct
import sys
import time
import threading

# ICMP parameters
ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
ICMP_ECHO = 8 # Echo request (per RFC792)
ICMP_MAX_RECV = 2048 # Max size of incoming buffer

class defaults(object):
    buffer_size = 32
    timeout = 1000      # In ms
    interval = 1        # In s
    pinger_count = 4

    if os.name == 'nt':
        # On Windows, the best timer is time.clock()
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

class Ping(object):
    """Ping a hostname"""
    def __init__(self, hostname,
            buffer_size = defaults.buffer_size,
            timeout = defaults.timeout):

        self.destination = hostname
        self.packet_size = buffer_size
        self.timeout = timeout

        self.delay = None
        self.ttl = None
        
        self.seq_number = 0
        self.sent = 0
        self.received = 0

    def do(self):
        """
        Send one ICMP ECHO_REQUEST and receive the response until self.timeout
        """
        # Ping ID is Process ID XOR Thread ID masked to 16 bits
        self.id = (os.getpid() ^ id(threading.currentThread())) & 0xFFFF

        # Increment sequence number
        self.seq_number += 1

        try: # One could use UDP here, but it's obscure
            current_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        except socket.error as e:
            if e.errno == socket.EPERM:
                # Operation not permitted - Add more information to traceback
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    "{} - Note that ICMP messages can only be send from processes running as root.".format(evalue)
                )
                raise etype, evalue, etb
            raise # raise the original error

        send_time = self._send(current_socket)
        if send_time == None:
            return

        receive_time, packet_size, ip, ip_header, icmp_header = self._receive(current_socket)
        current_socket.close()

        self.sent += 1

        if receive_time:
            self.delay = (receive_time - send_time) * 1000.0
            self.ttl = ip_header["ttl"]
            self.received += 1

            return self.delay

    def _send(self, current_socket):
        """
        Send one ICMP ECHO_REQUEST
        """
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        checksum = 0

        # Make a dummy header with a 0 checksum.
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, checksum, self.id, self.seq_number
        )

        padBytes = []
        startVal = 0x42
        for i in range(startVal, startVal + (self.packet_size)):
            padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
        data = bytes(padBytes)

        # Calculate the checksum on the data and the dummy header.
        checksum = self._calculate_checksum(header + data) # Checksum is in network order

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, checksum, self.id, self.seq_number
        )

        packet = header + data

        send_time = defaults.timer()

        try:
            current_socket.sendto(packet, (self.destination, 1)) # Port number is irrelevant for ICMP
        except socket.error as e:
            print("General failure {!r}".format(e.args[1]))
            current_socket.close()
            return

        return send_time

    def _receive(self, current_socket):
        """
        Receive the ping from the socket. timeout = in ms
        """
        timeout = self.timeout / 1000.0

        while True: # Loop while waiting for packet or timeout
            select_start = defaults.timer()
            inputready, outputready, exceptready = select.select([current_socket], [], [], timeout)
            select_duration = (defaults.timer() - select_start)
            if len(inputready) is 0: # timeout
                return None, 0, 0, 0, 0

            receive_time = defaults.timer()

            packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)

            icmp_header = self._header2dict(
                names=[
                    "type", "code", "checksum",
                    "packet_id", "seq_number"
                ],
                struct_format="!BBHHH",
                data=packet_data[20:28]
            )

            if icmp_header["packet_id"] == self.id: # Our packet
                ip_header = self._header2dict(
                    names=[
                        "version", "type", "length",
                        "id", "flags", "ttl", "protocol",
                        "checksum", "src_ip", "dest_ip"
                    ],
                    struct_format="!BBHHHBBHII",
                    data=packet_data[:20]
                )
                packet_size = len(packet_data) - 28
                ip = socket.inet_ntoa(struct.pack("!I", ip_header["src_ip"]))
                # XXX: Why not ip = address[0] ???
                return receive_time, packet_size, ip, ip_header, icmp_header

            timeout = timeout - select_duration
            if timeout <= 0:
                return None, 0, 0, 0, 0


    def _calculate_checksum(self, source_string):
        """
        A port of the functionality of in_cksum() from ping.c
        Ideally this would act on the string as a series of 16-bit ints (host
        packed), but this works.
        Network data is big-endian, hosts are typically little-endian
        """
        if len(source_string)%2:
            source_string += "\x00"
        converted = array.array("H", source_string)
        if sys.byteorder == "big":
            converted.byteswap()
        val = sum(converted)

        val &= 0xffffffff # Truncate val to 32 bits (a variance from ping.c, which
                          # uses signed ints, but overflow is unlikely in ping)

        val = (val >> 16) + (val & 0xffff)    # Add high 16 bits to low 16 bits
        val += (val >> 16)                    # Add carry from above (if any)
        answer = ~val & 0xffff                # Invert and truncate to 16 bits
        answer = socket.htons(answer)

        return answer

    def _header2dict(self, names, struct_format, data):
        """ unpack the raw received IP and ICMP header informations to a dict """
        unpacked_data = struct.unpack(struct_format, data)
        return dict(zip(names, unpacked_data))

    def __str__(self):
        return "Pinging {} with {} bytes of data: time={:.2f}ms, ttl={}, icmp_seq={}".format(
            self.destination, self.packet_size, self.delay, self.ttl, self.seq_number)
