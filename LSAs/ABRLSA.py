import struct

from LSAs import HeaderOpaqueLSA

OSPF_LSA_ABR = "> L L" #Link Data struct
OSPF_LSA_ABR_LEN = struct.calcsize(OSPF_LSA_ABR)
class ABRLSA(HeaderOpaqueLSA):
    def __init__(self,sourceR, lsage, opt, opaqueType, opaqueID, advert, lsNumber, ck, lg):
        HeaderOpaqueLSA.__init__(self,sourceR, lsage, opt, opaqueType, opaqueID, advert, lsNumber, ck, lg)

        self.LinkData = []


    def getLinkData(self):
        return self.LinkData

    def addLinkDataEntry(self, entry):
        self.LinkData.append(entry)

    def removeLinkDataEntry(self, entry):
        self.LinkData.remove(entry)
        