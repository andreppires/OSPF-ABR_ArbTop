import struct

from OSPFPacket import OSPFPacket
from utils import createchecksum

OSPF_DD_HEADER = ">BBBB L"
OSPF_DD_HEADER_LEN = struct.calcsize(OSPF_DD_HEADER)

class DatabaseDescriptionPacket(OSPFPacket):

    def __init__(self, sourceRouter, version, tp, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2, External, init, more, master, seqNumber, toSend):
        self.sourceRouter = sourceRouter
        self.Options = External
        self.Init = init
        self.More = more
        self.Master = master
        self.DatabaseDescriptionSequenceNumber = seqNumber
        self.ListLSAHeader = []

        OSPFPacket.__init__(self, version, tp, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        if toSend:
            self.setLength()
            self.computeChecksum()

    def getSourceRouter(self):
        return self.sourceRouter

    def getDatabaseDescriptionSequenceNumber(self):
        return self.DatabaseDescriptionSequenceNumber

    def getListLSA(self):
        return self.ListLSAHeader

    def addLSAHeader(self, lsaheader):

        self.ListLSAHeader.append(lsaheader)

    def removeLSAHeader(self, LSType, LSID, LSAdvRouter):
        for x in self.ListLSAHeader:
            if x.getLSType() == LSType and x.getLSID() == LSID and x.getADVRouter() == LSAdvRouter:
                self.ListLSAHeader.remove(x)
                return True
        return False

    def packDD(self):
        IMMS = self.Init*4 + self.More*2 + self.Master*1
        print IMMS, "<-------"
        pack = struct.pack(OSPF_DD_HEADER, 0,0,self.Options, IMMS, int(self.DatabaseDescriptionSequenceNumber))
        for x in self.ListLSAHeader:
            pack = pack + x

        return pack

    def packDDtoSend(self):
        return self.getHeaderPack() + self.packDD()

    def setLength(self):
        self.setPackLength(OSPF_DD_HEADER_LEN + (20*len(self.ListLSAHeader)))

    def computeChecksum(self):
        ##-- Checksum --##
        ospfheader = self.getHeaderPack()
        packDD = self.packDD()
        data = ospfheader + packDD
        OSPF_Checksum = createchecksum(data, len(self.ListLSAHeader), 2)
        self.setChecksum(int(OSPF_Checksum, 16))