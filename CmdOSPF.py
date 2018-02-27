import cmd
import threading
from time import sleep
from socket import *

import mcast
import utils
from LSAs.ABRLSDB import ABRLSDB
from LSAs.ASBRLSA import ASBRLSA
from LSAs.PrefixLSA import PrefixLSA
from LSDB import LSDB
from Interface import interface
from LSAs.RouterLSA import RouterLSA
from LSAs.ABRLSA import ABRLSA
from RoutingTable import RoutingTable

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
        self.LSDB = {}
        self.OpaqueID = 0
        self.routingTable = RoutingTable(self)

        self.thread = threading.Thread(target=self.multicastReceiver, args=())
        self.thread.daemon = True
        self.thread.start()

        self.thread = threading.Thread(target=self.incrementLSATimer, args=())
        self.thread.daemon = True
        self.thread.start()

        return cmd.Cmd.cmdloop(self)

    def do_hello(self, line):
        """Hello!!!"""
        print "hello!"

    def do_EOF(self, line):
        """to stop reading a file"""
        return True

    def do_exit(self, line):
        """exit from OSPF"""
        print "Bye!"
        return True

    def do_quit(self, line):
        """the same as exit"""
        print "Bye!"
        return True

    def do_bye(self, line):
        """the same as exit"""
        print "Bye!"
        return True

    def do_lsdb(self, line):
        self.LSDB[line][0].printLSDB()

    def do_graph(self, line):
        self.LSDB[line][0].printGraph()

    def do_list(self,line):
        """list interfaces"""
        print utils.getAllInterfaces()

    def do_routing_table(self, line):
        self.routingTable.printAll()

    def do_interface(self, line):
        """interface [name interface] [area] [cost]"""
        print "Add interface to OSPF"
        inter, area, cost = line.split()
        cost = int(cost)
        intadd = utils.getIPofInterface(inter)
        type = utils.getTypeofInterface(inter)
        netmask = utils.getNetMaskofInterface(inter)


        self.setInterface(interface(type, intadd, netmask, area, self.HelloInterval, self.RouterDeadInterval,
                                    self.IntTransDelay, self.RouterPriority, self.RouterID, self, cost), inter,
                          self.RouterID, area)

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
            if interface_name == 0 or interface_obj==None or packet==0:
                continue
            if packet.getType() == 11:
                    self.receiveLSAtoLSDB(packet.getReceivedLSAs()[0], 'ABR')
            interface_obj.packetReceived(packet)
            
    def unicastReceiver(self, interfaceaddr, type, timeout):
        PROTO = 89
        bufferSize = 1500

        s = socket(AF_INET, SOCK_RAW, PROTO)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((interfaceaddr, PROTO))
        if timeout:
            s.settimeout(10.0)
        try:
            while True:
                data, addr = s.recvfrom(bufferSize)
                packet = mcast.readPack(addr, data)
                if packet.getType() != type:
                    continue
                break
        except Exception:
            return 0

        return packet

    def StartInterfacesList(self):
        for x in utils.getAllInterfaces():
            self.listInterfaces.append({'interface-name':x, 'ip':utils.getIPofInterface(x),
                                        'netmask':utils.getNetMaskofInterface(x), 'interface-object': None})

    def setInterface(self, object_interface , interface_name, rid, area):
        for x in self.listInterfaces:
            if x['interface-name']==interface_name:
                x['interface-object']=object_interface
                x['interface-area']=area

        self.createLSA(area, rid, False)

    def createLSA(self, area, rid, sn):
        # create/Update RouterLSA
        linkdata=[]
        for x in self.listInterfaces:
            if x['interface-object'] != None and x['interface-object'].getArea() == area:
                typeLink = x['interface-object'].getTypeLink()
                if typeLink == 2:   # transit network
                    linkdata.append([x['interface-object'].getDR(), x['interface-object'].getIPIntAddr(), typeLink,
                                     0, x['interface-object'].getMetric()])
                else:
                    if typeLink == 3:   # stub
                        networkIP = utils.getNetworkIP(x['interface-object'].getIPIntAddr(), x['interface-object'].
                                                       getIPInterfaceMask())
                        linkdata.append([networkIP, x['interface-object'].getIPInterfaceMask(),
                                         typeLink, 0, x['interface-object'].getMetric()])
                    else:
                        "Error creating LSA. Link Type not supported"
        if sn == False:
            rlsa = RouterLSA(None, 0,2,1,rid, rid, 0, 1, 0, 0, 0, 0, len(linkdata), linkdata)
        else:
            rlsa = RouterLSA(None, 0, 2, 1, rid, rid, sn, 1, 0, 0, 0, 0, len(linkdata), linkdata)

        if area in self.LSDB:
            if len(self.LSDB)>1:
                rlsa.setBbit(True)
                self.threadforAbrLsdbStart()
            self.LSDB[area][0].receiveLSA(rlsa)
        else:
            if area != 'ABR':
                x = [LSDB(area, self), 0]
            else:
                x = [ABRLSDB(area, self), 0]
            self.LSDB[area] = x
            if len(self.LSDB)>1:
                rlsa.setBbit(True)
                self.threadforAbrLsdbStart()

            self.LSDB[area][0].receiveLSA(rlsa)

    def threadforAbrLsdbStart(self):
        t = threading.Thread(target=self.createLSDBforABROverlay, args=())
        t.daemon = True
        t.start()

    def createLSDBforABROverlay(self):
        if 'ABR' not in self.LSDB:
            x = [ABRLSDB('ABR', self), 0]
            self.LSDB['ABR'] = x
            self.createASBRLSAs()
            self.createPrefixLSAs()
        self.createABRLSA()

    def createABRLSA(self):

        # create ABR LSA
        opaqueID = self.getOpaqueID()
        lsa = ABRLSA(None, 0, 2, opaqueID, self.RouterID, 0, 0, 0)

        # get ABR Neigbords and metric
        ABRNeighbords = []
        for x in self.LSDB:
            if x == 'ABR':
                continue
            N = self.LSDB[x][0].getNeighbordABR(self.RouterID)
            if len(N) > 0:
                ABRNeighbords.append(N)

        # add them
        for x in ABRNeighbords:
            lsa.addLinkDataEntry(x)
        # add LSA to LSDB
        self.LSDB['ABR'][0].receiveLSA(lsa)

    def createPrefixLSAs(self):
        self.routingTable.createPrefixLSAs()

    def createASBRLSAs(self):
        # Get ASBRs Routers
        for x in self.LSDB:
            if x == 'ABR': # special LSDB
                continue
            for y in self.LSDB[x][0].getAsbrRouterLSAS(self.RouterID):
                # create PrefixLSA for every NetworkLSA
                opaqueID = self.getOpaqueID()
                data = y.getPrefixAndCost()
                lsa = ASBRLSA(None, 0, 2, opaqueID, self.RouterID, 0, 0, 0, data[0], data[1])
                self.LSDB['ABR'][0].receiveLSA(lsa)

    def getActiveAreas(self):
        out =[]
        for x in self.LSDB:
            if x == 'ABR': # special LSDB
                continue
            out.append(x)
        return out

    def getOpaqueID(self):
        self.OpaqueID += 1
        return self.OpaqueID

    def incrementLSATimer(self):
        while True:
            for x in self.LSDB:
                if self.LSDB[x][1] == 1800:
                    self.createLSA(self.LSDB[x][0].getArea(), self.RouterID, False)
                    self.LSDB[x][1] = 0
                else:
                    self.LSDB[x][1] = self.LSDB[x][1]+1
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
        return 0 #error

    def receiveLSAtoLSDB(self, lsa, area):
        self.LSDB[area][0].receiveLSA(lsa)

    def getLSDB(self, areaid):
        return self.LSDB[areaid][0]

    def getInterfaceIPExcept(self, area):
        out = []
        for x in self.listInterfaces:
            if x['interface-object'] != None and x['interface-area'] == area:
                out.append(x['interface-object'].getIPIntAddr())
        return out

    def getAllInterface(self):
        out = []
        for x in self.listInterfaces:
            if x['interface-object'] != None:
                out.append(x['interface-object'].getIPIntAddr())
        return out

    def getRouterID(self):
        return self.RouterID

    def receivenewLSA(self, lsa):
        if 'ABR' in self.LSDB:
            self.receiveLSAtoLSDB(lsa, 'ABR')

    def setNewRoutes(self, routes):
        self.routingTable.receiveEntries(routes)

    def createPrefixLSA(self, prefix, cost, netmask):
        opaqueID = self.getOpaqueID()
        lsa = PrefixLSA(None, 0, 2, opaqueID, self.RouterID, 0, 0, 0,
                        cost, netmask, prefix)
        if 'ABR' in self.LSDB:
            self.LSDB['ABR'][0].receiveLSA(lsa)


