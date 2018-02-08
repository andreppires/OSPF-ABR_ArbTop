import struct

from OSPFPacket import OSPFPacket
from utils import createchecksum, IPtoDec

OSPF_LSREQUEST = ">LLL"
OSPF_LSREQUEST_LEN = struct.calcsize(OSPF_LSREQUEST)

class LinkStateRequestPacket(OSPFPacket):


    def __init__(self,sourceRouter, version, type, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2):
        OSPFPacket.__init__(self, version, type, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.sourceRouter = sourceRouter
        self.LSARequests = []

        self.setPackLength(OSPF_LSREQUEST_LEN *len(self.LSARequests))


    def getSourceRouter(self):
        return self.sourceRouter

    def receiveRequest(self, rq):
        self.LSARequests.append(rq)

    def packLSR(self):
        pack = ''
        for x in self.LSARequests:
            pack =pack + struct.pack(OSPF_LSREQUEST, x['LSType'], IPtoDec(x['LinkStateID']), IPtoDec(x['AdvertisingRouter']))
        return pack

    def computeChecksum(self):

        ##-- Checksum --##
        ospfheader = self.getHeaderPack()
        packLSR = self.packLSR()
        data = ospfheader + packLSR
        OSPF_Checksum = createchecksum(data, len(self.LSARequests), 3)
        self.setChecksum(int(OSPF_Checksum, 16))

    def setLength(self):
        self.setPackLength(OSPF_LSREQUEST_LEN*len(self.LSARequests))

    def getLSReqToSend(self):
        self.setLength()
        self.computeChecksum()
        return self.getHeaderPack() + self.packLSR()

    def getLSARequests(self):
        return self.LSARequests