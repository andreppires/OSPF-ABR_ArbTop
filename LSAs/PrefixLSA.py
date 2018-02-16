import struct

from LSAs import HeaderOpaqueLSA

OSPF_LSA_PREFIX = "> L L L"
OSPF_LSA_PREFIX_LEN = struct.calcsize(OSPF_LSA_PREFIX)


class PrefixLSA(HeaderOpaqueLSA):
    def __init__(self, sourceR, lsage, opt, opaqueID, advert, lsNumber, ck, lg, metric, subnetMask, subnetAddr):
        HeaderOpaqueLSA.__init__(self, sourceR, lsage, opt, 21, opaqueID, advert, lsNumber, ck, lg)

        self.Metric = metric
        self.SubnetMask = subnetMask
        self.SubnetAddress = subnetAddr