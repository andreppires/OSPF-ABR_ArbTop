import threading
import time


class neighbord():
    def __init__(self, rDeadInt, NeighbordID, nprio, addr, options, DR,BDR):
        self.state = 0
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

        self.thread = threading.Thread(self.stateLife())
        self.thread.daemon = True
        self.thread.start()

    def stateLife(self):
        self.state = 1
        while self.state != 0:
            self.inativatyTimer = self.inativatyTimer - 1
            if(self.inativatyTimer  == 0):
                self.state = 0
            time.sleep(1)

    def getNeighbordID(self):
        return self.neighbordID
