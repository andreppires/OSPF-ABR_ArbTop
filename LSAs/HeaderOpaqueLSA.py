import struct

import utils

OSPF_LSA_OPAQUE_HDR = "> HBB BBH L L HH"
OSPF_LSA_OPAQUE_HDR_CHKS = "> BB BBH L L HH"
OSPF_LSA_OPAQUE_HDR_LEN = struct.calcsize(OSPF_LSA_OPAQUE_HDR)
OSPF_LSA_OPAQUE_HDR_CHKS_LEN = struct.calcsize(OSPF_LSA_OPAQUE_HDR_CHKS)

class HeaderOpaqueLSA:
    def __init__(self, sourceRouter, lsage, opt, opaquetype, opaqueID, advert, lsNumber, ck, lg):

        self.sourceRouter = sourceRouter
        self.LinkStateAge = lsage
        self.Options =  opt
        self.LinkStateType = 11
        self.OpaqueType = opaquetype
        self.OpaqueID = opaqueID
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

    def getOpaqueID(self):
        return self.OpaqueID

    def setOpaqueID(self, op):
        self.OpaqueID = op

    def getLSType(self):
        return self.LinkStateType

    def getLSID(self):
        return self.getOpaqueID()

    def getAge(self):
        return self.LinkStateAge

    def setMaxAge(self):
        self.LinkStateAge = self.MaxAge

    def countAge(self):
        self.LinkStateAge = self.LinkStateAge + 1

    def getADVRouter(self):
        return self.AdvertisingRouter

    def getSeqNumber(self):
        return self.LinkStateSequenceNumber

    def getChecksum(self):
        return self.LinkStateChecksum

    def getOpaqueType(self):
        return self.OpaqueType

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

        return struct.pack("> HBB BBH L L", self.LinkStateAge, self.Options, self.LinkStateType,
                           self.OpaqueType, 0, self.OpaqueID, utils.IPtoDec(self.AdvertisingRouter),
                           self.LinkStateSequenceNumber) + ck + struct.pack("!H", self.Length)


    def getLength(self):
        return self.Length

    def getLengthHeader(self, checksum):
        if checksum:
            return OSPF_LSA_OPAQUE_HDR_CHKS_LEN
        else:
            return OSPF_LSA_OPAQUE_HDR

    def setLength(self, lgt, chks):
        if chks:
            self.Length = lgt + 2
        else:
            self.Length = lgt

    def setChecksum(self, ck):
        self.LinkStateChecksum = ck

