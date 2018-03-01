from RoutingTable import RoutingTable


class ABRRoutingTable(RoutingTable):
    def __init__(self, routingclass):
        RoutingTable.__init__(self, routingclass)

    def AlertPrefixLSA(self, destination):
        prefix = destination['destination']
        cost = destination['cost']
        netmaks = destination['netmask']

        self.RoutingClass.createSummaryLSAfromPrefixLSA(prefix, netmaks, cost)

