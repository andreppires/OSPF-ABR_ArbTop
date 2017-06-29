# some imports
import socket, sys
from struct import *


def receiver():
    # create a raw socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error, msg:
        sys.exit()
        return 'Socket not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

    s.recv() # not sure
    return 0