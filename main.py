import threading
from TimeProcessing import start
from CreatePacket import createIPheader

#dest='127.0.0.1'
#source='127.0.0.1'
#x= createIPheader(dest, source)


class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()

def configuration():
    print 'config!'

def timeKeeping():
    print 'time keeping'
    start()

def receivedOSPFpackets():
    print 'received packets'

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

if __name__ == '__main__':
        main()





