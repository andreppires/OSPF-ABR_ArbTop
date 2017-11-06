import time, threading

from Deliver import deliver
from HelloPacket import HelloPacket
from Neighbord import neighbord
from PacktConstruction import createHelloPck, createOSPFHeader


class interface:
    """Interface class"""
    def __init__(self, type, ipint, ipintmask, areaID, helloint, routerDeadInterval, IntTransDelay,
                 routerPriority, rid):
        self.Type = type
        self.State = 1
        self.IPInterfaceAddress = ipint
        self.IPInterfaceMask = ipintmask
        self.AreaID = areaID
        self.RouterID=rid
        self.HelloInterval = helloint
        self.RouterDeadInterval = routerDeadInterval
        self.InfTransDelay = IntTransDelay
        self.RouterPriority = routerPriority

        self.HelloTimer = 0
        self.WaitTimer = routerDeadInterval
        self.Neighbours = []
        self.DesignatedRouter='0.0.0.0'
        self.BackupDesignatedRouter='0.0.0.0'
        self.InterfaceOutputCost=10
        self.RxmtInterval = 30
        self.Autye= None
        self.AuthenticationKey = None


        self.InterfaceStates={0:"Down",
                              1:"Loopback",
                              2:"Waiting",
                              3:"Point-to-point",
                              4:"DR Other",
                              5:"Backup",
                              6:"DR"}

        self.thread = threading.Thread(target=self.statelife)
        self.thread.daemon = True
        self.thread.start()




    def decreaseHelloTimer(self):
        self.HelloTimer=self.HelloTimer -1

    def resetHelloTimer(self):
        self.HelloTimer=self.HelloInterval

    def decreaseWaitTimer(self):
        self.WaitTimer=self.WaitTimer - 1

    def resetWaitTimer(self):
        self.WaitTimer=self.RouterDeadInterval

    def getNeihbordIDs(self):
        out=[]
        for x in self.Neighbours:
            out.append(x.getNeighbordID())
        return out

    def sendHello(self):
        neighbords=self.getNeihbordIDs()
        HelloPack = createHelloPck(self.IPInterfaceMask, self.DesignatedRouter, self.BackupDesignatedRouter,neighbords
                                   , self.RouterPriority, self.HelloInterval,
                                   self.RouterDeadInterval)
        OSPFHeader = createOSPFHeader(1, self.RouterID, self.AreaID, HelloPack[1], HelloPack[0], len(neighbords))
        packet = OSPFHeader + HelloPack[0]
        deliver(packet, self.IPInterfaceAddress)
        print "Hello enviado: interface"+ self.IPInterfaceAddress

    def statelife(self):
        self.State=2 #WaitTimer
        time.sleep(self.WaitTimer)
        while self.State != 0 and self.State !=1:
            if self.HelloTimer == 0:
                self.sendHello()
                self.HelloTimer=self.HelloInterval
            time.sleep(1)
            self.decreaseHelloTimer()

    def packetReceived(self, packet):
        if packet.getType() == 1:
            self.readHello(packet)
        else:
            print "nao sei o tipo de pacote"
            pass


    def readHello(self,packet):

        if self.RouterID in packet.getNNeighbors():
            # estou listado no Hello do vizinho
            for x in self.Neighbours:
                if x.getNeighbordID() == packet.RouterID:
                    #   ja era vizinho
                    x.updateFromHello(packet)
                    return 1    # sucess
            #   ainda nao o tinha como vizinho
            self.Neighbours.append(neighbord(packet.RouterDeadInterval, packet.RouterID, packet.RouterPri,
                                              packet.sourceRouter, packet.Options, packet.DesignatedRouter,
                                              packet.BackupDesignatedRouter))
            return 1    # sucess
        else:
            # ainda nao sou vizinho
            pass


    ### Events causing interface state changes 9.2
    def InterfaceUp(self):
        self.State = 2  # Waiting

    def WaitTimer(self):
        if self.DesignatedRouter == '0.0.0.0':
            self.State = 6  # Designated Router
        else:
            if self.BackupDesignatedRouter == '0.0.0.0':
                self.State = 5  # Backup Designated Router
            else:
                self.State = 4  # DR Other

    def BackupSeen(self, dr, ID):
        if dr == 0:  # alguem ja e BDR:
            self.State = 4  # DR Other
            self.BackupDesignatedRouter = ID
        elif dr == 1:   # alguem ja e DR e nao ha BDR
            self.State = 5  # Backup Designated Router
            self.DesignatedRouter = ID
            self.BackupDesignatedRouter = self.RouterID

    def NeighborChange(self):
        self.DesignatedRouter = '0.0.0.0'
        self.BackupDesignatedRouter = '0.0.0.0'
        self.State = 2  # Waiting


    def LoopIn(self):
        self.State = 1  # Loopback

    def UnloopInd(self):
        self.State = 0  # Down

    def InterfaceDown(self):
        self.State = 0  # Down
        # reset as interfaces
        self.DesignatedRouter = '0.0.0.0'
        self.BackupDesignatedRouter = '0.0.0.0'
        self.InterfaceOutputCost = 10
        self.RxmtInterval = 30

    def DRElection(self):



        pass







