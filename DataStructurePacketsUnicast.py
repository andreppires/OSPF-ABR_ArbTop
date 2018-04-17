import threading


class DataStructurePacketsUnicast():
    def __init__(self):
        self.packets = []
        self.lock = threading.Lock()

    def receivePacket(self, packet):
        self.lock.acquire()
        try:
            self.packets.append(packet)
        finally:
            self.lock.release()

    def returnpacket(self):
        self.lock.acquire()
        try:
            if len(self.packets) > 0:
                toReturn = self.packets.pop(0)
                return toReturn
            else:
                return False

        finally:
            self.lock.release()
