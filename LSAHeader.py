import struct

import utils

OSPF_LSA_HDR = "> HBB L L L HH"
OSPF_LSA_HDR_CHKS = "> BB L L L HH"
OSPF_LSA_HDR_LEN = struct.calcsize(OSPF_LSA_HDR)
OSPF_LSA_HDR_CHKS_LEN = struct.calcsize(OSPF_LSA_HDR_CHKS)

class LSAHeader:
    def __init__(self, lsage, opt, lstype, lsid, advert):
        self.LinkStateAge = lsage
        self.Options =  opt
        self.LinkStateType = lstype
        self.LinkStateID = lsid
        self.AdvertisingRouter = advert
        self.LinkStateSequenceNumber =0x80000001
        self.LinkStateChecksum = 0
        self.Length = 0

        self.MaxAge = 3600
        self.MaxSeqNumber = 0x7fffffff

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

    def setNextSN(self, sn):
        if sn == self.MaxSeqNumber:
            self.LinkStateSequenceNumber = 0x80000001
        else:
             self.LinkStateSequenceNumber = sn + 1

    def printLSA(self):
        print self.LinkStateAge, self.LinkStateType, self.LinkStateID, self.LinkStateSequenceNumber


    def getHeaderPack(self, chck):
        if chck:
            return struct.pack(OSPF_LSA_HDR_CHKS, self.Options, self.LinkStateType,
                               utils.IPtoDec(self.LinkStateID), utils.IPtoDec(self.AdvertisingRouter),
                               self.LinkStateSequenceNumber, 00, self.Length)
        else:
            return struct.pack(OSPF_LSA_HDR, self.LinkStateAge, self.Options, self.LinkStateType,
                               utils.IPtoDec(self.LinkStateID),utils.IPtoDec(self.AdvertisingRouter),
                               self.LinkStateSequenceNumber, 00, self.Length)

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