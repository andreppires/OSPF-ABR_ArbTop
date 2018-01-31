# some imports
import socket, sys
from struct import *

proto=89
AllSPFRouters= '224.0.0.5'

def deliver(packet, addr_int, destination, multicast):
    if multicast:
        multicat_group=(AllSPFRouters, proto)
        # create a raw socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(addr_int))
            s.settimeout(0.2)

        except socket.error as msg:
            sys.exit()
            return 'Socket not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

        # Send the packet finally - the port specified has no effect
        s.sendto(packet, multicat_group)	# put this in a loop if you want to flood the target
        return 0
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
        except socket.error as msg:
            return 'Socket not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

        # send packet
        s.sendto(packet, (destination, proto))

