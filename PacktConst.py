from random import randint
import socket
from struct import pack

def createIPheader(dest_ip, source_ip):

    # ip header fields
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0  # kernel will fill the correct total length
    ip_id = (randint(0, 9999))  # random: should not be the same
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0  # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton(source_ip)  # Spoof the source ip address if you want to
    ip_daddr = socket.inet_aton(dest_ip)

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check,
                     ip_saddr, ip_daddr)
    return ip_header


def createOSPFHeader(type, rid, aid) :

    version = 2
    typeof = type
    pcklength= 0 #TODO
    routerID= rid
    AreaID= aid
    checksum= 0 #TODO
    autype= 0 #TODO
    Authentic= '' #TODO

    ospfheader= pack('!BBH4s4sHH8s', version, typeof, pcklength, routerID, AreaID, checksum, autype, Authentic)
    return ospfheader


def createHelloPck(netmaks, DR, BDR, Neighbors):
    networkmaks = netmaks
    helloint = 10
    Options = 0  # TODO verificar que options sao estas
    routerPri = 1  # TODO verificar qual o valor correto
    routDeadInt = '3600'  # TODO verificar qual o valor correto
    DesigRout = DR
    BackupDesigRout = BDR

    hello = pack('!4sHBB4s4s4s ', networkmaks, helloint, Options, routerPri, routDeadInt, DesigRout, BackupDesigRout)

    # Neighbors tem de ser uma lista/conjunto dos varios vizinhos.
    for x in Neighbors:
        hello = hello + pack('4s', x)

    return hello


