from .common import *
from .packet import *

from struct import pack
from urllib import urlencode

__all__ = ('RequestHeader', 'Request')

class RequestHeader():
    def __init__(self, ID, lic, req_type):
        self.__ID   = ID
        self.__lic  = lic
        self.__type = req_type
    
    def get_type(self):
        return self.__type
    
    def __str__(self):
        return  pack('I', self.__ID) + \
                self.__lic           + \
                chr(self.__type)

class Request(Packet):
    def __init__(self, header):
        super(Request, self).__init__()
        
        self.__header = header
        self.__string = str(header)
    
    def __iadd__(self, data):
        self.__string += data
        return self
    
    def parse(self, fmt, data):
        self.__string += pack(fmt, data)

    def get_type(self):
        return self.__header.get_type()
    
    def get_data(self):
        header = pack('H', 2 + len(self.__string))
        return urlencode({'request' : header + self.__string})
