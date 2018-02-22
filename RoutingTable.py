class RoutingTable():
    def __init__(self):
        self.routingEntries=[]

    def removeEntry(self, entry):
        self.routingEntries.remove(entry)

    def addEntry(self, entry):
        self.routingEntries.append(entry)

    def receiveEntry(self, newentry):
        entry = self.alredyExists(newentry)
        if len(entry)>1:
                toCompare=entry[0]
                if self.compareEntry(toCompare, newentry):
                    for x in entry:
                        self.removeEntry(x)
                    self.addEntry(newentry)
                    # Changes in the routing table
                    # recalculate shortest path and cost to destination
                    # recalculate shortest path and cost to Neighbord ABR
        else:
            if len(entry) == 1:
                if self.compareEntry(entry, newentry):
                    self.removeEntry(entry)
                    self.addEntry(newentry)
                    # Changes in the routing table
                    # recalculate shortest path and cost to destination
                    # recalculate shortest path and cost to Neighbord ABR
            else:
                self.addEntry(newentry)


    def alredyExists(self, newentry):
        out=[]
        for x in self.routingEntries:
            if x['destination'] == newentry['destination']:
                out.append(x)
        return out

    def compareEntry(self, old, new):
        # nao interessa o custo se e menor ou mais.
        # cada vez que se recebe um novo LSA volta-se a calcular o custo e o caminho para
        # os destinos. Se forem diferentes entao temos de colocar novas entradas e criar
        # os novos Prefix-LSA respectivos

        if new != old:
            return True
        else:
            return False
