import time, threading

from Deliver import deliver
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
                              5:"DR"}

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
        time.sleep(self.WaitTimer)
        while self.State != 0:
            if self.HelloTimer == 0:
                self.sendHello()
                self.HelloTimer=self.HelloInterval
            time.sleep(1)
            self.decreaseHelloTimer()
            #self.decreaseWaitTimer()



