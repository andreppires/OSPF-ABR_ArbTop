import struct

import utils
from LSAHeader import LSAHeader

OSPF_LSA_NETWORK = "> L"
OSPF_LSA_NETWORK_LEN = struct.calcsize(OSPF_LSA_NETWORK)


class NetworkLSA(LSAHeader):
    def __init__(self, sourceR, lsage, opt, lstype, lsid, advert, lsNumber, ck,
                 lg, netmasks, listrouters):
        self.NetworkMask = netmasks
        self.attachedRouter = listrouters
        LSAHeader.__init__(self, sourceR,lsage, opt, lstype, lsid, advert, lsNumber, ck, lg)


    def printLSA(self):
        print "Network LSA: Link ID     ADV Router    Age   Seq#      Link count"
        print "            ",self.getLSID(), " ", self.getADVRouter(), "    ", self.getAge(), "    ",\
            self.getSeqNumber(), "    ", len(self.attachedRouter)

    def calculateLength(self, ck):
        hdlen = self.getLengthHeader(ck)
        netlen = (OSPF_LSA_NETWORK_LEN * (len(self.attachedRouter) + 1))
        self.setLength(hdlen+netlen, ck)
        return hdlen+netlen

    def getAttachedRouters(self):
        return self.attachedRouter

    def calculateChecksum(self):
        lg = self.calculateLength(True)

        pack = self.packNLSA()

        structn = self.getHeaderPack() + pack

        checkum = utils.fletcher(structn, 16, lg)
        self.setChecksum(checkum)
        return checkum

    def packNLSA(self):
        pack = struct.pack(OSPF_LSA_NETWORK, utils.IPtoDec(self.NetworkMask))

        for x in self.attachedRouter:
            pack = pack + struct.pack(OSPF_LSA_NETWORK, utils.IPtoDec(x))
        return pack

    def getLSAtoSend(self):
        pack = self.packNLSA()
        return self.getHeaderPack() + pack, self.getLength()

    def getPrefixAndCost(self):
        network = utils.getNetworkfromIPandMask(self.LinkStateID, self.NetworkMask)
        return [10, self.NetworkMask, network] # TODO need to calculate the shortest path cost

    def getDicOfNeighbors(self):
        out = {}
        for x in self.attachedRouter:
            out[x] = 0
        return out

    def getNetworkMask(self):
        return self.NetworkMask
