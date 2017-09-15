from time import sleep
from utils import getIPAllInterfaces
from Deliver import deliver
from PacktConst import createIPheader, createHelloPck, createOSPFHeader


def TimeStart(Helloint,rpi, rdi,rid, aid):
    #sleep(15) # TODO dar tempo para ver se alguem esta on no link
    while True:

        neighbord = ['4.5.6.7', '2.2.2.2']
        HelloPack = createHelloPck('255.255.255.0', '3.4.5.6', '6.7.8.9', neighbord, rpi, Helloint,
                                   rdi)
        OSPFHeader = createOSPFHeader(1, rid, aid, HelloPack[1], HelloPack[0], len(neighbord))
        packet = OSPFHeader + HelloPack[0]

        netinterfaces=getIPAllInterfaces().items()
        for x in range(0, len(netinterfaces)):
            if netinterfaces[x][0]=='lo':
                continue
            else:
                deliver(packet, netinterfaces[x][1])

        sleep(Helloint)



