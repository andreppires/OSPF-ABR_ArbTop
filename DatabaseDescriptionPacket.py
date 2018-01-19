import struct

from OSPFPacket import OSPFPacket

OSPF_DD_HEADER = ">BBBB L"
OSPF_DD_HEADER_LEN = struct.calcsize(OSPF_DD_HEADER)

class DatabaeDescriptionPacket(OSPFPacket):

    def __init__(self, sourceRouter, version, packet_lenght, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2, External, init, more, master, seqNumber):
        self.sourceRouter = sourceRouter
        OSPFPacket.__init__(self, version, 2, packet_lenght, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.Options = External *10
        self.Init = init
        self.More = more
        self.Master = master
        self.DatabaseDescriptionSequenceNumber = seqNumber
        self.ListLSAHeader = []

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
        IMMS = self.Init*100 + self.More*10 + self.Master
        struct.pack(OSPF_DD_HEADER, 0,0,self.Options, IMMS, self.DatabaseDescriptionSequenceNumber)