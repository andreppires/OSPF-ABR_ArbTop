from utils import getAllInterfaces, getIPofInterface
from utils import getTypeofInterface

# Tabela/Lista de adjacencias
# |Name   | IP         |Type       | NeigbourdList      | DR      | BDR
# | ens33 | 20.20.20.1 | Broadcast | [2.2.2.2, 1.3.4.5] | 2.2.2.2 | 1.2.3.4
# | ens37 | 10.10.10.2 | Broadcast | [l1.1.1.1]         | 1.1.1.1 | 1.2.3.4
#
#

# Start adjacencies
interfaces= getAllInterfaces()
interfaces.remove('lo')
global adjacencies
adjacencies = []
aux= []

for x in interfaces:
    listaux=[x, getIPofInterface(x), getTypeofInterface(x).rstrip(),list(aux), '', '']
    adjacencies.append(listaux)

def getListOfAdjacencies(interface):
    for x in adjacencies:
        if x[0]==interface:
            return x
    return 0 #not found

def getListOfAdjacenciesByIP(ip):
    for x in adjacencies:
        if x[1]==ip:
            return x
    return 0 #not found

def addneighbordToint(intIP, neigbord):
    listIP=getListOfAdjacenciesByIP(intIP)
    IPadj=listIP[3]
    IPadj.append(neigbord)
    return 0

def remneighbordToint(intIP,neigbord):
    listIP = getListOfAdjacenciesByIP(intIP)
    IPadj = listIP[3]
    IPadj.remove(neigbord)
    return 0


