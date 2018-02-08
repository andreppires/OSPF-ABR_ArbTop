import struct

from OSPFPacket import OSPFPacket
from utils import createchecksum

OSPF_LSUPDATE = ">L"
OSPF_LSUPDATE_LEN = struct.calcsize(OSPF_LSUPDATE)

class LinkStateUpdatePacket(OSPFPacket):


    def __init__(self,sourceRouter, version, type, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2, Nlsas):
        OSPFPacket.__init__(self, version, type, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.sourceRouter = sourceRouter
        self.NLSAs = Nlsas
        self.ReceivedLSAs = []

    def getSourceRouter(self):
        return self.sourceRouter

    def receiveLSA(self, rq):
        self.ReceivedLSAs.append(rq)

    def getReceivedLSAs(self):
        return self.ReceivedLSAs

    def packLSUPD(self):
        pack = struct.pack(OSPF_LSUPDATE, self.NLSAs)
        lg=0
        for x in self.ReceivedLSAs:
            lg += x.getLength()
            pack = pack + x.getLSAtoSend()[0]
        return pack, lg

    def computeChecksum(self):

        ##-- Checksum --##
        ospfheader = self.getHeaderPack()
        packLSR = self.packLSUPD()[0]
        data = ospfheader + packLSR
        OSPF_Checksum = createchecksum(data, self.getPackLength(), 4)
        self.setChecksum(int(OSPF_Checksum, 16))

    def setLength(self, lg):
        self.setPackLength(OSPF_LSUPDATE_LEN + lg)

    def getPackLSUPD(self):
        pack, lg = self.packLSUPD()
        self.setLength(lg)
        self.computeChecksum()
        return self.getHeaderPack() + pack

    def getLSARequests(self):
        return self.LSARequests