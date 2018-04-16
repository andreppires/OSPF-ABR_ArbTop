import threading

class DataStructurePacketsUnicast():
    def __init__(self):
        self.packets =[]
        self.lock = threading.Lock()

    def receivePacket(self, packet):
        self.lock.acquire()
        try:
            self.packets.append(packet)
        finally:
            self.lock.release()

    def returnpacket(self):
        if len(self.packets) >0:
            self.lock.acquire()
            try:
                toReturn = self.packets.pop(0)
            finally:
                self.lock.release()
            return toReturn
        else:
            return False
