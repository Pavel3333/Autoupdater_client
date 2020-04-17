from .common  import *
from .shared  import *
from .packet  import *
from .request import *

import json

from os      import makedirs
from os.path import exists
from struct  import unpack

__all__ = ('Response', 'ModsListResponse', 'DepsResponse', 'getResponse')

class Response(StreamPacket):
    __slots__ = { 'type', 'total_length', 'data' }
    
    def __init__(self, urldata, resp_type, force_auth=False):
        super(Response, self).__init__(Constants.AUTOUPDATER_URL, urldata)
        
        if not self.check():
            return
        
        self.type         = resp_type
        self.total_length = 0
        self.data         = {}
        
        resp_progress = (
            'Mods',
            'Deps',
            'ModFiles'
        )
        
        self.total_length = self.parse('I', 4)[0]
        self.fail_code         = self.parse('B', 1)[0]
        
        if self.total_length < 5:
            self.fail(ErrorCode.RespTooSmall, self.fail_code)
            return
        
        if self.fail_code == WarningCode.TokenExpired:
            print 'token expired!'
            g_AUShared.token = None
            self.fail(ErrorCode.TokenExpired, self.fail_code)
            return
        
        try:
            self.data = json.loads(self.read())
        except:
            self.fail(ErrorCode.RespInvalid, self.fail_code)
            return
        
        if 'token' in self.data:
            g_AUShared.token = self.data['token'].decode('utf-8')
    
    def getChunkSize(self):
        return len(self.chunk) - self.offset
    
    def changeProgress(self, size):
        self.total_processed += size
        
        processed = self.total_processed
        total     = self.total_length
        unit      = DataUnits.B
        
        while processed > 1024 or total > 1024:
            if not DataUnits.__hasattr__(int(unit) + 1):
                break
            
            processed = self.div1024(processed)
            total     = self.div1024(total)
            unit = DataUnits.__getattr__(int(unit) + 1)
        
        g_AUEvents.onDataProcessed(self.type, processed, total, unit)
    
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
        
        self.mods = {}
        
        self.init()
        
        g_AUShared.addResponse(self)
    
    def init(self):
        if not self.check():
            return
        
        if self.fail_code != ErrorCode.Success:
            self.fail(ErrorCode.GetMods, self.fail_code)
            return
        
        if 'exp_time' in self.data:
            g_AUShared.exp_time = self.data['exp_time']
        
        if 'mods' not in self.data:
            self.fail(ErrorCode.ReadMods, self.fail_code)
            return
        
        self.mods = self.data['mods']
    
    def slots(self):
        return super(ModsListResponse, self).slots() | self.__slots__

class DepsResponse(Response):
    __slots__ = {'dependencies'}
    
    def __init__(self, *args):
        super(DepsResponse, self).__init__(*args)
        
        self.dependencies = {}
        
        self.init()
        
        g_AUShared.addResponse(self)
    
    def init(self):
        if not self.check():
            return
        
        if self.fail_code != ErrorCode.Success:
            self.fail(ErrorCode.GetDeps, self.fail_code)
            return
        
        if 'deps' in self.data:
            self.dependencies = self.data['deps']
        else:
            self.fail(ErrorCode.ReadDeps, self.fail_code)
            return
    
    def slots(self):
        return super(DepsResponse, self).slots() | self.__slots__

def getResponse(cls, req):
    respType = g_AUShared.respType
    req_header = RequestHeader(respType)

    resp = cls(getRequest(req_header, req), respType)
    if resp.fail_err == ErrorCode.TokenExpired:
        del resp
        del req_header
        req_header = RequestHeader(respType, force_auth=True)
        resp = cls(getRequest(req_header, req), respType)
    
    return resp