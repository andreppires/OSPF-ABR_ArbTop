import struct

from utils import IPtoDec

OSPF_HDR = "> BBH L L HH L L"
OSPF_HDR_LEN = struct.calcsize(OSPF_HDR)

class OSPFPacket():
    def __init__(self, version, tp, RouterID, areaID, checksum, AuType, authentication1, authentication2):
        self.version = version
        self.type = tp
        self.packet_length = 0
        self.RouterID = RouterID
        self.AreaID = areaID
        self.Checksum = checksum
        self.AuType = AuType
        self.Authentication = authentication1
        self.Authentication2 = authentication2


    def getType(self):
        return self.type

    def getChecksum(self):
        return self.Checksum

    def setChecksum(self, ck):
        self.Checksum = ck

    def getPackLength(self):
        return self.packet_length

    def setPackLength(self, lg):
        self.packet_length = lg + OSPF_HDR_LEN

    def getHeaderPack(self):
        return struct.pack(OSPF_HDR, self.version, self.type, self.packet_length, IPtoDec(self.RouterID), IPtoDec(self.AreaID),
                    self.Checksum, self.AuType, self.Authentication, self.Authentication2)

