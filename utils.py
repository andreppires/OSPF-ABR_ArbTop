import os
import socket
import fcntl
import struct
import binascii
import sys

from LSAs.LSAHeader import LSAHeader

OSPF_DD_HEADER = ">BBBB L"
OSPF_HELLO = "> L HBB L L L"
OSPF_HDR = "> BBH L L HH L L"
OSPF_LSA_HDR = "> HBB L L L HH"
OSPF_HDR_LEN = struct.calcsize(OSPF_HDR)
OSPF_HELLO_LEN= struct.calcsize(OSPF_HELLO)
OSPF_DD_HEADER_LEN = struct.calcsize(OSPF_DD_HEADER)
OSPF_LSA_HDR_LEN = struct.calcsize(OSPF_LSA_HDR)

def createchecksum(msg, lenN, type):
    lenPck = len(msg)
    if type == 5:
        lenPck = OSPF_HDR_LEN + lenN
    fields = struct.unpack("!"+str(lenPck/2)+"H", msg)
    fields = list(fields)

    sum = 0
    # Zeroize current checksum and auth fields for calculation
    fields[6] = 0
    fields[8] = 0
    fields[9] = 0

    # Add all remains field and convert to hex
    for f in fields:
        sum =sum + f

    high,low = divmod(sum, 0x10000)
    compl = low + high
    checksum = compl ^ 0xffff
    return hex(checksum)

def IPtoDec(ip):
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
         (int(parts[2]) << 8) + int(parts[3])


def DectoIP(dec):
    return '.'.join([str(dec >> (i << 3) & 0xFF)
          for i in range(4)[::-1]])


def unpackLSAHeader(unpacked):
        pack = struct.unpack(OSPF_LSA_HDR, unpacked)
        newHeader = LSAHeader(None, pack[0], pack[1], pack[2], DectoIP(pack[3]), DectoIP(pack[4]), hex(pack[5]), pack[6], pack[7])
        return newHeader


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


def getNetworkfromIPandMask(ip, mask):
    ipaddr = int(''.join(['%02x' % int(x) for x in ip.split('.')]), 16)
    netmask = IPtoDec(mask)
    network = DectoIP(ipaddr & netmask)
    return network

def getNetworkIP(ipadd, netmask):
    splitted = ipadd.split('.')
    if netmask == '255.255.255.0':
        return splitted[0]+'.'+splitted[1]+'.'+splitted[2]+'.0'
    if netmask == '255.255.0.0':
        return splitted[0] + '.' + splitted[1] + '.0.0'
    print "Netmask not supported!"

def calcDottedNetmask(mask):
    return sum([bin(int(x)).count('1') for x in mask.split('.')])


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
    CHKSUM_OFFSET = 16

    packet = fin[:CHKSUM_OFFSET] + '\x00\x00' + fin[CHKSUM_OFFSET + 2:]  # turns chksum to 0
    c0 = c1 = 0
    for char in packet[2:]:  # ignores LS Age
        c0 += ord(char)
        c1 += c0
    c0 %= 255
    c1 %= 255
    x = ((len(packet) - 16 - 1) * c0 - c1) % 255
    if x <= 0:
        x += 255
    y = 510 - c0 - x
    if y > 255:
        y -= 255
    return chr(x) + chr(y)
