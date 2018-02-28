import time, threading
from operator import itemgetter

from OSPFPackets.DatabaseDescriptionPacket import DatabaseDescriptionPacket
from Deliver import deliver
from OSPFPackets.HelloPacket import HelloPacket
from OSPFPackets.LinkStateAcknowledgmentPacket import LinkStateAcknowledgmentPacket
from OSPFPackets.LinkStateUpdatePacket import LinkStateUpdatePacket
from utils import unpackLSAHeader
from OSPFPackets.LinkStateRequestPacket import LinkStateRequestPacket
from Neighbord import neighbord
from LSAs.NetworkLSA import NetworkLSA
from LSAs.PrefixLSA import PrefixLSA


class interface:
    """Interface class"""
    def __init__(self, type, ipint, ipintmask, areaID, helloint, routerDeadInterval, IntTransDelay,
                 routerPriority, rid, router, interfaceCost):
        self.routerclass = router
        self.Type = type
        self.State = 1
        self.IPInterfaceAddress = ipint
        self.IPInterfaceMask = ipintmask
        self.AreaID = areaID
        self.RouterID=rid
        self.HelloInterval = helloint
        self.RouterDeadInterval = routerDeadInterval
        self.InfTransDelay = IntTransDelay
        self.RouterPriority = routerPriority

        self.HelloTimer = 0
        self.WaitTimer = routerDeadInterval
        self.Neighbours = []
        self.DesignatedRouter='0.0.0.0'
        self.BackupDesignatedRouter='0.0.0.0'
        self.InterfaceOutputCost = interfaceCost
        self.RxmtInterval = 30
        self.Autye= None
        self.AuthenticationKey = None
        self.TypeofInterface = 3    # Stub
        self.LSATimer = 60*30


        self.InterfaceStates={0:"Down",
                              1:"Loopback",
                              2:"Waiting",
                              3:"Point-to-point",
                              4:"DR Other",
                              5:"Backup",
                              6:"DR"}

        self.thread = threading.Thread(target=self.statelife, args=())
        self.thread.daemon = True
        self.thread.start()

    def getMetric(self):
        return self.InterfaceOutputCost

    def decreaseHelloTimer(self):
        self.HelloTimer=self.HelloTimer -1

    def resetHelloTimer(self):
        self.HelloTimer=self.HelloInterval

    def decreaseWaitTimer(self):
        self.WaitTimer=self.WaitTimer - 1

    def resetWaitTimer(self):
        self.WaitTimer=self.RouterDeadInterval

    def getNeighbords(self):
        aux=[]
        for x in self.Neighbours:
            aux.append(x['RouterID'])
        return aux

    def sendHello(self):
        neighbords=self.getNeighbords()

        HelloPack = HelloPacket(self.IPInterfaceAddress, 2, 1, self.RouterID, self.AreaID, 0, 0, 0,
                                0, self.IPInterfaceMask, self.HelloInterval, 2, self.RouterPriority,
                                self.RouterDeadInterval, self.DesignatedRouter, self.BackupDesignatedRouter, neighbords)

        deliver(HelloPack.getHelloPackettoSend(), [self.IPInterfaceAddress], 0, True)

    def decreaseLSATimer(self):
        self.LSATimer -= 1

    def statelife(self):

        self.State = 2  # WaitTimer
        self.sendHello()
        self.resetHelloTimer()
        for x in range(0,self.WaitTimer):
            time.sleep(1)
            self.decreaseHelloTimer()
            self.decreaseLSATimer()
            if self.HelloTimer == 0:
                self.sendHello()
                self.resetHelloTimer()

        self.DRElection()

        while self.State != 0 and self.State !=1:
            time.sleep(1)
            self.decreaseHelloTimer()
            self.decreaseLSATimer()
            if self.HelloTimer == 0:
                self.sendHello()
                self.resetHelloTimer()
            if self.LSATimer == 0 and self.havetoNLSA():
                self.createNLSA()

    def havetoNLSA(self):
        if self.DesignatedRouter == self.IPInterfaceAddress and len(self.Neighbours)>0:
            return True
        else:
            return False

    def createNLSA(self):
        newNLSA = NetworkLSA(None, 0,2,2,self.IPInterfaceAddress,self.RouterID, 0, 0, 0,
                             self.IPInterfaceMask, self.getNeighbords())
        self.routerclass.receiveLSAtoLSDB(newNLSA, self.AreaID)
        self.LSATimer = 60*30

    def packetReceived(self, packet):
        if packet.getType() == 1:
            self.readHello(packet)
        if packet.getType() == 3:
            pass #TODO Link State Request
        if packet.getType() == 4:
            self.readLSUpdate(packet)
        if packet.getType() == 5:
            pass #TODO Read Link State ACK

    def readHello(self,packet):
        if self.RouterID in packet.getNNeighbors():

            found = False
            for x in self.Neighbours:
                if x['RouterID'] == packet.RouterID:
                    found = True
                    self.getNeighbord(packet.RouterID).updateFromHello(packet)
                    continue
            if found == False:

                self.Neighbours.append({'RouterID': packet.RouterID,
                                        'Neighbord-object': neighbord(self, packet.RouterDeadInterval, packet.RouterID,
                                                                      packet.RouterPri, packet.sourceRouter,
                                                                      packet.Options, packet.DesignatedRouter,
                                                                      packet.BackupDesignatedRouter)})
                if self.havetoNLSA():
                    self.createNLSA()
                    self.routerclass.createLSA(self.AreaID, self.RouterID, False)

                th = threading.Thread(target=self.startDDProcess, args=())
                th.daemon = True
                th.start()

    def startDDProcess(self):
        #ExStart phase

        # wait for first packet
        packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)
        sourceRouter = packetReceived.getSourceRouter()
        ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
        # create DD to send
        packet = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2, self.RouterID,
                                           self.AreaID, 0, 0, 0,
                                0, 2, 1, 1, 1, ddseqnumber, True)
        packet = packet.packDDtoSend()

        # send packet to source router
        deliver(packet, self.IPInterfaceAddress, sourceRouter, False)

        # who is the master?
        if self.RouterID > packetReceived.getRouterID():
            master = True   # i'm the master
        else:
            master = False  # i'm the slave

        # Exchange phase

        LSDB = self.routerclass.getLSDB(self.AreaID)
        ListHeaderstosendLSDB = LSDB.getHeaderLSAs()

        if master:

            # Wait for slave response
            packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)
            sourceRouter = packetReceived.getSourceRouter()
            ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
            LSAHeaders = packetReceived.getListLSA()

            ddseqnumber += 1
            newpack = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2, self.RouterID, self.AreaID, 0, 0, 0,
                                                0, 2, 0, 1, 1, ddseqnumber, False)
            for x in ListHeaderstosendLSDB:
                newpack.addLSAHeader(x)

            # Update Header
            newpack.setPackLength(20 * len(ListHeaderstosendLSDB) + 8)
            newpack.computeChecksum()

            # send packet to source router
            newpack = newpack.packDDtoSend()
            deliver(newpack, self.IPInterfaceAddress, sourceRouter, False)

            # Wait for slave response
            packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)

            sourceRouter = packetReceived.getSourceRouter()
            ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
            MbitRecv = packetReceived.getMbit()
            LSAHeaders += packetReceived.getListLSA()

            Mbit = True
            while Mbit:
                # Exchange not ended
                # create DD to send
                ddseqnumber += 1
                packet = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2, self.RouterID, self.AreaID, 0, 0, 0,
                                                   0, 2, 0, 0, 1, ddseqnumber, True)
                packet = packet.packDDtoSend()

                # send packet to source router
                deliver(packet, self.IPInterfaceAddress, sourceRouter, False)

                # Wait for slave response
                packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)

                sourceRouter = packetReceived.getSourceRouter()
                ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
                Mbit = packetReceived.getMbit()


            # End Exchange: move to Loading


        else:
            newpack = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2,
                                                self.RouterID, self.AreaID, 0, 0, 0,
                                0, 2, 0, 0, 0, ddseqnumber, False)
            for x in ListHeaderstosendLSDB:
                newpack.addLSAHeader(x)

            # Update Header
            newpack.setPackLength(20*len(ListHeaderstosendLSDB) + 8)
            newpack.computeChecksum()

            # send packet to source router
            newpack = newpack.packDDtoSend()
            deliver(newpack, self.IPInterfaceAddress, sourceRouter, False)

            # Wait for master response
            packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)

            sourceRouter = packetReceived.getSourceRouter()
            ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
            Mbit = packetReceived.getMbit()
            LSAHeaders = packetReceived.getListLSA()

            # create DD to send
            packet = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2,
                                               self.RouterID, self.AreaID, 0, 0, 0,
                                               0, 2, 0, 0, 0, ddseqnumber, True)
            packet = packet.packDDtoSend()

            # send packet to source router
            deliver(packet, self.IPInterfaceAddress, sourceRouter, False)

            while Mbit:
                # Exchange not ended

                # Wait for master response
                packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 2, False)

                sourceRouter = packetReceived.getSourceRouter()
                ddseqnumber = packetReceived.getDatabaseDescriptionSequenceNumber()
                Mbit = packetReceived.getMbit()
                for x in (packetReceived.getListLSA()):
                    LSAHeaders.append(x)

                # create DD to send
                packet = DatabaseDescriptionPacket(self.IPInterfaceAddress, 2, 2,
                                                   self.RouterID, self.AreaID, 0, 0,0,
                                                   0, 2, 0, 0, 0, ddseqnumber, True)
                packet = packet.packDDtoSend()

                # send packet to source router
                deliver(packet, self.IPInterfaceAddress, sourceRouter, False)


            # End Exchange: move to Loading

        # wait for LS-Request
        thr = threading.Thread(target=self.TakeCareofLSRequest, args=[])
        thr.daemon = True
        thr.start()

        packet = LinkStateRequestPacket(self.IPInterfaceAddress, 2, 3,
                                            self.RouterID, self.AreaID, 0, 0, 0, 0)

        haveToSend = False
        for x in LSAHeaders:
             LSAH = unpackLSAHeader(x)
             if LSDB.HaveThisLSA(LSAH):
                 continue
             else:
                 haveToSend = True
                 packet.receiveRequest({'LSType': LSAH.getLSType(),
                                        'LinkStateID':LSAH.getLSID(),
                                        'AdvertisingRouter': LSAH.getADVRouter()})
        # send LS-Request
        if haveToSend:
            pack = packet.getLSReqToSend()
            deliver(pack, self.IPInterfaceAddress, sourceRouter, False)
            self.TakeCareofLSUpdate()

    def TakeCareofLSUpdate(self):
        # Wait for master response
        packetReceived = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 4, False)
        sourceRouter = packetReceived.getSourceRouter()

        # create LS-ACK
        pack = LinkStateAcknowledgmentPacket(self.IPInterfaceAddress, 2, 5,
                                             self.RouterID, self.AreaID, 0, 0, 0, 0)
        LSAs = packetReceived.getReceivedLSAs()

        for x in LSAs:
            pack.receiveLSA(x.getHeaderPack(False), x.getLengthHeader(False))
            self.routerclass.receiveLSAtoLSDB(x, self.AreaID)

        # send  LS-ACK
        deliver(pack.getLSACKToSend(), self.IPInterfaceAddress, sourceRouter, False)

    def TakeCareofLSRequest(self):


        pack = self.routerclass.unicastReceiver(self.IPInterfaceAddress, 3, True)

        if pack != 0:

            LSAs = pack.getLSARequests()
            LSDB = self.routerclass.getLSDB(self.AreaID)
            sourceRouter = pack.getSourceRouter()

            packetToSend = LinkStateUpdatePacket(self.IPInterfaceAddress, 2, 4, self.RouterID, self.AreaID,
                                             0, 0, 0, 0, len(LSAs))
            for x in LSAs:
                LSA = LSDB.getLSA(x['LSType'], x['LinkStateID'], x['AdvertisingRouter'])
                if LSA == False:
                    print "Problem! LSA not found on LSDB!"
                else:
                    packetToSend.receiveLSA(LSA)

            # deliver
            packetToSend = packetToSend.getPackLSUPD()
            deliver(packetToSend, self.IPInterfaceAddress, sourceRouter, False)

            #wait for LS-ACK or LS- REQ # TODO

    def getNeighbord(self, neighID):
        for x in self.Neighbours:
            if x['RouterID']==neighID:
                return x['Neighbord-object']

    def InterfaceUp(self):
        self.State = 2  # Waiting

    def WaitTimer(self):
        if self.DesignatedRouter == '0.0.0.0':
            self.State = 6  # Designated Router
        else:
            if self.BackupDesignatedRouter == '0.0.0.0':
                self.State = 5  # Backup Designated Router
            else:
                self.State = 4  # DR Other

    def BackupSeen(self, state, DR, BDR):
        if state == 0:  # alguem ja e BDR:
            self.State = 4  # DR Other
            self.BackupDesignatedRouter = BDR
            self.DesignatedRouter = DR
        elif state == 1:   # alguem ja e DR e nao ha BDR
            self.State = 5  # Backup Designated Router
            self.DesignatedRouter = DR
            self.BackupDesignatedRouter = self.IPInterfaceAddress

    def NeighborChange(self):
        self.DRElection()

    def RemoveNeighbord(self,routerid):

        self.Neighbours = [i for i in self.Neighbours if i['RouterID'] != routerid]
        self.NeighborChange()

    def LoopIn(self):
        self.State = 1  # Loopback

    def UnloopInd(self):
        self.State = 0  # Down

    def InterfaceDown(self):
        self.State = 0  # Down
        # reset as interfaces
        self.DesignatedRouter = '0.0.0.0'
        self.BackupDesignatedRouter = '0.0.0.0'
        self.InterfaceOutputCost = 10
        self.RxmtInterval = 30

    def DRElection(self):

        ## Step (1)
        listPossible=[]
        if self.RouterPriority >0:
            routerItSelf={'RouterID':self.RouterID,
                          'DR':self.DesignatedRouter,
                          'BDR':self.BackupDesignatedRouter,
                          'RouterPriority':self.RouterPriority,
                          'StateDR':self.StateDR(),
                          'StateBDR':self.StateBDR(),
                          'neighbordAddress': self.IPInterfaceAddress}
            listPossible.append(routerItSelf)

        for x in self.Neighbours:
            if x['Neighbord-object'].neighbordPriority >0:
                routerToAdd={'RouterID':x['Neighbord-object'].neighbordID,
                             'DR':x['Neighbord-object'].neighbordDR,
                             'BDR':x['Neighbord-object'].neighbordBDR,
                             'RouterPriority':x['Neighbord-object'].neighbordPriority,
                             'StateDR':x['Neighbord-object'].StateDR(),
                             'StateBDR':x['Neighbord-object'].StateBDR(),
                             'neighbordAddress':x['Neighbord-object'].neighbordAddress}
                listPossible.append(routerToAdd)
        ## Step (2)
        listPossibleBDR = []
        for x in listPossible:
            if x['StateDR'] == True:
                continue
            else:
                listPossibleBDR.append(x)
        listofBDR = []
        for x in listPossibleBDR:
            if x['StateBDR'] == True:
                listofBDR.append(x)
        statebdr=False
        if len(listofBDR)== 1:
            if listofBDR[0]['RouterID'] == routerItSelf['RouterID']:    # Eu sou o BDR
                statebdr = True
                bdr = self.IPInterfaceAddress
                for x in listPossible:
                    if x['RouterID'] == routerItSelf['RouterID']:
                        x['StateBDR'] = True
                        x['BDR'] = bdr
            else:
                bdr= listofBDR[0]['neighbordAddress']
                for x in listPossible:
                    if x['RouterID'] == listofBDR[0]['RouterID']:
                        x['StateBDR'] = True
                        x['BDR'] = bdr
        else:
            if len(listofBDR)>0:

                routerid=listofBDR[0]['RouterID']
                for x in listofBDR:
                    # TODO not tested
                    if x['RouterID']>routerid:
                        routerid=x['RouterID']
                        pass
                bdr= x['neighbordAddress']
                for j in listPossible:
                    if j['RouterID'] == x['RouterID']:
                        j['StateBDR'] = True
                        j['BDR'] = x['neighbordAddress']
            else:
                try:
                    listofBDR = sorted(listPossibleBDR, key=itemgetter('RouterPriority'),
                                   reverse=True)
                except Exception:
                    pass
                if len(listofBDR)== 0:
                    statebdr= False
                    bdr = '0.0.0.0'
                else:
                    if len(listofBDR)==1:
                        if listofBDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                            statebdr = True
                            bdr = self.IPInterfaceAddress
                            for x in listPossible:
                                if x['RouterID'] == routerItSelf['RouterID']:
                                    x['StateBDR'] = True
                                    x['BDR'] = bdr
                        else:
                            bdr= listofBDR[0]['neighbordAddress']
                            for x in listPossible:
                                if x['RouterID'] == listofBDR[0]['RouterID']:
                                    x['StateBDR'] = True
                                    x['BDR'] = bdr
                    else:
                        if listofBDR[0]['RouterPriority'] == listofBDR[1]['RouterPriority']:
                            #tie
                            del listPossibleBDR[:]
                            for x in listofBDR:
                                if x['RouterPriority'] == listofBDR[0]['RouterPriority']:
                                    listPossibleBDR.append(x)
                            if len(listPossibleBDR) != 0:
                                listPossibleBDR.sort(listPossibleBDR, key=itemgetter('RouterID'), reverse=True)
                            if listPossibleBDR[0]['RouterID'] == routerItSelf['RouterID']:   # Eu sou o BDR
                                bdr= self.IPInterfaceAddress
                                statebdr = True
                                for x in listPossible:
                                    if x['RouterID'] == routerItSelf['RouterID']:
                                        x['StateBDR'] = True
                                        x['BDR'] = self.IPInterfaceAddress
                            else:
                                bdr= listPossibleBDR[0]['neighbordAddress']
                                for x in listPossible:
                                    if x['RouterID'] == listPossibleBDR[0]['RouterID']:
                                        x['StateBDR'] = True
                                        x['BDR'] = listPossibleBDR[0]['neighbordAddress']

        # Step(3)
        listPossibleDR = []
        for x in listPossible:
            if x['StateBDR'] == True:
                continue
            else:
                listPossibleDR.append(x)
        statedr = False
        listofDR = []
        for x in listPossibleDR:
            if x['StateDR'] == True:
                listofDR.append(x)

        if len(listofDR) == 1:
            if listofDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                dr = self.IPInterfaceAddress
                statedr = True
            else:
                dr = listofDR[0]['neighbordAddress']

        else:
            if len(listofDR) == 0:
                ## O DR e o BDR agora calculado

                dr = bdr
                statebdr = False
                bdr = '0.0.0.0'
                if dr== self.IPInterfaceAddress:
                    for x in listPossible:
                        if x['RouterID'] == routerItSelf['RouterID']:
                            x['StateDR'] = True
                            x['DR'] = self.IPInterfaceAddress
                            x['BDR'] = '0.0.0.0'
                            x['StateBDR'] = False
                            statedr = True
                else:
                    for x in listPossible:
                        if x['neighbordAddress'] == dr:
                            x['DR'] = dr
                            x['StateDR'] = True
                            x['BDR'] = '0.0.0.0'
                            x['StateBDR'] = False
            else:
                try:
                    listofDR = sorted(listPossibleDR, key=itemgetter('RouterPriority'), reverse=True)
                except Exception:
                    pass
                if len(listofDR) == 1:
                    if listofDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                        dr = listofDR[0]['neighbordAddress']
                        statedr = True

                        for x in listPossible:
                            if x['RouterID'] == routerItSelf['RouterID']:
                                x['StateDR'] = True
                                x['DR'] = self.IPInterfaceAddress
                    else:
                        dr = listofDR[0]['neighbordAddress']
                        statedr = False

                        for x in listPossible:
                            if x['RouterID'] == listofDR[0]['RouterID']:
                                x['StateDR'] = True
                                x['DR'] = listofDR[0]['neighbordAddress']
                else:
                    if listofDR[0]['RouterPriority'] == listofDR[1]['RouterPriority']:
                        # tie
                        del listPossibleDR[:]
                        for x in listofDR:
                            if x['RouterPriority'] == listofDR[0]['RouterPriority']:
                                listPossibleDR.append(x)

                        listPossibleDR.sort(listPossibleDR, key=itemgetter('RouterID'), reverse=True)
                        if listPossibleDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o DR
                            dr = self.IPInterfaceAddress
                            statedr = True

                            for x in listPossible:
                                if x['RouterID'] == routerItSelf['RouterID']:
                                    x['StateDR'] = True
                                    x['DR'] = self.IPInterfaceAddress
                        else:
                            dr = listPossibleDR[0]['neighbordAddress']
                            statedr = False
                            for x in listPossible:
                                if x['RouterID'] == listPossibleDR[0]['RouterID']:
                                    x['StateDR'] = True
                                    x['DR'] = listPossibleDR[0]['neighbordAddress']

        if statebdr or statedr:
            statedr = False
            statebdr = False
            dr = '0.0.0.0'
            bdr = '0.0.0.0'
            ## Step (2)
            listPossibleBDR = []
            for x in listPossible:
                if x['StateDR'] == True:
                    continue
                else:
                    listPossibleBDR.append(x)
            listofBDR = []
            for x in listPossibleBDR:
                if x['StateBDR'] == True:
                    listofBDR.append(x)
            statebdr = False
            if len(listofBDR) == 1:
                if listofBDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                    statebdr = True
                    bdr = self.IPInterfaceAddress
                    for x in listPossible:
                        if x['RouterID'] == routerItSelf['RouterID']:
                            x['StateBDR'] = True
                            x['BDR'] = bdr
                else:
                    bdr = listofBDR[0]['neighbordAddress']
                    for x in listPossible:
                        if x['RouterID'] == listofBDR[0]['RouterID']:
                            x['StateBDR'] = True
                            x['BDR'] = bdr
            else:
                if len(listofBDR) > 0:

                    routerid = listofBDR[0]['RouterID']
                    for x in listofBDR:
                        # TODO not tested
                        if x['RouterID'] > routerid:
                            routerid = x['RouterID']
                            pass
                    bdr = x['neighbordAddress']
                    for j in listPossible:
                        if j['RouterID'] == x['RouterID']:
                            j['StateBDR'] = True
                            j['BDR'] = x['neighbordAddress']
                else:
                    try:
                        listofBDR = sorted(listPossibleBDR, key=itemgetter('RouterPriority'), reverse=True)
                    except Exception:
                        pass
                    if len(listofBDR) == 0:
                        statebdr = False
                        bdr = '0.0.0.0'
                    else:
                        if len(listofBDR) == 1:
                            if listofBDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                                statebdr = True
                                bdr = self.IPInterfaceAddress
                                for x in listPossible:
                                    if x['RouterID'] == routerItSelf['RouterID']:
                                        x['StateBDR'] = True
                                        x['BDR'] = bdr
                            else:
                                bdr = listofBDR[0]['neighbordAddress']
                                for x in listPossible:
                                    if x['RouterID'] == listofBDR[0]['RouterID']:
                                        x['StateBDR'] = True
                                        x['BDR'] = bdr
                        else:
                            if listofBDR[0]['RouterPriority'] == listofBDR[1]['RouterPriority']:
                                # tie
                                del listPossibleBDR[:]
                                for x in listofBDR:
                                    if x['RouterPriority'] == listofBDR[0]['RouterPriority']:
                                        listPossibleBDR.append(x)

                                listPossibleBDR.sort(listPossibleBDR, key=itemgetter('RouterID'), reverse=True)
                                if listPossibleBDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                                    bdr = self.IPInterfaceAddress
                                    statebdr = True
                                    for x in listPossible:
                                        if x['RouterID'] == routerItSelf['RouterID']:
                                            x['StateBDR'] = True
                                            x['BDR'] = self.IPInterfaceAddress
                                else:
                                    bdr = listPossibleBDR[0]['neighbordAddress']
                                    for x in listPossible:
                                        if x['RouterID'] == listPossibleBDR[0]['RouterID']:
                                            x['StateBDR'] = True
                                            x['BDR'] = listPossibleBDR[0]['neighbordAddress']

            # Step(3)
            listPossibleDR = []
            for x in listPossible:
                if x['StateBDR'] == True:
                    continue
                else:
                    listPossibleDR.append(x)
            statedr = False
            listofDR = []
            for x in listPossibleDR:
                if x['StateDR'] == True:
                    listofDR.append(x)

            if len(listofDR) == 1:
                if listofDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                    dr = self.IPInterfaceAddress
                    statedr = True
                else:
                    dr = listofDR[0]['neighbordAddress']

            else:
                if len(listofDR) == 0:
                    ## O DR e o BDR agora calculado

                    dr = bdr
                    statebdr = False
                    bdr = '0.0.0.0'
                    if dr == self.IPInterfaceAddress:
                        for x in listPossible:
                            if x['RouterID'] == routerItSelf['RouterID']:
                                x['StateDR'] = True
                                x['DR'] = self.IPInterfaceAddress
                                x['BDR'] = '0.0.0.0'
                                x['StateBDR'] = False
                                statedr = True
                    else:
                        for x in listPossible:
                            if x['neighbordAddress'] == dr:
                                x['DR'] = dr
                                x['StateDR'] = True
                                x['BDR'] = '0.0.0.0'
                                x['StateBDR'] = False
                else:
                    try:
                        listofDR = sorted(listPossibleDR, key=itemgetter('RouterPriority'), reverse=True)
                    except Exception:
                        pass
                    if len(listofDR) == 1:
                        if listofDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o BDR
                            dr = listofDR[0]['neighbordAddress']
                            statedr = True

                            for x in listPossible:
                                if x['RouterID'] == routerItSelf['RouterID']:
                                    x['StateDR'] = True
                                    x['DR'] = self.IPInterfaceAddress
                        else:
                            dr = listofDR[0]['neighbordAddress']
                            statedr = False

                            for x in listPossible:
                                if x['RouterID'] == listofDR[0]['RouterID']:
                                    x['StateDR'] = True
                                    x['DR'] = listofDR[0]['neighbordAddress']
                    else:
                        if listofDR[0]['RouterPriority'] == listofDR[1]['RouterPriority']:
                            # tie
                            del listPossibleDR[:]
                            for x in listofDR:
                                if x['RouterPriority'] == listofDR[0]['RouterPriority']:
                                    listPossibleDR.append(x)

                            listPossibleDR.sort(listPossibleDR, key=itemgetter('RouterID'), reverse=True)
                            if listPossibleDR[0]['RouterID'] == routerItSelf['RouterID']:  # Eu sou o DR
                                dr = self.IPInterfaceAddress
                                statedr = True

                                for x in listPossible:
                                    if x['RouterID'] == routerItSelf['RouterID']:
                                        x['StateDR'] = True
                                        x['DR'] = self.IPInterfaceAddress
                            else:
                                dr = listPossibleDR[0]['neighbordAddress']
                                statedr = False
                                for x in listPossible:
                                    if x['RouterID'] == listPossibleDR[0]['RouterID']:
                                        x['StateDR'] = True
                                        x['DR'] = listPossibleDR[0]['neighbordAddress']


        # DR and BDR Updated
        self.DesignatedRouter = dr
        self.BackupDesignatedRouter = bdr
        if statedr:
            self.State = 6  # DR
        else:
            if statebdr:
                self.State = 5  # BDR
            else:
                self.State = 4  # DR Other

        # Update LSAs
        self.TypeofInterfaceChange()
        if self.havetoNLSA():
            self.createNLSA()
        self.routerclass.createLSA(self.AreaID, self.RouterID, False)

        # Backup Designated Router Updated
        self.BackupDesignatedRouter = bdr

    def StateDR(self):
        if self.IPInterfaceAddress == self.DesignatedRouter:
            return True
        else:
            return False

    def StateBDR(self):
        if self.IPInterfaceAddress == self.BackupDesignatedRouter:
            return True
        else:
            return False

    def getstate(self):
        return self.State

    def getIPAddr(self):
        return self.IPInterfaceAddress

    def getDR(self):
        return self.DesignatedRouter

    def getIPIntAddr(self):
        return self.IPInterfaceAddress

    def getMetric(self):
        return self.InterfaceOutputCost

    def getArea(self):
        return self.AreaID

    def getIPInterfaceMask(self):
        return self.IPInterfaceMask

    def getTypeLink(self):
        return self.TypeofInterface

    def TypeofInterfaceChange(self):
        if len(self.Neighbours) == 0:
            self.TypeofInterface = 3    # Stub Network
        else:
            self.TypeofInterface = 2    # Transit Network

    def readLSUpdate(self, packet):
        LSAs = packet.getReceivedLSAs()
        sourceRouter = packet.getSourceRouter()

        # create LS-ACK
        pack = LinkStateAcknowledgmentPacket(self.IPInterfaceAddress, 2, 5,
                                             self.RouterID, self.AreaID, 0, 0, 0, 0)

        for x in LSAs:
            pack.receiveLSA(x.getHeaderPack(False), x.getLengthHeader(False))
            self.routerclass.receiveLSAtoLSDB(x, self.AreaID)

        # send  LS-ACK
        deliver(pack.getLSACKToSend(), [self.IPInterfaceAddress], sourceRouter, True)
