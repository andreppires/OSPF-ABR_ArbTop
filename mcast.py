from socket import *
from string import atoi
from struct import pack
from binascii import b2a_hex, b2a_qp

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

class dcast(object):
    def __init__(self):
        self.bufsize = BUFSIZE

    def create(self, address, PROTO):
        self.proto = PROTO
        s = socket(AF_INET, SOCK_RAW, self.proto)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((address, self.proto))
        return s
    def recv(self, s):
        self.s = s
        return self.s.recvfrom(self.bufsize)

def readPack(addr,data):
    pos = 0

    if data:
        if (addr[0]) in str(getIPAllInterfaces()):
            return 0
        print "*** Packet received from %s ***" % (addr[0])
        if b2a_hex(data[pos + 9]) == OSPF_TYPE_IGP:
            print "Protocol OSPF IGP (%d)" % atoi(b2a_hex(data[pos + 9]), 16)
        else:
            print "Error, not an OSPF packet"
            print b2a_hex(data[pos + 9])
            return 0

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
            networkmask = (inet_ntoa(data[pos + 24:pos + 28]))
            print "Network Mask: %s" % networkmask
            routpri = (td(data[pos + 31]))
            print "Router Priority: %d" % routpri
            helloint = (td(data[pos + 28]) + td(data[pos + 29]))
            print "Hello Interval: %d seconds" % helloint
            deadint = (td(data[pos + 32]) + td(data[pos + 33]) +
                       td(data[pos + 34]) + td(data[pos + 35]))
            print "Dead Interval: %d seconds" % deadint
            designRouter = (inet_ntoa(data[pos + 36:pos + 40]))
            print "Designated Router: %s" % designRouter
            backdesignRouter = (inet_ntoa(data[pos + 40:pos + 44]))
            print "Backup Designated Router: %s\n" % backdesignRouter

    else:
        print( "Error, not an OSPF packet")


def td(r):
    for i in r:
        return int(b2a_hex(i), 16)