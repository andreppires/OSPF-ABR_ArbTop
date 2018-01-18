from OSPFPacket import OSPFPacket

class HelloPacket(OSPFPacket):


    def __init__(self,sourceRouter, version, type, packet_lenght, RouterID, areaID, checksum, AuType,
                               authentication1, authentication2, networkmask, helloint, options, routpri, routerdeadint,
                               designRouter, backdesignRouter, neighbors):
        self.sourceRouter = sourceRouter
        OSPFPacket.__init__(self, version, type, packet_lenght, RouterID, areaID, checksum, AuType, authentication1,
                            authentication2)
        self.NetworkMask = networkmask
        self.HelloInterval = helloint
        self.Options = options
        self.RouterPri = routpri
        self.RouterDeadInterval = routerdeadint
        self.DesignatedRouter = designRouter
        self.BackupDesignatedRouter = backdesignRouter
        self.Neighbors = neighbors

    def getNRouterID(self):
        return self.RouterID

    def getNNeighbors(self):
        return self.Neighbors

    def getType(self):
        return self.type