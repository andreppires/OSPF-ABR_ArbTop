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

def timeKeeping(hell,rpi,rdi,rid,aid):
    TimeStart(hell,rpi,rdi,rid, aid)


def receivedOSPFpackets():
    startReceiver()

def interfaceStatusChanges():
    return 0


def monitors():
    return 0


def main():

    ### Read configuration files ###
    f = open('./configs/routerID', 'r')             #routerID
    routerID=f.readline()
    f.close()

    f = open('./configs/Area0/AreaID', 'r')         #AreaID
    AreaID = f.readline()
    f.close()

    f = open('./configs/HelloInterval', 'r')        #Hello Interval
    hellointerval = int(f.readline())
    f.close()

    f = open('./configs/RouterDeadInterval', 'r')   #Router dead Interval
    routerDeadInterval = hellointerval* int(f.readline())
    f.close()

    f = open('./configs/RouterPriority', 'r')       #RouterPriority
    RouterPriority = int(f.readline())
    f.close()

    # Thread(configuration)

    Thread(receivedOSPFpackets)
    Thread(timeKeeping(hellointerval, RouterPriority, routerDeadInterval, routerID, AreaID))

    # Thread(interfaceStatusChanges)
    # Thread(monitors)

    #To test
    #ipHeader = createIPheader('224.0.0.5', '20.20.20.1',1)
    #neighbord = ['4.5.6.7','2.2.2.2']
    #HelloPack = createHelloPck('255.255.255.0','3.4.5.6' , '6.7.8.9', neighbord, 1, 10, 40)
    #OSPFHeader = createOSPFHeader(1, '1.2.3.4', '0.0.0.0', HelloPack[1], HelloPack[0] , len(neighbord))
    #packet =OSPFHeader+HelloPack[0]
    #deliver(packet, '20.20.20.1')


if __name__ == '__main__':
    main()
