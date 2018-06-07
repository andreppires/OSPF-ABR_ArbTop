from socket import *
from string import atoi
from binascii import b2a_hex, b2a_qp
import struct

from LSAs.SummaryLSA import SummaryLSA
from utils import getIPAllInterfaces, IPtoDec, append_hex

from OSPFPackets.LinkStateAcknowledgmentPacket import LinkStateAcknowledgmentPacket
from OSPFPackets.DatabaseDescriptionPacket import DatabaseDescriptionPacket
from OSPFPackets.LinkStateRequestPacket import LinkStateRequestPacket
from OSPFPackets.LinkStateUpdatePacket import LinkStateUpdatePacket
from OSPFPackets.HelloPacket import HelloPacket
from LSAs.NetworkLSA import NetworkLSA
from LSAs.RouterLSA import RouterLSA
from LSAs.LSAHeader import LSAHeader
from LSAs.PrefixLSA import PrefixLSA
from LSAs.ASBRLSA import ASBRLSA
from LSAs.ABRLSA import ABRLSA


OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

DEBUG = False


MCAST_GROUP = '224.0.0.5'
BIND_ADDR = '0.0.0.0'
PROTO = 89
BUFSIZE = 1024

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
        packetLdata = '' + struct.pack('!H', 0) + (data[pos + 2]) + (data[pos + 3])
        packet_lenght = IPtoDec(inet_ntoa(packetLdata))
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
        AuType = (td(data[pos + 14])) + (td(data[pos + 15]))
        authentication1 = td(data[pos + 16:pos + 20])
        authentication2 = td(data[pos + 20:pos + 24])

        if DEBUG:
            print "Area ID: %s" % (areaID)
            print "Source OSPF Router: %s" % (RouterID)
        # Authentication Type
        if b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '00' and DEBUG:
            print "Authentication Type: None"
        elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '01' and DEBUG:
            print "Authentication Type: Plain text"
            print "Authentication Data: %s" % b2a_qp(data[pos + 16:pos + 24])
        elif b2a_hex(data[pos + 14]) == '00' and b2a_hex(data[pos + 15]) == '02' and DEBUG:
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

            neighbors = []
            NumNeighbors = (packet_lenght - 44) / 4  # 44 = lenght OSPF packet without neighbors with LLS Data Block
            # 4  = #bits per neighbor
            for x in range(0, NumNeighbors):
                neighbors.append((inet_ntoa(data[pos + 44 + x * 4:pos + 48 + x * 4])))

            return HelloPacket(addr[0], version, type, RouterID, areaID, checksum, AuType,
                               authentication1, authentication2, networkmask, helloint, options, routpri, deadint,
                               designRouter, backdesignRouter, neighbors)

        if type == 2:
            # Database Description Packet
            options = td(data[pos + 26])
            IMMS = td(data[pos + 27])
            I = False
            M = False
            MS = False
            if IMMS >= 4:
                I = True
                IMMS = IMMS - 4
            if IMMS >= 2:
                M = True
                IMMS = IMMS - 2
            if IMMS >= 1:
                MS = True
                IMMS = IMMS - 1
            if DEBUG:
                print "IMMS = ", IMMS, "- tem de ser igual a 0!"

            DDSequenceNumber = IPtoDec(inet_ntoa(data[pos + 28:pos + 32]))

            packet = DatabaseDescriptionPacket(addr[0], type, version, RouterID, areaID, checksum, AuType,
                                               authentication1, authentication2, options, I, M, MS, DDSequenceNumber,
                                               False)
            NLSAHeaders = (packet_lenght - 32) / 20
            newpos = pos + 32
            for x in range(0, NLSAHeaders):
                lsa = data[newpos:newpos + 20]
                packet.addLSAHeader(lsa)
                newpos = newpos + 20

            return packet

        if type == 3:
            # Link State Request
            NRequests = (packet_lenght - 24) / 12
            packet = LinkStateRequestPacket(addr[0], version, type, RouterID, areaID, checksum, AuType,
                                            authentication1, authentication2)
            for x in range(0, NRequests):
                LS1 = str(hex(td(data[pos + 24 + x * 12])))
                LS2 = str(hex(td(data[pos + 25 + x * 12])))
                LS3 = str(hex(td(data[pos + 26 + x * 12])))
                LS4 = str(hex(td(data[pos + 27 + x * 12])))
                LSType = int(LS1 + LS2[2:] + LS3[2:] + LS4[2:], 16)

                LinkStateID = (inet_ntoa(data[pos + 28 + x * 12:pos + 32 + x * 12]))
                AdvertisingRouter = inet_ntoa(data[pos + 32 + x * 12:pos + 36 + x * 12])

                Request = {'LSType': LSType, 'LinkStateID': LinkStateID, 'AdvertisingRouter': AdvertisingRouter}
                packet.receiveRequest(Request)

            return packet

        if type == 4:
            # Link State Update

            NLSAs = IPtoDec(inet_ntoa(data[pos + 24:pos + 28]))

            # create LSUpdate
            packet = LinkStateUpdatePacket(addr[0], version, type, RouterID, areaID, checksum, AuType,
                                           authentication1, authentication2, NLSAs)

            newpos = pos + 28

            for x in range(0, NLSAs):  # Read the LSAs
                aux =''+struct.pack('!H',0)+(data[newpos])+(data[newpos+1])
                LSAge = IPtoDec(inet_ntoa(aux))
                Options = td(data[newpos + 2])
                LSType = td(data[newpos + 3])
                LSID = (inet_ntoa(data[newpos + 4:newpos + 8]))
                AdvertisingRouter = (inet_ntoa(data[newpos + 8:newpos + 12]))
                LSSeqNum = IPtoDec(inet_ntoa(data[newpos + 12:newpos + 16]))
                a = (td(data[newpos + 16]))
                b = (td(data[newpos + 17]))
                LSChecksum = chr(a) + chr(b)
                Length = append_hex((td(data[newpos + 18])), (td(data[newpos + 19])))

                if LSType == 1:  # Router-LSA
                    VEB = td(data[newpos + 20])
                    V = False
                    E = False
                    B = False
                    if VEB >= 4:
                        V = True
                        VEB = VEB - 4
                    if VEB >= 2:
                        E = True
                        VEB = VEB - 2
                    if VEB >= 1:
                        B = True

                    Nlinks = int(str(hex(td(data[newpos + 22]))) + str(hex(td(data[newpos + 23])))[2:], 16)
                    position = newpos + 24
                    ListLinks = []
                    for x in range(0, Nlinks):
                        LinkID = (inet_ntoa(data[position:position + 4]))
                        LinkData = (inet_ntoa(data[position + 4:position + 8]))
                        LinkType = td(data[position + 8])
                        NMetrics = td(data[position + 9])
                        Metric0 = int(str(hex(td(data[position + 10]))) + str(hex(td(data[position + 11])))[2:], 16)
                        ListLinks.append([LinkID, LinkData, LinkType, NMetrics, Metric0])
                        position += 12
                    newRouterLSA = RouterLSA(addr[0], LSAge, Options, LSType, LSID, AdvertisingRouter, LSSeqNum,
                                             LSChecksum, Length, V, E, B, Nlinks, ListLinks)
                    packet.receiveLSA(newRouterLSA)

                if LSType == 2:  # Network-LSA
                    NetMask = (inet_ntoa(data[newpos + 20:newpos + 24]))
                    NAttachedRouters = (Length - 24) / 4
                    ListAtt = []

                    for x in range(0, NAttachedRouters):
                        ListAtt.append((inet_ntoa(data[newpos + 24 + 4 * x:newpos + 28 + 4 * x])))

                    newNetworkLSA = NetworkLSA(addr[0], LSAge, Options, LSType, LSID, AdvertisingRouter, LSSeqNum,
                                               LSChecksum, Length, NetMask, ListAtt)
                    packet.receiveLSA(newNetworkLSA)

                if LSType == 3:  # Summary-LSA (IP Network)
                    packet.receiveLSA(SummaryLSA(addr[0], LSAge, Options, LSType, LSID, AdvertisingRouter, LSSeqNum,
                                                 LSChecksum, Length, '255.255.255.0', 0))

                if LSType == 4:  # Summary-LSA (ASBR)
                    print "Read of ASBR Summary LSA not done"
                    pass

                if LSType == 5:  # External-LSA
                    print "Read of External LSA not done"
                    pass

                if LSType == 11:  # Opaque-LSA - AS flooding

                    opaquetype = td(data[newpos + 4])
                    opaqueid = append_hex(td(data[newpos + 5]), append_hex(td(data[newpos + 6]),
                                                                           td(data[newpos + 7])))
                    if opaquetype == 20:  # ABR-LSA
                        NNeigh = (Length - 18) / 8

                        newlsa = ABRLSA(addr[0], LSAge, Options, opaqueid, AdvertisingRouter, LSSeqNum,
                                        LSChecksum, Length)

                        for x in range(NNeigh):
                            NeighborID = inet_ntoa(data[newpos + 20 + (x * 8):newpos + 24 + (x * 8)])
                            Metric = IPtoDec(inet_ntoa(data[newpos + 24 + (x * 8):newpos + 28 + (x * 8)]))
                            newlsa.addLinkDataEntry([NeighborID, Metric])
                        packet.receiveLSA(newlsa)

                    if opaquetype == 21:  # Prefix-LSA
                        Metric = IPtoDec(inet_ntoa(data[newpos + 20: newpos + 24]))
                        SubnetMask = (inet_ntoa(data[newpos + 24:newpos + 28]))
                        SubnetPrefix = (inet_ntoa(data[newpos + 28:newpos + 32]))

                        newlsa = PrefixLSA(addr[0], LSAge, Options, opaqueid, AdvertisingRouter,
                                           LSSeqNum, LSChecksum, Length, Metric, SubnetMask, SubnetPrefix)
                        packet.receiveLSA(newlsa)

                    if opaquetype == 22:  # ASBR-LSA
                        Metric = IPtoDec(inet_ntoa(data[newpos + 8: newpos + 12]))

                        DestinationRID = (inet_ntoa(data[newpos + 12:newpos + 16]))

                        newlsa = ASBRLSA(addr[0], LSAge, Options, opaqueid, AdvertisingRouter,
                                         LSSeqNum, LSChecksum, Length, Metric, DestinationRID)
                        packet.receiveLSA(newlsa)

                newpos += Length
            return packet

        if type == 5:
            # Link State Acknowledge
            return 0
            NLSAHeaders = (packet_lenght - 24) / 20

            LSACK = LinkStateAcknowledgmentPacket(addr[0], version, type, RouterID, areaID, checksum, AuType,
                                                  authentication1, authentication2)

            newpos = pos + 24
            for x in range(0, NLSAHeaders):
                aux = '' + struct.pack('!H', 0) + (data[newpos]) + (data[newpos + 1])
                LSAge = IPtoDec(inet_ntoa(aux))
                Options = int(hex(td(data[newpos + 2])), 16)
                LSType = int(str(td(data[newpos + 3])), 16)
                LSID = (inet_ntoa(data[newpos + 4:newpos + 8]))
                AdvertisingRouter = (inet_ntoa(data[newpos + 8:newpos + 12]))
                LSSeqNum = IPtoDec(inet_ntoa(data[newpos + 12:newpos + 16]))
                LSChecksum = int(str(hex(td(data[newpos + 16]))) + str(hex(td(data[newpos + 17])))[2:], 16)
                Length = int(str(hex(td(data[newpos + 18]))) + str(hex(td(data[newpos + 19])))[2:], 16)
                newpos += 20
                lsaH = LSAHeader(addr[0], LSAge, Options, LSType, LSID, AdvertisingRouter,
                                 LSSeqNum, LSChecksum, Length)
                LSACK.receceiveNotPackedLSAHEaders(lsaH)

            return LSACK

    else:
        if DEBUG:
            print("Error, not an OSPF packet")

    return 0


def td(r):
    for i in r:
        return int(b2a_hex(i), 16)