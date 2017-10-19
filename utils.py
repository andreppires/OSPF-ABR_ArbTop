import os
import socket
import fcntl
import struct

def getAllInterfaces():
    return os.listdir('/sys/class/net/')

def getIPofInterface(interface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', interface[:15])
        )[20:24])
import os
import socket
import fcntl
import struct

def getAllInterfaces():
    return os.listdir('/sys/class/net/')

def getIPofInterface(interface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        result= socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface[:15])
            )[20:24])
    except IOError: #interface not found
        return 0
    return result

def getIPAllInterfaces():
    result={}
    interfaces= getAllInterfaces()
    for x in interfaces:
        result[x]=getIPofInterface(x)
    return result

def getTypeofInterface(interface):
    # http://elixir.free-electrons.com/linux/latest/source/include/uapi/linux/if_arp.h
    # type= 1 > Ethernet
    # type=803 > RadioTap (wifi?)
    # type 772 > loopback
    path='/sys/class/net/'+ str(interface)+'/type'
    f = open(path, 'r')
    type = (f.readline())
    f.close()
    return type

def getInterfaceByIP(ip):
    info=getIPAllInterfaces()
    for x in info:
        if info[x] == ip:
            return x
    return 0


def getIPAllInterfaces():
    result={}
    interfaces= getAllInterfaces()
    for x in interfaces:
        result[x]=getIPofInterface(x)
    return result
