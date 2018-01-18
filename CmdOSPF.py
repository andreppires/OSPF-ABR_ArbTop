import cmd
import threading
from time import sleep

import mcast
import utils
from ASBR import ASBR
from Interface import interface
from RouterLSA import RouterLSA

OSPF_TYPE_IGP = '59'
HELLO_PACKET = '01'
PROTO = 89
DB_DESCRIPTION = '02'
LS_REQUEST = '03'
LS_UPDATE = '04'
LS_ACKNOWLEDGE = '05'

BUFSIZE = 1024


class cmdOSPF(cmd.Cmd):
    """Simple command processor for OSPF."""

    def cmdloop(self, routerID, routerDeadInterval, RouterPriority, hellointerval, inttransDelay):
        self.HelloInterval = hellointerval
        self.RouterID = routerID
        self.RouterDeadInterval = routerDeadInterval
        self.RouterPriority = RouterPriority
        self.IntTransDelay = inttransDelay

        self.listInterfaces = []
        self.StartInterfacesList()
        self.ASBR = {}

        self.thread = threading.Thread(target=self.multicastReceiver, args=())
        self.thread.daemon = True
        self.thread.start()

        self.thread = threading.Thread(target=self.incrementLSATimer, args=())
        self.thread.daemon = True
        self.thread.start()

        return cmd.Cmd.cmdloop(self)

    def do_hello(self, line):
        """Hello!!!"""
        print
        "hello!"

    def do_EOF(self, line):
        """to stop reading a file"""
        return True

    def do_exit(self, line):
        """exit from OSPF"""
        print
        "Bye!"
        return True

    def do_quit(self, line):
        """the same as exit"""
        print
        "Bye!"
        return True

    def do_bye(self, line):
        """the same as exit"""
        print
        "Bye!"
        return True

    def do_asbr(self, line):
        self.ASBR[line][0].printASBR()

    def do_list(self, line):
        """list interfaces"""
        print
        utils.getAllInterfaces()

    def do_interface(self, line):
        """interface [name interface] [area]"""
        print
        "Add interface to OSPF"
        inter, area = line.split()
        intadd = utils.getIPofInterface(inter)
        type = utils.getTypeofInterface(inter)
        netmask = utils.getNetMaskofInterface(inter)

        self.setInterface(interface(type, intadd, netmask, area, self.HelloInterval, self.RouterDeadInterval,
                                    self.IntTransDelay, self.RouterPriority, self.RouterID, self), inter, self.RouterID,
                          area)

    def multicastReceiver(self):
        MCAST_GROUP = '224.0.0.5'
        PROTO = 89

        cast = mcast.mcast()
        mgroup = cast.create(MCAST_GROUP, PROTO)
        while True:
            data, addr = cast.recv(mgroup)
            interface_name = self.WhatInterfaceReceivedthePacket(addr[0])
            packet = mcast.readPack(addr, data)
            interface_obj = self.getInterfaceByName(interface_name)
            if interface_name == 0 or interface_obj == None or packet == 0:
                continue
            interface_obj.packetReceived(packet)

    def StartInterfacesList(self):
        for x in utils.getAllInterfaces():
            self.listInterfaces.append({'interface-name': x, 'ip': utils.getIPofInterface(x),
                                        'netmask': utils.getNetMaskofInterface(x), 'interface-object': None})

    def setInterface(self, object_interface, interface_name, rid, area):
        for x in self.listInterfaces:
            if x['interface-name'] == interface_name:
                x['interface-object'] = object_interface

        self.createLSA(area, rid)

    def createLSA(self, area, rid):

        # create/Update RouterLSA
        linkdata = []
        for x in self.listInterfaces:
            if x['interface-object'] != None and x['interface-object'].getArea() == area:
                linkdata.append([x['interface-object'].getDR(), x['interface-object'].getIPIntAddr(), 2, 0,
                                 x['interface-object'].getMetric()])

        rlsa = RouterLSA(0, 2, 1, rid, rid, 0, 1, 0, len(self.listInterfaces), linkdata)
        if area in self.ASBR:
            self.ASBR[area][0].receiveLSA(rlsa)
        else:
            x = [ASBR(area), 0]
            self.ASBR[area] = x
            self.ASBR[area][0].receiveLSA(rlsa)

    def incrementLSATimer(self):
        while True:
            for x in self.ASBR:
                if self.ASBR[x][1] == 1800:
                    self.createLSA(self.ASBR[x][0].getArea(), self.RouterID)
                    self.ASBR[x][1] = 0
                else:
                    self.ASBR[x][1] = self.ASBR[x][1] + 1
            sleep(1)

    def WhatInterfaceReceivedthePacket(self, sourceIP):
        for x in range(len(self.listInterfaces)):
            if utils.IPinNetwork(sourceIP, self.listInterfaces[x]['ip'], self.listInterfaces[x]['netmask']):
                return self.listInterfaces[x]['interface-name']
        return 0

    def getInterfaceByName(self, interface_name):
        for x in range(len(self.listInterfaces)):
            if self.listInterfaces[x]['interface-name'] == interface_name:
                return self.listInterfaces[x]['interface-object']

        return 0  # error

    def receiveLSAtoASBR(self, lsa, area):
        self.ASBR[area][0].receiveLSA(lsa)
