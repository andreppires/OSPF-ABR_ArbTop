import os
import socket
import fcntl
import struct

import binascii

def IPtoDec(ip):
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
         (int(parts[2]) << 8) + int(parts[3])

def DectoIP(dec):
    return '.'.join([str(dec >> (i << 3) & 0xFF)
          for i in range(4)[::-1]])

def IPtoHex(ip):
    return binascii.hexlify(socket.inet_aton(ip))

def IPinNetwork( ip, network, mask):
    ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.')]), 16)
    networkaddr = int(''.join([ '%02x' % int(x) for x in network.split('.')]), 16)
    netmask = IPtoDec(mask)
    if (ipaddr & netmask) == (networkaddr & netmask):
        return True
    else:
        return False

def getNetworkIP(ipadd, netmask):
    splitted = ipadd.split('.')
    if netmask == '255.255.255.0':
        return splitted[0]+'.'+splitted[1]+'.'+splitted[2]+'.0'
    if netmask == '255.255.0.0':
        return splitted[0] + '.' + splitted[1] + '.0.0'
    print "Netmask not supported!"

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

def getNetMaskofInterface(interface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        result= socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            35099,  # SIOCGIFADDR ?
            struct.pack('256s', interface)
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


def fletcher(fin, k, lg):
    if k not in (16, 32, 64):
        raise ValueError("Valid choices of k are 16, 32 and 64")
    nbytes = k // 16
    mod = 2 ** (8 * nbytes) - 1
    s = s2 = 0
    fin = struct.unpack("!"+str(lg/2)+"H", fin)
    fin = list(fin)
    for t in fin:
        s += t
        s2 += s

    return hex(s % mod + (mod + 1) * (s2 % mod))