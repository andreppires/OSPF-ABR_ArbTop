import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_EXTERNAL = "> L BBH L L"
OSPF_LSA_EXTERNAL_LEN = struct.calcsize(OSPF_LSA_EXTERNAL)

class ASExternalLSA(LSAHeader):
    def __init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg, netMask, ebit, metric,
                 forwardingaddress, externalRouterTag):
        LSAHeader.__init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg)
        self.NetworkMask = netMask  # for type 4 this
        self.Ebit = ebit    #E bit is the first one of the byte
        self.metric = metric
        self.ForwardingAddress = forwardingaddress
        self.ExternalRouteTag = externalRouterTag