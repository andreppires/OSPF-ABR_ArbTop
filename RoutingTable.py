from operator import itemgetter


class RoutingTable():
    def __init__(self, routingclass):
        self.routingEntries=[]
        self.RoutingClass = routingclass

    def removeEntry(self, entry):
        self.routingEntries.remove(entry)

    def addEntry(self, entry):
        self.routingEntries.append(entry)

    def printAll(self):
        data = sorted(self.routingEntries, key=itemgetter('destination'))
        for x in data:
            print"Prefix:", x['destination'], '\tMask:', x['netmask'], '\tCost:',\
                x['cost'], '\tPath:', x['path']

    def receiveEntries(self, listentries):
        for destination in listentries:
            entry = self.alredyExists(destination)
            if entry is not False:
                if self.compareEntry(entry, destination):
                    self.removeEntry(entry)
                    self.addEntry(destination)
                    # Changes in the routing table
                    # recalculate shortest path and cost to destination
                    # recalculate shortest path and cost to Neighbord ABR
                    self.AlertPrefixLSA(destination)

                else:
                    # equal cost. Dont need to anounce new Prefix LSA
                    # Update path
                    entry['path']= destination['path']
            else:
                self.addEntry(destination) # nao havia nenhuma rota para o destino
                self.AlertPrefixLSA(destination)

    def AlertPrefixLSA(self, destination):
        prefix = destination['destination']
        cost = destination['cost']
        netmaks = destination['netmask']

        self.RoutingClass.createPrefixLSA(prefix, cost, netmaks)

    def alredyExists(self, newentry):
        for x in self.routingEntries:
            if x['destination'] == newentry['destination']:
                return x
        return False

    def compareEntry(self, old, new):
        if new['cost'] != old['cost']:
            return True
        else:
            return False

    def createPrefixLSAs(self):
        for x in self.routingEntries:
            self.AlertPrefixLSA(x)