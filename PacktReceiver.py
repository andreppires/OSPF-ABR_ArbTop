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

from utils import getIPAllInterfaces

MCAST_GROUP = '224.0.0.5'
PROTO = 89
BUFSIZE = 1024

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

def startReceiver():
    MCAST_GROUP = '224.0.0.5'
    PROTO = 89

    cast = mcast.mcast()
    mgroup = cast.create(MCAST_GROUP, PROTO)
    while True:
        data, addr = cast.recv(mgroup)
        mcast.readPack(addr, data)
