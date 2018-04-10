from Deliver import deliver
from Dijkstra import shortestPathCalculator
from LSDB import LSDB
from OSPFPackets.LinkStateUpdatePacket import LinkStateUpdatePacket
from utils import getIPofInterface


class ABRLSDB(LSDB):

    def __init__(self, area, routerclass):
        LSDB.__init__(self, area, routerclass)

    def printLSDB(self):
        self.LSAs = sorted(self.LSAs, key=lambda LSA: LSA.getOpaqueID())
        for x in self.LSAs:
            x.printLSA()

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
        self.recalculateshortestPaths()

    def recalculateshortestPaths(self):
        visited = []
        rid = self.routerClass.getRouterID()
        for x in self.LSAs:
            leastcostpathroutes = []
            if x.getOpaqueType() == 20 and x not in visited: #ABR LSA
                visited.append(x)
                continue
            if x.getOpaqueType() == 21 and x not in visited: #Prefix LSA
                bestchoice = x
                visited.append(x)
                destination = x.getSubnetAddress()
                netmask = x.getSubnetMask()
                try:
                    cost = x.getMetric() + \
                           shortestPathCalculator(self.graph, rid, x.getADVRouter())['cost']
                except:
                    continue
                for y in self.LSAs:
                    if y.getOpaqueType() == 21:
                        if y.getSubnetAddress() == destination and y.getSubnetMask() == netmask \
                                and y not in visited:
                            visited.append(y)
                            try:
                                thisCost = y.getMetric() + \
                                           shortestPathCalculator(self.graph,
                                                                  rid, y.getADVRouter())['cost']
                            except Exception:
                                continue
                            if thisCost < cost:
                                bestchoice = y
                                cost = thisCost
                aux = {}
                aux['destination'] = destination
                aux['cost'] = cost
                aux['path'] = bestchoice.getADVRouter()
                aux['netmask'] = netmask
                leastcostpathroutes.append(aux)
            self.routerClass.setNewRoutes(leastcostpathroutes, True)

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
                try:
                    interfaces.remove(sourceInterface)
                except ValueError:
                    continue
            if len(interfaces) != 0:
                pack = LinkStateUpdatePacket(None, 2, 4, self.routerClass.getRouterID(), x,
                                             0, 0, 0, 0, 1)
                pack.receiveLSA(lsa)
                packed = pack.getPackLSUPD()
                deliver(packed, interfaces, None, True)

    def constructgraph(self):
        G = {}
        for x in self.LSAs:
            if x.getLSType() == 11 and x.getOpaqueType() == 20:    # ABR-LSA
                RID = x.getADVRouter()
                Neigh = x.getDicOfNeighbors()
                G[RID] = Neigh
        self.graph = G
