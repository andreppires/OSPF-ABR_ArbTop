import struct

from OSPFPacket import OSPFPacket
from utils import createchecksum
from utils import IPtoDec

OSPF_HELLO = "> L HBB L L L"
OSPF_HELLO_LEN = struct.calcsize(OSPF_HELLO)
OSPF_HELLO_NEI = ">L"
OSPF_HELLO_NEI_LEN = struct.calcsize(OSPF_HELLO_NEI)

class HelloPacket(OSPFPacket):


    def __init__(self,sourceRouter, version, type, RouterID, areaID, checksum, AuType,
                 authentication1, authentication2, networkmask, helloint, options, routpri, routerdeadint,
                 designRouter, backdesignRouter, neighbors):
        self.sourceRouter = sourceRouter
        self.NetworkMask = networkmask
        self.HelloInterval = helloint
        self.Options = options
        self.RouterPri = routpri
        self.RouterDeadInterval = routerdeadint
        self.DesignatedRouter = designRouter
        self.BackupDesignatedRouter = backdesignRouter
        self.Neighbors = neighbors

        OSPFPacket.__init__(self, version, type, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.setPackLength(OSPF_HELLO_LEN+(len(self.Neighbors)*OSPF_HELLO_NEI_LEN))
        self.computeChecksum()

    def getNRouterID(self):
        return self.RouterID

    def getNNeighbors(self):
        return self.Neighbors

    def getHelloPack(self):
        hello = struct.pack(OSPF_HELLO, IPtoDec(self.NetworkMask), int(self.HelloInterval), self.Options, self.RouterPri,
                            self.RouterDeadInterval, IPtoDec(self.DesignatedRouter),
                            IPtoDec(self.BackupDesignatedRouter))
        for x in self.Neighbors:
            if x.find(".") == -1:  # caso o argumento nao contenha um ponto - nao e um ip
                continue
            else:
                hello = hello + struct.pack(OSPF_HELLO_NEI, (IPtoDec(x)))

        return hello

    def computeChecksum(self):
        ##-- Checksum --##
        ospfheader = self.getHeaderPack()
        packHello = self.getHelloPack()
        data = ospfheader + packHello
        OSPF_Checksum = createchecksum(data, len(self.Neighbors), 1)
        self.setChecksum(int(OSPF_Checksum, 16))

        pass

    def getHelloPackettoSend(self):
        return self.getHeaderPack() + self.getHelloPack()