from random import randint
import socket,struct

OSPF_HELLO = "> L HBB L L L"
OSPF_HDR = "> BBH L L HH L L"
OSPF_HDR_LEN = struct.calcsize(OSPF_HDR)
OSPF_HELLO_LEN= struct.calcsize(OSPF_HELLO)

def createchecksum(msg, lenN):
    lenPck=((lenN*4)+44)
    pktOSPF = msg[:lenPck]
    fields = struct.unpack("!"+str(lenPck/2)+"H", pktOSPF)
    fields = list(fields)

    sum = 0
    # Zeroize current checksum and auth fields for calculation
    fields[6] = 0
    fields[8] = 0
    fields[9] = 0

    # Add all remains field and convert to hex
    for f in fields:
        sum += f
    sum = hex(sum)

    compl = "0x" + sum[-4:]
    carry = sum[:len(sum) - 4]
    compl = int(compl, 16) + int(carry, 16)
    checksum = compl ^ 0xffff
    return hex(checksum)

def IPtoDec(ip):
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
         (int(parts[2]) << 8) + int(parts[3])

def DectoIP(dec):
    return '.'.join([str(dec >> (i << 3) & 0xFF)
          for i in range(4)[::-1]])

def createIPheader(dest_ip, source_ip, ttl):

    # ip header fields
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0  # kernel will fill the correct total length
    ip_id = (randint(0, 9999))  # random: should not be the same
    ip_frag_off = 0
    ip_ttl = ttl
    ip_proto = 89
    ip_check = 0  # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton(source_ip)  # Spoof the source ip address if you want to
    ip_daddr = socket.inet_aton(dest_ip)

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check,
                     ip_saddr, ip_daddr)

    return ip_header


def createOSPFHeader(type, rid, aid, helloLen, packHello, lenNeig) :

    version = 2
    typeof = type
    pcklength= OSPF_HDR_LEN + helloLen #TODO verificar se esta correto
    routerID = IPtoDec(rid)
    AreaID= IPtoDec(aid)
    checksum= 0 #TODO
    autype= 0 #TODO
    Authentic= 0 #TODO
    Autentic2= 0 #TODO
    ospfheader= struct.pack(OSPF_HDR, version, typeof, pcklength, routerID, AreaID, checksum, autype, Authentic, Autentic2)

    ##-- Checksum --##
    data= ospfheader + packHello
    OSPF_Checksum= createchecksum(data, lenNeig)
    checksum = int(OSPF_Checksum, 16)

    ospfheader = struct.pack(OSPF_HDR, version, typeof, pcklength, routerID, AreaID, checksum, autype, Authentic, Autentic2)
    return ospfheader


def createHelloPck(netmask, DR, BDR, Neighbors, rpri, helllo, routDeadInterval):

    networkmask = IPtoDec(netmask)
    helloint = int(helllo)
    Options = 2  # TODO verificar que options sao estas
    routerPri = int(rpri)  # TODO verificar qual o valor correto
    routDeadInt = int(routDeadInterval) # TODO verificar qual o valor correto
    DesigRout = IPtoDec(DR)
    BackupDesigRout = IPtoDec(BDR)

    hello = struct.pack(OSPF_HELLO, networkmask, helloint, Options, routerPri, routDeadInt, DesigRout, BackupDesigRout)

    novaStruct =OSPF_HELLO
    # Neighbors tem de ser uma lista/conjunto dos varios vizinhos.
    for x in Neighbors:
        if x.find(".")==-1: #caso o argumento nao contenha um ponto - nao e um ip
            continue
        else:
            hello = hello + struct.pack('!L', (IPtoDec(x)))
            novaStruct=novaStruct+ " L"
    helloLen= struct.calcsize(novaStruct)

    return hello, helloLen


