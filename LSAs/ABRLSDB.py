import threading

from Deliver import deliver
from Dijkstra import shortestPathCalculator
from LSAs.SummaryLSA import SummaryLSA
from LSDB import LSDB
from OSPFPackets.LinkStateUpdatePacket import LinkStateUpdatePacket
from utils import getIPofInterface


class ABRLSDB(LSDB):

    def __init__(self, area, routerclass):
        LSDB.__init__(self, area, routerclass)


        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def removeLSA(self, LSType, LSID, LSAdvRouter, flush):
        for x in self.LSAs:
            if x.getLSType() == LSType and x.getLSID() == LSID  and x.getADVRouter() == LSAdvRouter:
                if flush:
                    x.setMaxAge()
                    self.FlushLSA(x)
                self.LSAs.remove(x)
                return x
        return False

    def receiveLSA(self, lsa):
        exist = self.LSAAlreadyExists(lsa.getLSType(), lsa.getLSID(), lsa.getADVRouter(), lsa.getOpaqueType(), lsa)
        if exist is not False:
            if lsa.getADVRouter == self.routerClass.getRouterID():
                if lsa.getSeqNumber() > self.getLSA(lsa.getLSType(), lsa.getLSID(), lsa.getADVRouter()).getSeqNumber():
                    self.routerClass.createLSA(self.Area, self.routerClass.getRouterID(), lsa.getSewNumber + 1)
            x = exist[1]
            self.LSAs.remove(x)
            lsa.setNextSN(x.getSeqNumber())
            lsa.setOpaqueID(x.getOpaqueID())
        lsa.calculateChecksum()
        self.LSAs.append(lsa)
        self.FlushLSA(lsa)
        self.constructgraph()
        if lsa.getOpaqueType() == 21: # Prefix LSA
            self.createSummaryLSA(lsa)

    def createSummaryLSA(self, lsa):
        lsid = lsa.getSubnetAddress()
        subnetmask = lsa.getSubnetMask()
        metric = lsa.getMetric()
        rid = self.routerClass.getRouterID()
        try:
            extraCost = shortestPathCalculator(self.graph, rid, lsa.getADVRouter())
            metric += extraCost
        except:
            pass
        self.routerClass.createSummaryLSAfromPrefixLSA(lsid, subnetmask, metric)

    def LSAAlreadyExists(self, LSType, LSID, LSAdvRouter, opaquetype, lsa):
        if LSAdvRouter != self.routerClass.getRouterID():   # Not our LSA
            for x in self.LSAs:
                if x.getLSType() == LSType and x.getLSID() == LSID  and x.getOpaqueType() == opaquetype and \
                                x.getADVRouter() == LSAdvRouter:
                    return [True, x]
            return False
        else:   # our LSA
            if opaquetype == 20:
                # vamos atualizar o meu ABR lsa
                for x in self.LSAs:
                    if x.getLSType() == LSType and x.getOpaqueType() == opaquetype and \
                                    x.getADVRouter() == LSAdvRouter:
                        return [True, x]
                return False
            if opaquetype == 21:
                # vamos atualizar um Prefix lsa meu
                for x in self.LSAs:
                    if x.getLSType() == LSType and x.getOpaqueType() == opaquetype and \
                                    x.getADVRouter() == LSAdvRouter:
                        if x.getSubnetMask() == lsa.getSubnetMask() and \
                                        x.getSubnetAddress() == lsa.getSubnetAddress():
                            return [True, x]
                return False
            if opaquetype == 22:
                # vamos atualizar um ASBR lsa meu
                for x in self.LSAs:
                    if x.getLSType() == LSType and x.getOpaqueType() == opaquetype and \
                                    x.getADVRouter() == LSAdvRouter:
                        if x.getDestinationRID() == lsa.getDestinationRID():
                            return [True, x]
                return False

    def FlushLSA(self, lsa): #flush means send for all interfaces.

        pack = LinkStateUpdatePacket(None, 2, 4, self.routerClass.getRouterID(), self.Area,
                                     0, 0, 0, 0 ,1)
        pack.receiveLSA(lsa)
        packed = pack.getPackLSUPD()
        sourceRouter = lsa.getSource()

        activeAreas = self.routerClass.getActiveAreas()
        for x in activeAreas:
            if sourceRouter == None:
                # pacote nosso. Envia para todas as interfaces ativas
                interfaces = self.routerClass.getInterfaceIPExcept(x)
            else:
                # pacote nao e nosso. Envia para todas as interfaces ativas excepto a referente a esta.
                sourceInterface = self.routerClass.WhatInterfaceReceivedthePacket(sourceRouter)
                interfaces = self.routerClass.getInterfaceIPExcept(x)
                sourceInterface = getIPofInterface(sourceInterface)
                interfaces.remove(sourceInterface)
            if len(interfaces) != 0:
                deliver(packed, interfaces, None, True)

    def constructgraph(self):
        G = {}
        for x in self.LSAs:
            if x.getLSType() == 11 and x.getOpaqueType() == 20:    # ABR-LSA
                RID = x.getADVRouter()
                Neigh = x.getDicOfNeighbors()
                G[RID] = Neigh
        self.graph = G
