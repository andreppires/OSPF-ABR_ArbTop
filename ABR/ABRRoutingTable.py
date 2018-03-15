import threading

import os

import utils
from RoutingTable import RoutingTable


class ABRRoutingTable(RoutingTable):
    def __init__(self, routingclass):
        RoutingTable.__init__(self, routingclass)
        self.kernelEntries ={}

    def AlertPrefixLSA(self, destination):
        prefix = destination['destination']
        cost = destination['cost']
        netmaks = destination['netmask']

        self.threadTOtakeCareofKernelRoutingTable(destination)
        self.RoutingClass.createSummaryLSAfromPrefixLSA(prefix, netmaks, cost)


    def threadTOtakeCareofKernelRoutingTable(self, dest):
        self.thread = threading.Thread(target=self.takeCareofKernelRoutingTable, args=[dest])
        self.thread.daemon = True
        self.thread.start()

    def takeCareofKernelRoutingTable(self, destination):
        rid = self.RoutingClass.getRouterID()

        dotedNetmask = utils.calcDottedNetmask(destination['netmask'])
        dest = destination['destination']

        if dest in self.kernelEntries:
            # delete previos routing table enties for destination
            listEntries = self.kernelEntries[dest]
            for x in listEntries:
                bashCommand = "sudo ip route flush " + x
                os.system(bashCommand)

        if destination['path'] == rid:    # o ABR com melhor custo para o destino sou eu
            entry = self.RoutingClass.getRoutingDatatointraareaRouting(dest)
            interface = self.RoutingClass.WhatInterfaceReceivedthePacket(entry['path'][0][1])

            entrie =dest + "/" + str(dotedNetmask) +\
                    " via " + utils.getIPofInterface(interface) + " dev " + interface + " metric 110"
            # add new routing table entry for destination
            bashCommand = "sudo ip route add " + entrie
            os.system(bashCommand)
            self.kernelEntries[dest] = [entrie]
        else:
            data = self.RoutingClass.getbestpathtoABR(destination['path'])
            if data is not False:
                self.kernelEntries[dest] = []
                for path in data:
                    interface = self.RoutingClass.WhatInterfaceReceivedthePacket(path[1])
                    entrie = dest + "/" + str(dotedNetmask) +\
                             " via " + utils.getIPofInterface(interface) + " dev " + interface + " metric 110"

                    # add new routing table entry for destination
                    bashCommand = "sudo ip route add " + entrie
                    os.system(bashCommand)
                    self.kernelEntries[dest].append(entrie)


    def RemoveEntriesonKernelRT(self):
        for x in self.kernelEntries:
            listentries = self.kernelEntries[x]
            for y in listentries:
                bashCommand = "sudo ip route flush " + y[:-11]
                os.system(bashCommand)
