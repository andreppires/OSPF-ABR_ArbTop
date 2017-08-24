import threading
from PacktReceiver import startReceiver
from TimeProcessing import TimeStart
from Deliver import deliver
from PacktConst import *
from time import sleep


class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()


def configuration():
    return 0

def timeKeeping():
    TimeStart()


def receivedOSPFpackets():
    startReceiver()

def interfaceStatusChanges():
    return 0


def monitors():
    return 0


def main():
    #Thread(timeKeeping)
    #Thread(configuration)
    #Thread(receivedOSPFpackets)
    #Thread(interfaceStatusChanges)
    #Thread(monitors)

    #To test
    ipHeader = createIPheader('224.0.0.5', '20.20.20.1',1)
    neighbord = ['4.5.6.7','2.2.2.2']
    HelloPack = createHelloPck('255.255.255.0','3.4.5.6' , '6.7.8.9', neighbord)
    OSPFHeader = createOSPFHeader(1, '1.2.3.4', '0.0.0.0', HelloPack[1], HelloPack[0] , len(neighbord))

    packet = ipHeader+OSPFHeader+HelloPack[0]

    deliver(packet, '224.0.0.5')



if __name__ == '__main__':
    main()
