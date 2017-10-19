# some imports
import socket, sys
from struct import *
from string import atoi
from binascii import b2a_hex, b2a_qp

import mcast
from utils import getIPAllInterfaces

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
PROTO = 89
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

BUFSIZE = 1024

def receiver(address):
    # create a raw socket
    cast = mcast.dcast()
    mgroup = cast.create(address, PROTO)
    while True:
        data, addr = cast.recv(mgroup)
        mcast.readPack(addr, data)
