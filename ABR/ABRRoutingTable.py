import threading

import os

import utils
from RoutingTable import RoutingTable


class ABRRoutingTable(RoutingTable):
    def __init__(self, routingclass):
        RoutingTable.__init__(self, routingclass)

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
        # delete previos routing table enties for destination
        bashCommand = "sudo ip route flush " + destination['destination'] + \
                      "/" + str(dotedNetmask)
        os.system(bashCommand)

        if destination['path'] == rid:    # o ABR com melhor custo para o destino sou eu
            entry = self.RoutingClass.getRoutingDatatointraareaRouting(destination['destination'])
            interface = self.RoutingClass.WhatInterfaceReceivedthePacket(entry['path'][0][1])

            # add new routing table entry for destination
            bashCommand = "sudo ip route add "+destination['destination']+\
                          "/"+str(dotedNetmask)+ " via "+utils.getIPofInterface(interface) +" dev "+interface
            os.system(bashCommand)
        else:
            data = self.RoutingClass.getbestpathtoABR(destination['path'])
            if data is not False:
                for path in data:
                    interface = self.RoutingClass.WhatInterfaceReceivedthePacket(data['path'][1])

                    # add new routing table entry for destination
                    bashCommand = "sudo ip route add " + destination['destination'] + \
                                  "/" + str(dotedNetmask) + " via " + utils.getIPofInterface(
                        interface) + " dev " + interface
                    os.system(bashCommand)


