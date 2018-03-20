import struct

import utils

OSPF_LSA_HDR = "> HBB L L I HH"
OSPF_LSA_HDR_CHKS = "> BB L L I HH"
OSPF_LSA_HDR_LEN = struct.calcsize(OSPF_LSA_HDR)
OSPF_LSA_HDR_CHKS_LEN = struct.calcsize(OSPF_LSA_HDR_CHKS)

class LSAHeader:
    def __init__(self, sourceRouter, lsage, opt, lstype, lsid, advert, lsNumber, ck, lg):
        self.sourceRouter = sourceRouter
        self.LinkStateAge = lsage
        self.Options =  opt
        self.LinkStateType = lstype
        self.LinkStateID = lsid
        self.AdvertisingRouter = advert
        if lsNumber == 0:
            self.LinkStateSequenceNumber =0x80000001
        else:
            self.LinkStateSequenceNumber = lsNumber
        self.LinkStateChecksum = ck
        self.Length = lg

        self.MaxAge = 3600
        self.MaxSeqNumber = 0x7fffffff

    def getSource(self):
        return self.sourceRouter

    def printaTudo(self): # Para debug
        print "AGE ", (self.LinkStateAge)
        print "OPTIONS ", self.Options
        print "TYPE ", self.LinkStateType
        print "LINK STATE ID ", self.LinkStateID
        print "Adver Router ", self.AdvertisingRouter
        print "Link State SeqNum ", self.LinkStateSequenceNumber
        print "CHECKSUM ", self.LinkStateChecksum
        print "LENGHT ", self.Length

    def getOpaqueType(self):
        return False

    def getAge(self):
        return self.LinkStateAge

    def setMaxAge(self):
        self.LinkStateAge = self.MaxAge

    def countAge(self):
        self.LinkStateAge = self.LinkStateAge + 1

    def getLSID(self):
        return self.LinkStateID

    def getADVRouter(self):
        return self.AdvertisingRouter

    def getLSType(self):
        return self.LinkStateType

    def getSeqNumber(self):
        return self.LinkStateSequenceNumber

    def getChecksum(self):
        return self.LinkStateChecksum

    def setNextSN(self, sn):
        if sn == self.MaxSeqNumber:
            self.LinkStateSequenceNumber = 0x80000001
        else:
             self.LinkStateSequenceNumber = sn + 1

    def printLSA(self):
        print self.LinkStateAge, self.LinkStateType, self.LinkStateID, self.LinkStateSequenceNumber


    def getHeaderPack(self):

        if type(self.LinkStateChecksum) is not str:
            ck = struct.pack(">H", self.LinkStateChecksum)
        else:
            ck = self.LinkStateChecksum

        return struct.pack("> HBB L L I", self.LinkStateAge, self.Options, self.LinkStateType,
                           utils.IPtoDec(self.LinkStateID),utils.IPtoDec(self.AdvertisingRouter),
                           self.LinkStateSequenceNumber) + ck + struct.pack("!H", self.Length)

    def calculateLength(self):
        pass        #TODO To overide

    def getLength(self):
        return self.Length

    def getLengthHeader(self, checksum):
        if checksum:
            return OSPF_LSA_HDR_CHKS_LEN
        else:
            return OSPF_LSA_HDR_LEN

    def setLength(self, lgt, chks):
        if chks:
            self.Length = lgt + 2
        else:
            self.Length = lgt

    def setChecksum(self, ck):
        self.LinkStateChecksum =ck

    def calculateChecksum(self):
        pass # TODO To overide

