from socket import *
from struct import pack
from binascii import b2a_hex

from utils import getIPAllInterfaces

MCAST_GROUP = '224.0.0.5'
BIND_ADDR = '0.0.0.0'
PROTO = 89
BUFSIZE = 1024

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

class mcast(object):
    def __init__(self):
        self.bufsize = BUFSIZE

    def create(self, MCAST_GROUP, PROTO):
        self.mcast_group = MCAST_GROUP
        self.proto = PROTO
        s = socket(AF_INET, SOCK_RAW, self.proto)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((self.mcast_group, self.proto))
        netinterfaces=getIPAllInterfaces().items()
        for x in range(0, len(netinterfaces)):
            if netinterfaces[x][0]=='lo':
                continue
            else:
                mcast = inet_aton(self.mcast_group)+inet_aton(netinterfaces[x][1])
                s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, str(mcast))
        return s
    def recv(self, s):
        self.s = s
        return self.s.recvfrom(self.bufsize)
