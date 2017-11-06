from socket import *
from string import atoi
from struct import pack
from binascii import b2a_hex, b2a_qp

from HelloPacket import HelloPacket
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

DEBUG=False


class mcast(object):
    def __init__(self):
        self.bufsize = BUFSIZE

    def create(self, MCAST_GROUP, PROTO):
        self.mcast_group = MCAST_GROUP
        self.proto = PROTO
        s = socket(AF_INET, SOCK_RAW, self.proto)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((self.mcast_group, self.proto))
        netinterfaces = getIPAllInterfaces().items()
        for x in range(0, len(netinterfaces)):
            if netinterfaces[x][0] == 'lo':
                continue
            else:
                mcast = inet_aton(self.mcast_group) + inet_aton(netinterfaces[x][1])
                s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, str(mcast))
        return s

    def recv(self, s):
        self.s = s
        return self.s.recvfrom(self.bufsize)


def readPack(addr, data):
    pos = 0


    if data:
        if (addr[0]) in str(getIPAllInterfaces()):
            return 0
        if DEBUG:
            print "*** Packet received from %s ***" % (addr[0])
        if b2a_hex(data[pos + 9]) == OSPF_TYPE_IGP:
            if DEBUG:
                print "Protocol OSPF IGP (%d)" % atoi(b2a_hex(data[pos + 9]), 16)
        else:
            if DEBUG:
                print "Error, not an OSPF packet"
                print b2a_hex(data[pos + 9])
            return 0

        pos += 20
        version = (td(data[pos]))
        packet_lenght = (td(data[pos + 2])) + (td(data[pos + 3]))
        # Message Type
        if b2a_hex(data[pos + 1]) == HELLO_PACKET:
            type = 1
            if DEBUG:
                print "Message Type: Hello Packet (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
        elif b2a_hex(data[pos + 1]) == DB_DESCRIPTION:
            type = 2
            if DEBUG:
                print "Message Type: DB Description (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
        elif b2a_hex(data[pos + 1]) == LS_REQUEST:
            type = 3
            if DEBUG:
                print "Message Type: LS Request (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
        elif b2a_hex(data[pos + 1]) == LS_UPDATE:
            type = 4
            if DEBUG:
                print "Message Type: LS Update (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
        elif b2a_hex(data[pos + 1]) == LS_ACKNOWLEDGE:
            type = 5
            if DEBUG:
                print "Message Type: LS Acknowledge (%d)" % atoi(b2a_hex(data[pos + 1]), 16)
        if b2a_hex(data[pos]) == '01' or '02' or '03':
            if DEBUG:
                print "OSPF Version: %d" % atoi(b2a_hex(data[pos]), 16)
        else:
            if DEBUG:
                print "OSPF Version: Unknown"
        areaID = inet_ntoa(data[pos + 8:pos + 12])
        RouterID = inet_ntoa(data[pos + 4:pos + 8])
        checksum = (td(data[pos + 12])) + (td(data[pos + 13]))
        AuType =  (td(data[pos + 14])) + (td(data[pos + 15]))
        authentication1 = td(data[pos + 16:pos + 20])
        authentication2 = td(data[pos + 20:pos + 24])

        if DEBUG:
            print "Area ID: %s" % (areaID)
            print "Source OSPF Router: %s" % (RouterID)
        # Authentication Type
        if b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '00' and DEBUG:
            print "Authentication Type: None"
        elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '01'and DEBUG:
            print "Authentication Type: Plain text"
            print "Authentication Data: %s" % b2a_qp(data[pos + 16:pos + 24])
        elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '02'and DEBUG:
            print "Authentication Type: Message-digest"

        if type == 1:
            # Hello Packet
            networkmask = (inet_ntoa(data[pos + 24:pos + 28]))
            helloint = (td(data[pos + 28]) + td(data[pos + 29]))
            options = (td(data[pos + 30]))
            routpri = (td(data[pos + 31]))
            deadint = (td(data[pos + 32]) + td(data[pos + 33]) +
                       td(data[pos + 34]) + td(data[pos + 35]))
            designRouter = (inet_ntoa(data[pos + 36:pos + 40]))
            backdesignRouter = (inet_ntoa(data[pos + 40:pos + 44]))

            if DEBUG:
                print "Network Mask: %s" % networkmask
                print "Router Priority: %d" % routpri
                print "Hello Interval: %d seconds" % helloint
                print "Dead Interval: %d seconds" % deadint
                print "Designated Router: %s" % designRouter
                print "Backup Designated Router: %s\n" % backdesignRouter

            #TODO retirar os neighbors
            neighbors = []
            NumNeighbors = (packet_lenght- 44)/4    # 44 = lenght OSPF packet without neighbors with LLS Data Block
                                                    # 4  = #bits per neighbor
            for x in range(0,NumNeighbors):
                neighbors.append((inet_ntoa(data[pos + 44 + x*4:pos + 48 + x*4])))


            return HelloPacket(addr[0], version, type, packet_lenght, RouterID, areaID, checksum, AuType,
                               authentication1, authentication2, networkmask, helloint, options, routpri, deadint,
                               designRouter, backdesignRouter, neighbors)

    else:
        if DEBUG:
            print("Error, not an OSPF packet")

    return 0


def td(r):
    for i in r:
        return int(b2a_hex(i), 16)