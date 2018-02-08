import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_ROUTER = "> BBH "
OSPF_LSA_ROUTER_LEN = struct.calcsize(OSPF_LSA_ROUTER)
OSPF_LSA_ROUTER_LINK_DATA = "> I I BBH"
OSPF_LSA_ROUTER_LINK_DATA_LEN = struct.calcsize(OSPF_LSA_ROUTER_LINK_DATA)

class RouterLSA(LSAHeader):
    def __init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg, v, e, b, links, linksData):
        LSAHeader.__init__(self,sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg)
        self.V = v
        self.E = e
        self.B = b
        self.NumberLinks = links
        self.LinksData = linksData

    def printLSA(self):
        print "Router LSA:"
        print "Link ID          ADV Router      Age     Seq#        Link count"
        print self.getLSID(),"      ",self.getADVRouter(),"      ",self.getAge(),\
            "      ", self.getSeqNumber(),"      ", len(self.LinksData)

    def calculateLength(self, ck):

        hdlen = self.getLengthHeader(ck)
        netlen = (OSPF_LSA_ROUTER_LEN + (OSPF_LSA_ROUTER_LINK_DATA_LEN * self.NumberLinks))
        self.setLength(hdlen+netlen, ck)
        return hdlen+netlen

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
    def packRLSA(self):
        #self.printaTudoo()
        first = self.V*4 + self.E*2 + self.B
        pack = struct.pack(OSPF_LSA_ROUTER, first, 0, self.NumberLinks)

        for x in self.LinksData:
            pack = pack + struct.pack(OSPF_LSA_ROUTER_LINK_DATA, utils.IPtoDec(x[0]),
                                      utils.IPtoDec(x[1]), x[2], x[3], x[4])
        return pack

    def getLSAtoSend(self, ):
        pack = self.packRLSA()
        return [self.getHeaderPack(False) + pack, self.getLength()]