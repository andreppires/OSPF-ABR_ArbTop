import threading

import os

from PacktReceiver import startReceiver
from Receiver import receiver
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


def receivedOSPFMulticastpackets():
    startReceiver()

def receivedirectPackets(add):
    receiver(add)

def interfaceStatusChanges():
    return 0


def monitors():
    return 0


def main():

    #Stop ferewall service to allow all the packets
    bashCommand = "sudo systemctl stop firewalld.service"
    os.system(bashCommand)

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

    Thread(receivedirectPackets('10.10.10.2'))
    Thread(timeKeeping(hellointerval, RouterPriority, routerDeadInterval, routerID, AreaID))
    Thread(receivedOSPFMulticastpackets)

    # Thread(interfaceStatusChanges)
    # Thread(monitors)


if __name__ == '__main__':
    main()
