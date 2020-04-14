from .common import *
from .packet import *
from .shared import *

from struct import pack
from urllib import urlencode

__all__ = ('RequestHeader', 'Request', 'getRequest')

class RequestHeader():
    def __init__(self, req_type, force_auth=False):
        self.__type = req_type
        self.force_auth = force_auth
    
    def get_type(self):
        return self.__type
    
    def __str__(self):
        need_auth = self.force_auth or g_AUShared.token is None
        result = chr(bool(need_auth)) + chr(self.__type)
        
        if need_auth:
            result += pack('I', g_AUShared.ID) + \
                      g_AUShared.lic_key
        else:
            result += g_AUShared.token
        return result

class Request(Packet):
    def __init__(self):
        super(Request, self).__init__()
        
        self.__string = ''
    
    def __iadd__(self, data):
        self.__string += data
        return self
    
    def parse(self, fmt, data):
        self.__string += pack(fmt, data)
    
    def __str__(self):
        return self.__string

def getRequest(req_header, req):
        data = str(req_header) + str(req)
        header = pack('H', 2 + len(data))
        return urlencode({'request' : header + data})