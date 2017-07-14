import threading
from PacktReceiver import startReceiver
from TimeProcessing import TimeStart
from Deliver import deliver
from PacktConst import *


class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()


def configuration():
    print 'config!'


def timeKeeping():
    print 'time keeping'
    TimeStart()


def receivedOSPFpackets():
    print 'Receiver'
    startReceiver()

def interfaceStatusChanges():
    print 'interface status'


def monitors():
    print 'monitors'


def main():
    Thread(timeKeeping)
    Thread(configuration)
    Thread(receivedOSPFpackets)
    Thread(interfaceStatusChanges)
    Thread(monitors)

    deliver(createIPheader('127.0.0.1', '127.0.0.1')+createOSPFHeader(1, '1.1.1.1', '0')+createHelloPck('255.255.255.0', '', '', ''), '224.0.0.5')



if __name__ == '__main__':
    main()
