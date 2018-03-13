import struct

import utils
from LSAs.HeaderOpaqueLSA import HeaderOpaqueLSA

OSPF_LSA_ABR = "> L L" #Link Data struct
OSPF_LSA_ABR_LEN = struct.calcsize(OSPF_LSA_ABR)

class ABRLSA(HeaderOpaqueLSA):
    def __init__(self,sourceR, lsage, opt, opaqueID, advert, lsNumber, ck, lg):
        HeaderOpaqueLSA.__init__(self, sourceR, lsage, opt, 20, opaqueID, advert, lsNumber, ck, lg)

        self.LinkData = []  # [IPVizinho, Metrica]


    def getLinkData(self):
        return self.LinkData

    def addLinkDataEntry(self, entry):
        self.LinkData.append(entry)

    def removeLinkDataEntry(self, entry):
        self.LinkData.remove(entry)

    def printLSA(self):
        print "##### ABR-LSA id:", self.OpaqueID
        print "ADV Router:", self.getADVRouter(), "\tNeighbors count:", len(self.LinkData)

    def calculateLength(self, ck):

        hdlen = self.getLengthHeader(ck)
        netlen = (OSPF_LSA_ABR_LEN * len(self.LinkData))
        self.setLength(hdlen+netlen, ck)
        return hdlen+netlen

    def packABRLSA(self):

        pack = ''
        for x in self.LinkData:
            pack = pack + struct.pack(OSPF_LSA_ABR_LEN, utils.IPtoDec(x[0]), (x[1]))
        return pack

    def calculateChecksum(self):
        lg = self.calculateLength(True)

        pack = self.packABRLSA()

        structn = self.getHeaderPack() + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return 0

    def printaTudoo(self):
        print "Links Data:", self.LinkData

    def getLSAtoSend(self, ):
        pack = self.packABRLSA()
        return [self.getHeaderPack() + pack, self.getLength()]

    def getDicOfNeighbors(self):
        out ={}
        for x in self.LinkData:
            out[x[0]] = x[1]
        return out

