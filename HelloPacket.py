
class HelloPacket():


    def __init__(self,sourceRouter, version, type, packet_lenght, RouterID, areaID, checksum, AuType,
                               authentication1, authentication2, networkmask, helloint, options, routpri, routerdeadint,
                               designRouter, backdesignRouter, neighbors):
        self.sourceRouter = sourceRouter
        self.version = version
        self.type = type
        self.packet_length = packet_lenght
        self.RouterID = RouterID
        self.AreaID = areaID
        self.Checksum = checksum
        self.AuType = AuType
        self.Authentication = authentication1
        self.Authentication2 = authentication2
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