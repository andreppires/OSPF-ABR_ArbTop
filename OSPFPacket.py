class OSPFPacket():
    def __init__(self, version, tp, packet_lenght, RouterID, areaID, checksum, AuType, authentication1, authentication2):
        self.version = version
        self.type = tp
        self.packet_length = packet_lenght
        self.RouterID = RouterID
        self.AreaID = areaID
        self.Checksum = checksum
        self.AuType = AuType
        self.Authentication = authentication1
        self.Authentication2 = authentication2