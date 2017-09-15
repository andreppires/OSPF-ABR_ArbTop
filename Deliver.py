# some imports
import socket, sys
from struct import *

import struct

from utils import getIPAllInterfaces
proto=89
multicast_group= '224.0.0.5'

def deliver(packet, addr_int):
    multicat_group=(multicast_group, proto)
    # create a raw socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(addr_int))
        s.settimeout(0.2)

    except socket.error as msg:
        sys.exit()
        return 'Socket not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

    # Send the packet finally - the port specified has no effect
    #print "Enviar para:"+ dest_ip
    s.sendto(packet, multicat_group)	# put this in a loop if you want to flood the target
    return 0
