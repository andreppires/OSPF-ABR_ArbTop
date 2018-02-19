import struct

from LSAs.HeaderOpaqueLSA import HeaderOpaqueLSA

OSPF_LSA_ASBR = "> L L"
OSPF_LSA_ASBR_LEN = struct.calcsize(OSPF_LSA_ASBR)


class ASBRLSA(HeaderOpaqueLSA):
    def __init__(self, sourceR, lsage, opt, opaqueID, advert, lsNumber, ck, lg, metric, destiRouterID):
        HeaderOpaqueLSA.__init__(self, sourceR, lsage, opt, 22, opaqueID, advert, lsNumber, ck, lg)

        self.Metric = metric
        self.DestinationRouterID = destiRouterID