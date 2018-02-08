import struct

from OSPFPacket import OSPFPacket
from utils import createchecksum


class LinkStateAcknowledgmentPacket(OSPFPacket):


    def __init__(self,sourceRouter, version, type, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2):
        OSPFPacket.__init__(self, version, type, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.sourceRouter = sourceRouter
        self.LSAHeaders = []
        self.lengtLSAs=0
        self.NotPackedLSAHeaders = []

    def receceiveNotPackedLSAHEaders(self, lsaH):
        self.NotPackedLSAHeaders.append(lsaH)

    def getNotPackedLSAHeaders(self):
        return self.NotPackedLSAHeaders

    def computeChecksum(self):

        ##-- Checksum --##
        ospfheader = self.getHeaderPack()
        packLSR = self.packLSACK()
        data = ospfheader + packLSR
        OSPF_Checksum = createchecksum(data, self.lengtLSAs, 5)
        self.setChecksum(int(OSPF_Checksum, 16))

    def packLSACK(self):
        pack =''
        for x in self.LSAHeaders:
            pack += x
        return pack

    def setLength(self, lg):
        self.lengtLSAs +=lg
        self.setPackLength(self.lengtLSAs)

    def getLSACKToSend(self):
        self.computeChecksum()
        return self.getHeaderPack() + self.packLSACK()

    def receiveLSA(self, packedlsa, lg):
        self.LSAHeaders.append(packedlsa)
        self.setLength(lg)