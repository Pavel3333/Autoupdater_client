from .common import *
from .shared import *
from .packet import *

import json

from os      import makedirs
from os.path import exists
from struct  import unpack

__all__ = ('Response', 'ModsListResponse', 'DepsResponse', 'getResponse')

class Response(StreamPacket):
    __slots__ = {'failed', 'code', 'type', 'total_length', 'data'}
    
    def __init__(self, urldata, resp_type, force_auth=False):
        super(Response, self).__init__(Constants.AUTOUPDATER_URL, urldata)
        
        if not self.check():
            return
        
        self.code         = 0
        self.type         = resp_type
        self.total_length = 0
        self.data         = {}
        
        types_events = {
            ResponseType.index('GET_MODS_LIST') : 'Mods',
            ResponseType.index('GET_DEPS')      : 'Deps',
            ResponseType.index('GET_FILES')     : 'ModFiles'
        }
        
        if self.type in types_events:
            self.onDataProcessed = getattr(g_AUEvents, 'on%sDataProcessed'%(types_events[self.type])) # TODO
        else:
            raise NotImplementedError('Response type %s is not exists', self.type)
        
        self.total_length = self.parse('I', 4)[0]
        self.code         = self.parse('B', 1)[0]
        
        if self.total_length < 5:
            self.fail('RESP_TOO_SMALL')
            return
        
        if self.code == WarningCode['TOKEN_EXPIRED']:
            g_AUShared.token = None
            self.fail('TOKEN_EXPIRED')
            return
        
        try:
            self.data = json.loads(self.read())
        except:
            self.fail('RESP_INVALID')
            return
        
        if 'token' in self.data:
            g_AUShared.token = self.data.token
    
    def getChunkSize(self):
        return len(self.chunk) - self.offset
    
    def changeProgress(self, size):
        self.total_processed += size
        
        processed = self.total_processed
        total     = self.total_length
        unit      = DataUnits.index('B')
        
        while processed > 1024 or total > 1024:
            if unit + 1 >= len(DataUnits):
                break
            
            processed = self.div1024(processed)
            total     = self.div1024(total)
            unit += 1
            
        self.onDataProcessed(processed, total, unit)
    
    def readChunk(self, size):
        data = self.chunk[self.offset : self.offset + size]
        self.changeProgress(size)
        self.offset += size
        return data
    
    def readAllChunk(self):
        data = self.chunk[self.offset:]
        self.changeProgress(len(data))
        self.offset = len(self.chunk)
        return data
    
    def read(self, size=None):
        if self.offset:
            self.chunk = self.chunk[self.offset : ]
            self.offset = 0
        if not size:
            data = self.read_stream()
            if data:
                self.chunk += data
            return self.readAllChunk()
        else:
            while self.getChunkSize() < size:
                self.chunk += self.read_stream(Constants.CHUNK_MAX_SIZE)
            return self.readChunk(size)
    
    def slots(self):
        return super(Response, self).slots() | self.__slots__
    
    def parse(self, fmt, size):
        data = self.read(size)
        if not data:
            raise EOFError('Could not read the data')
        return unpack(fmt, data)
    
    @staticmethod
    def div1024(value):
        return round(float(value) / 1024, 2)

class ModsListResponse(Response):
    __slots__ = {'mods'}
    
    def __init__(self, *args):
        super(ModsListResponse, self).__init__(*args)
        
        if not self.check():
            return
        
        self.mods = {}
        
        if self.code != ErrorCode.index('SUCCESS'):
            self.fail('GETTING_MODS')
            return
        
        if 'exp_time' in self.data:
            g_AUShared.exp_time = self.data['exp_time']
        
        if 'mods' in self.data:
            self.mods = self.data['mods']
        else:
            self.fail('READING_MODS')
        
        g_AUShared.addRequest(self)
    
    def slots(self):
        return super(ModsListResponse, self).slots() | self.__slots__

class DepsResponse(Response):
    __slots__ = {'dependencies'}
    
    def __init__(self, *args):
        super(DepsResponse, self).__init__(*args)
        
        if not self.check():
            return
        
        self.dependencies = {}
        
        if self.code != ErrorCode.index('SUCCESS'):
            self.fail('GETTING_DEPS')
            return
        
        if 'deps' in self.data:
            self.dependencies = self.data['deps']
        else:
            self.fail('READING_DEPS')
    
    def slots(self):
        return super(DepsResponse, self).slots() | self.__slots__

def getResponse(cls, respType, req):
    respType = ResponseType.index(respType)
    req_header = RequestHeader(respType)

    resp = cls(getRequest(req_header, req), respType)
    if resp.failed == ErrorCode.index('TOKEN_EXPIRED'):
        del resp
        del req_header
        req_header = RequestHeader(respType, force_auth=True)
        resp = cls(getRequest(req_header, req), respType)
    
    return resp