import cmd
import threading
import mcast
import utils
from Interface import interface

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
        ### {interfacename}
        self.StartInterfacesList()

        self.thread = threading.Thread(target=self.multicastReceiver)
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
                                    self.IntTransDelay, self.RouterPriority, self.RouterID), inter)

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

    def setInterface(self, object_interface, interface_name):
        for x in self.listInterfaces:
            if x['interface-name'] == interface_name:
                x['interface-object'] = object_interface

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
