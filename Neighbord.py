import threading
import time


class neighbord():
    """Neighbord class"""
    def __init__(self, interface, rDeadInt, NeighbordID, nprio, addr, options, DR, BDR):
        self.interface = interface
        self.state = 0
        self.RouterDeadInterval = rDeadInt
        self.inativatyTimer = rDeadInt
        self.masterSlave = 0
        self.ddSequenceNumber = 0
        self.neighbordID = NeighbordID
        self.neighbordPriority = nprio
        self.neighbordAddress = addr
        self.neighbordOptions = options
        self.neighbordDR = DR
        self.neighbordBDR = BDR


        self.NeighbordStates = {0: "Down",
                                1: "Attempt",
                                2: "Init",
                                3: "2-Way",
                                4: "ExStart",
                                5: "Exchange",
                                5: "Loading",
                                6: "Full"}

        self.thread = threading.Thread(target=self.stateLife, args=())
        self.thread.daemon = True
        self.thread.start()

    def stateLife(self):
        self.state = 3
        while self.state != 0:

            self.decreaseInativatyTimer()

            if(self.inativatyTimer  == 0):
                self.DestroyMe()
                self.state = 0
            time.sleep(1)

    def getNeighbordID(self):
        if self.state !=1:
            return self.neighbordID

    def DestroyMe(self):
        self.interface.RemoveNeighbord(self.neighbordID)


    def decreaseInativatyTimer(self):
        self.inativatyTimer = self.inativatyTimer - 1

    def resetInativatyTimer(self):
        self.inativatyTimer = self.RouterDeadInterval

    def updateFromHello(self, packet):
        # TODO verificar verificar se os valores de netmask e hellointerval e RdeadInterval com os valores padrao da int
        # TODO validar o IP header e o header OSPF
        # TODO check the E bit for inter router or border router

        self.resetInativatyTimer()
        self.neighbordID = packet.RouterID

        if self.neighbordPriority != packet.RouterPri:
            self.neighbordPriority = packet.RouterPri
            self.interface.NeighborChange()

        if (packet.DesignatedRouter==packet.sourceRouter and packet.BackupDesignatedRouter=='0.0.0.0'
            and self.interface.getstate()==2):
            self.interface.BackupSeen(1,packet.DesignatedRouter, packet.BackupDesignatedRouter)

        if ((packet.DesignatedRouter==packet.sourceRouter and packet.DesignatedRouter != self.neighbordDR) or
            (packet.sourceRouter == self.neighbordDR and packet.sourceRouter != packet.DesignatedRouter)):
            self.interface.NeighborChange()

        if ((packet.BackupDesignatedRouter==packet.BackupDesignatedRouter and self.interface.getstate==2)):
            self.interface.BackupSeen(0, packet.DesignatedRouter, packet.BackupDesignatedRouter)

        if ((packet.BackupDesignatedRouter==packet.sourceRouter and packet.BackupDesignatedRouter != self.neighbordBDR)
            or (packet.sourceRouter == self.neighbordBDR and packet.sourceRouter != packet.BackupDesignatedRouter)):
            self.interface.NeighborChange()

        self.neighbordDR = packet.DesignatedRouter
        self.neighbordBDR = packet.BackupDesignatedRouter




        pass

    def StateDR(self):
        if self.neighbordAddress == self.neighbordDR:
            return True
        else:
            return False

    def StateBDR(self):
        if self.neighbordAddress == self.neighbordBDR:
            return True
        else:
            return False
