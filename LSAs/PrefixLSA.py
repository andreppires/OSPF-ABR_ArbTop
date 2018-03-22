import struct

import utils
from LSAs.HeaderOpaqueLSA import HeaderOpaqueLSA

OSPF_LSA_PREFIX = "> L L L"
OSPF_LSA_PREFIX_LEN = struct.calcsize(OSPF_LSA_PREFIX)


class PrefixLSA(HeaderOpaqueLSA):
    def __init__(self, sourceR, lsage, opt, opaqueID, advert, lsNumber, ck, lg, metric, subnetMask, subnetAddr):
        HeaderOpaqueLSA.__init__(self, sourceR, lsage, opt, 21, opaqueID, advert, lsNumber, ck, lg)

        self.Metric = metric
        self.SubnetMask = subnetMask
        self.SubnetAddress = subnetAddr

    def getSubnetMask(self):
        return self.SubnetMask

    def getSubnetAddress(self):
        return self.SubnetAddress

    def getMetric(self):
        return self.Metric

    def printLSA(self):
        print "##### Prefix-LSA id:", self.OpaqueID, ", ADV Router:", self.getADVRouter()
        print "Prefix", self.SubnetAddress, "\tSubnet Mask:", self.SubnetMask, "\tMetric:", self.Metric

    def calculateLength(self, ck):
        hdlen = self.getLengthHeader(ck)
        netlen = OSPF_LSA_PREFIX_LEN
        self.setLength(hdlen + netlen, ck)
        return hdlen + netlen

    def calculateChecksum(self):
        lg = self.calculateLength(True)

        pack = self.packPrefixLSA()

        structn = self.getHeaderPack() + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return checkum

    def packPrefixLSA(self):
        pack = struct.pack(OSPF_LSA_PREFIX, self.Metric, utils.IPtoDec(self.SubnetMask),
                           utils.IPtoDec(self.SubnetAddress))
        return pack

    def getLSAtoSend(self):
        pack = self.packPrefixLSA()
        return self.getHeaderPack() + pack, self.getLength()
