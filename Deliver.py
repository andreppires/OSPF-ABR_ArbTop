# some imports
import socket, sys
from struct import *


def deliver(packet, dest_ip):
    # create a raw socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error, msg:
        sys.exit()
        return 'Socket not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

    # Send the packet finally - the port specified has no effect
    s.sendto(packet, (dest_ip , 0 ))	# put this in a loop if you want to flood the target
    return 0
