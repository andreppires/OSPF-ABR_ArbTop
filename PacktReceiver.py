#!/usr/bin/env python
#
#
# OSPF Multicast Sniffer
#
# Add's a listener to multicast group 224.0.0.5 (AllSPFRouters),
# waits for an OSPF hello packet and extract the most important info.
# Won't work on Win32...
#
# Limited support for LS_UPDATE, LS_REQUEST, LS_ACKNOWLEDGE and
# DB_DESCRIPTION specific structure.
#
# ***CODE PROVIDED AS-IS WITHOUT ANY KIND OF WARRANTY***
#
# Sample Output:
# *** Packet received from 192.168.1.231 ***
# Protocol OSPF IGP (89)
# Message Type: Hello Packet (1)
# OSPF Version: 2
# Area ID: 0.0.0.0
# Source OSPF Router: 192.168.168.231
# Authentication Type: Message-digest
# Network Mask: 255.255.255.0
# Router Priority: 1
# Hello Interval: 10 seconds
# Dead Interval: 40 seconds
# Designated Router: 192.168.1.230
# Backup Designated Router: 192.168.1.231
#

from binascii import b2a_hex, b2a_qp
import mcast
from socket import *
from string import atoi

MCAST_GROUP = '224.0.0.5'
PROTO = 89
BUFSIZE = 1024

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

def td(r):
    for i in r:
        return int(b2a_hex(i), 16)

def startReceiver():
    MCAST_GROUP = '224.0.0.5'
    PROTO = 89
    BUFSIZE = 10240

    OSPF_TYPE_IGP = '59'
    HELLO_PACKET = '01'
    DB_DESCRIPTION = '02'
    LS_REQUEST = '03'
    LS_UPDATE = '04'
    LS_ACKNOWLEDGE = '05'

    cast = mcast.mcast()
    mgroup = cast.create(MCAST_GROUP, PROTO)
    while True:
        pos=0
        try:
            data, addr = cast.recv(mgroup)
            if data:
                print "*** Packet received from %s ***" % (addr[0])
                if b2a_hex(data[pos + 9]) == OSPF_TYPE_IGP:
                    print "Protocol OSPF IGP (%d)" % atoi(b2a_hex(data[pos + 9]), 16)
                else:
                    print "Error, not an OSPF packet"
                    print b2a_hex(data[pos + 9])
                    continue

                pos += 20
                # Message Type
                if b2a_hex(data[pos + 1]) == HELLO_PACKET:
                    type = 1
                    print "Message Type: Hello Packet (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
                elif b2a_hex(data[pos + 1]) == DB_DESCRIPTION:
                    type = 2
                    print "Message Type: DB Description (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
                elif b2a_hex(data[pos + 1]) == LS_REQUEST:
                    type = 3
                    print "Message Type: LS Request (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
                elif b2a_hex(data[pos + 1]) == LS_UPDATE:
                    type = 4
                    print "Message Type: LS Update (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
                elif b2a_hex(data[pos + 1]) == LS_ACKNOWLEDGE:
                    type = 5
                    print "Message Type: LS Acknowledge (%d)" % atoi(b2a_hex(data[pos + 1]), 16)

                if b2a_hex(data[pos]) == '01' or '02' or '03':
                    print "OSPF Version: %d" % atoi(b2a_hex(data[pos]), 16)
                else:
                    print "OSPF Version: Unknown"

                print "Area ID: %s" % (inet_ntoa(data[pos + 8:pos + 12]))
                print "Source OSPF Router: %s" % (inet_ntoa(data[pos + 4:pos + 8]))

                # Authentication Type
                if b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '00':
                    print "Authentication Type: None"
                elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '01':
                    print "Authentication Type: Plain text"
                    print "Authentication Data: %s" % b2a_qp(data[pos + 16:pos + 24])
                elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '02':
                    print "Authentication Type: Message-digest"

                if type == 1:
                    # Hello Packet
                    print "Network Mask: %s" % (inet_ntoa(data[pos + 24:pos + 28]))
                    print "Router Priority: %d" % (td(data[pos + 31]))
                    print "Hello Interval: %d seconds" % (td(data[pos + 28]) + td(data[pos + 29]))
                    print "Dead Interval: %d seconds" % (
                        td(data[pos + 32]) + td(data[pos + 33]) + td(data[pos + 34]) + td(data[pos + 35]))
                    print "Designated Router: %s" % (inet_ntoa(data[pos + 36:pos + 40]))
                    print "Backup Designated Router: %s\n" % (inet_ntoa(data[pos + 40:pos + 44]))

            else:
                print( "Error, not an OSPF packet")
        except KeyboardInterrupt:
            print( 'quit')
            exit()
