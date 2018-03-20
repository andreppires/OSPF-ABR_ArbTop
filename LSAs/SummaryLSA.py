import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_SUMMARY = "> L B B H "
OSPF_LSA_SUMMARY_LEN = struct.calcsize(OSPF_LSA_SUMMARY)

class SummaryLSA(LSAHeader):
    def __init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg, netMask, metric):
        LSAHeader.__init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg)
        self.NetworkMask = netMask  # for type 4 this
        self.Metric = metric

    def getMetric(self):
        return self.Metric

    def printLSA(self):
        print "Summary LSA: Type", self.getLSType()
        print "Link ID          ADV Router      Age     Metric"
        print self.getLSID(), "      ", self.getADVRouter(), "      ", self.getAge(), \
            "      ", self.getMetric()

    def calculateLength(self, ck):
        hdlen = self.getLengthHeader(ck)
        self.setLength(hdlen + OSPF_LSA_SUMMARY_LEN, ck)
        return hdlen + OSPF_LSA_SUMMARY_LEN

    def packSLSA(self):
        pack = struct.pack(OSPF_LSA_SUMMARY, utils.IPtoDec(self.NetworkMask), 0, 0, self.Metric)

        return pack

    def calculateChecksum(self):
        lg = self.calculateLength(True)

        pack = self.packSLSA()

        structn = self.getHeaderPack() + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return 0

    def getLSAtoSend(self, ):
        pack = self.packSLSA()
        return [self.getHeaderPack() + pack, self.getLength()]
