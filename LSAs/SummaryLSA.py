import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_SUMMARY = "> L B BH "
OSPF_LSA_SUMMARY_LEN = struct.calcsize(OSPF_LSA_SUMMARY)

class SummaryLSA(LSAHeader):
    def __init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg, netMask, metric):
        LSAHeader.__init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg)
        self.NetworkMask = netMask  # for type 4 this
        self.Metric = metric

    def printLSA(self):
        print "Summary LSA: Type", self.getLSType()
        print "Link ID          ADV Router      Age     Seq#"
        print self.getLSID(), "      ", self.getADVRouter(), "      ", self.getAge(), \
            "      ", self.getSeqNumber()

    def calculateLength(self, ck):
        hdlen = self.getLengthHeader(ck)
        self.setLength(hdlen + OSPF_LSA_SUMMARY_LEN, ck)
        return hdlen + OSPF_LSA_SUMMARY_LEN

    def packRLSA(self):
        # self.printaTudoo()
        pack = struct.pack(OSPF_LSA_SUMMARY, self.NetworkMask, 0, self.Metric)

        return pack

    def calculateChecksum(self):
        lg = self.calculateLength(True)

        pack = self.packRLSA()

        structn = self.getHeaderPack(True) + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return 0

    def printaTudoo(self):
        self.printaTudo()
        print "EVB:", self.E, self.V, self.B
        print "Number Links:", self.NumberLinks
        print "Links Data:", self.LinksData

    def getLSAtoSend(self, ):
        pack = self.packRLSA()
        return [self.getHeaderPack(False) + pack, self.getLength()]
