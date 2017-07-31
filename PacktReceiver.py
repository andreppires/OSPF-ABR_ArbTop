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

MCAST_GROUP = '224.0.0.5'
PROTO = 89
BUFSIZE = 10240

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'


def startReceiver():
    MCAST_GROUP = '224.0.0.5'
    PROTO = 89

    OSPF_TYPE_IGP = '59'
    HELLO_PACKET = '01'
    DB_DESCRIPTION = '02'
    LS_REQUEST = '03'
    LS_UPDATE = '04'
    LS_ACKNOWLEDGE = '05'

    print("received packets")
    cast = mcast.mcast()
    mgroup = cast.create(MCAST_GROUP, PROTO)
    pos = 0
    while True:
        print('estou aqui!')
        try:
            data, addr = cast.recv(mgroup)
            if data:
                print("*** Packet received from %s ***" % (addr[0]))
                if b2a_hex(data[pos + 9]) == OSPF_TYPE_IGP:
                    print( "Protocol OSPF IGP (%d)" % int(b2a_hex(data[pos + 9]), 16))
                    pos += 20
                    # Message Type
                    if b2a_hex(data[pos + 1]) == HELLO_PACKET:
                        type = 1
                        print( "Message Type: Hello Packet (%d)" % int(b2a_hex(data[pos + 1]), 16))
                    elif b2a_hex(data[pos + 1]) == DB_DESCRIPTION:
                        type = 2
                        print( "Message Type: DB Description (%d)" % int(b2a_hex(data[pos + 1]), 16))
                    elif b2a_hex(data[pos + 1]) == LS_REQUEST:
                        type = 3
                        print( "Message Type: LS Request (%d)" % int(b2a_hex(data[pos + 1]), 16))
                    elif b2a_hex(data[pos + 1]) == LS_UPDATE:
                        type = 4
                        print( "Message Type: LS Update (%d)" % int(b2a_hex(data[pos + 1]), 16))
                    elif b2a_hex(data[pos + 1]) == LS_ACKNOWLEDGE:
                        type = 5
                        print( "Message Type: LS Acknowledge (%d)" % int(b2a_hex(data[pos + 1]), 16))

                    if b2a_hex(data[pos]) == '01' or '02' or '03':
                        print( "OSPF Version: %d" % int(b2a_hex(data[pos]), 16))
                    else:
                        print( "OSPF Version: Unknown")
            else:
                print( "Error, not an OSPF packet")
        except KeyboardInterrupt:
            print( 'quit')
            exit()
