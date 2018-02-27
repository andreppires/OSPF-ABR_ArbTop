import threading
from operator import itemgetter
from time import sleep

from Deliver import deliver
from OSPFPackets.LinkStateUpdatePacket import LinkStateUpdatePacket
from utils import getIPofInterface, getNetworkfromIPandMask
from Dijkstra import shortestPathCalculator


class LSDB:

    def __init__(self, area, routerclass):
        self.LSAs = []
        self.MaxAge = 3600
        self.MaxSeqNumber = 0x7fffffff
        self.Area = area
        self.routerClass = routerclass
        self.graph = None


        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def getArea(self):
        return self.Area

    def printGraph(self):
        print self.graph

    def run(self):
        sleep(1)
        while True:
            for x in self.LSAs:
                if x.getAge() ==self.MaxAge:
                    self.LSAs.remove(x)
                else:
                    x.countAge()
                sleep(1)

    def LSAAlreadyExists(self, LSType, LSID, LSAdvRouter, opaquetype, lsa):
        for x in self.LSAs:
            if x.getLSType() == LSType and x.getLSID() == LSID  and x.getADVRouter() == LSAdvRouter:
                return [True, x]
        return False

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
        if self.LSAAlreadyExists(lsa.getLSType(), lsa.getLSID(), lsa.getADVRouter(), None, None):
            x = self.removeLSA(lsa.getLSType(), lsa.getLSID(), lsa.getADVRouter(), False)
            lsa.setNextSN(x.getSeqNumber())
        lsa.calculateChecksum()
        self.LSAs.append(lsa)
        self.FlushLSA(lsa)
        self.constructgraph()
        self.recalculateshortestPaths()

    def recalculateshortestPaths(self):
        leastcostpathroutes = []
        rid = self.routerClass.getRouterID()
        for x in self.LSAs:
            routes = []
            haveToSend = False

            if x.getLSType() == 2:    # Network-LSA
                try:
                    result = []
                    for y in x.getAttachedRouters():
                        result.append(shortestPathCalculator(self.graph, rid, y))
                    result = sorted(result, key=itemgetter('cost'))
                    leastcost = result[0]['cost']
                    for z in range(0, len(result)-1):
                        if result[z]['cost'] != leastcost:
                            break
                        routes.append(result[z]['path'])
                        haveToSend = True
                except Exception:
                    pass
                if haveToSend:
                    aux = {}
                    aux['destination'] = getNetworkfromIPandMask(x.getLSID(), x.getNetworkMask())
                    aux['cost'] = leastcost
                    aux['path'] = routes
                    aux['netmask'] = x.getNetworkMask()
                    aux['area'] = self.getArea()
                    leastcostpathroutes.append(aux)


        self.routerClass.setNewRoutes(leastcostpathroutes)

    def FlushLSA(self, lsa): #flush means send for all interfaces.

        pack = LinkStateUpdatePacket(None, 2, 4, self.routerClass.getRouterID(), self.Area,
                                     0, 0, 0, 0 ,1)
        pack.receiveLSA(lsa)
        packed = pack.getPackLSUPD()
        sourceRouter = lsa.getSource()
        if sourceRouter == None:
            # pacote nosso. Envia para todas as interfaces ativas
            interfaces = self.routerClass.getInterfaceIPExcept(self.Area)
        else:
            # pacote nao e nosso. Envia para todas as interfaces ativas excepto a referente a esta.
            sourceInterface = self.routerClass.WhatInterfaceReceivedthePacket(sourceRouter)
            interfaces = self.routerClass.getInterfaceIPExcept(self.Area)
            sourceInterface = getIPofInterface(sourceInterface)
            interfaces.remove(sourceInterface)
        if len(interfaces) != 0:
            deliver(packed, interfaces, None, True)

    def printLSDB(self):
        self.LSAs = sorted(self.LSAs, key=lambda LSA: LSA.getLSType())
        for x in self.LSAs:
            x.printLSA()

    def getHeaderLSAs(self):
        list=[]
        for x in self.LSAs:
            list.append(x.getHeaderPack(False))
        return list

    def HaveThisLSA(self, lsa):
        for x in self.LSAs:
            if lsa.getLSType == x.getLSType() and lsa.getLSID() == x.getLSID and lsa.getADVRouter() == x.getADVRouter():
                if lsa.getSeqNumber() > x.getSeqNumber() or (lsa.getSeqNumber() == x.getSeqNumber() and
                                                             lsa.getChecksum() >= x.getChecksum()):
                    return True     # same LSA but more recent
                else:
                    return False    # same LSA. Not most recent
        return False        # dont have that LSA

    def getLSA(self, type, id, advR):
        for x in self.LSAs:
            if type == x.getLSType() and id == x.getLSID() and advR == x.getADVRouter():
                return x
        return False        # dont have that LSA

    def getNeighbordABR(self, rid):
        out = []
        for x in self.LSAs:
            if x.getLSType == 1 and x.getBbit() is True and x.getADVRouter() != rid:
                out.append(10, x.getADVRouter())    # TODO get cost to destination
        return out

    def getNetworkLSAs(self):
        out = []
        for x in self.LSAs:

            if x.getLSType() == 2:  # NetworkLSA
                out.append(x)
        return out

    def getAsbrRouterLSAS(self, rid):
        out = []
        for x in self.LSAs:
            if x.getLSType() == 1 and x.getEbit() is True  and x.getBbit() is True and x.getADVRouter() != rid:
                out.append([10, x.getADVRouter()])  # TODO get cost to destination
        return out

    def constructgraph(self):
        G = {}
        for x in self.LSAs:
            if x.getLSType() == 1:    # Router-LSA
                RID = x.getADVRouter()
                Neigh = x.getDicOfNeighbors()
                G[RID] = Neigh
            else:
                if x.getLSType() == 2:  #Network-LSA
                    RID = x.getLSID()
                    Neigh = x.getDicOfNeighbors()
                    G[RID] = Neigh
        self.graph = G





