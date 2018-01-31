import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_ROUTER = "> BBH "
OSPF_LSA_ROUTER_LEN = struct.calcsize(OSPF_LSA_ROUTER)
OSPF_LSA_ROUTER_LINK_DATA = "> L L BBH"
OSPF_LSA_ROUTER_LINK_DATA_LEN = struct.calcsize(OSPF_LSA_ROUTER_LINK_DATA)

class RouterLSA(LSAHeader):
    def __init__(self,lsage, opt, lstype, lsid, advert, v, e, b, links, linksData):
        LSAHeader.__init__(self, lsage, opt, lstype, lsid, advert)
        self.V = v
        self.E = e
        self.B = b
        self.NumberLinks = links
        self.LinksData = linksData
    def printLSA(self):
        print "Router LSA:"
        print "Link ID          ADV Router      Age     Seq#        Link count"
        print self.getLSID(),"      ",self.getADVRouter(),"      ",self.getAge(),"      ", self.getSeqNumber(),"      ", len(self.LinksData)
        print self.LinksData

    def calculateLength(self, ck):
        hdlen = self.getLengthHeader(ck)
        netlen = (OSPF_LSA_ROUTER_LEN + (OSPF_LSA_ROUTER_LINK_DATA_LEN * self.NumberLinks))
        self.setLength(hdlen+netlen, ck)
        return hdlen+netlen

    def calculateChecksum(self):
        lg = self.calculateLength(True)
        first = self.V*100 + self.E*10 + self.B
        pack = struct.pack(OSPF_LSA_ROUTER, first, 0, self.NumberLinks)

        for x in self.LinksData:
            pack = pack + struct.pack(OSPF_LSA_ROUTER_LINK_DATA, utils.IPtoDec(x[0]), utils.IPtoDec(x[1]),
                                      x[2], x[3], x[4])

        structn = self.getHeaderPack(True) + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return 0
