from common import *
from shared import *
from packet import *

import json

from os      import makedirs
from os.path import exists
from struct  import unpack

__all__ = ('Response', 'ModsListResponse', 'DepsResponse', 'FilesResponse')

class Response(Error, StreamPacket):
    __slots__ = {'failed', 'code', 'type', 'total_length'}
    
    def __init__(self, urldata, resp_type):
        super(Response, self).__init__(Constants.AUTOUPDATER_URL, urldata)
        
        self.code         = 0
        self.type         = resp_type
        self.total_length = 0
        
        if self.conn is None:
            self.fail('CONNECT')
            return
        
        types_events = {
            ResponseType.index('GET_MODS_LIST') : 'Mods',
            ResponseType.index('GET_DEPS')      : 'Deps',
            ResponseType.index('GET_FILES')     : 'ModFiles'
        }
        
        if self.type in types_events:
            self.onDataProcessed = getattr(g_AUEvents, 'on%sDataProcessed'%(types_events[self.type]))
        else:
            raise NotImplementedError('Response type is not exists')
        
        self.total_length = self.parse('I', 4)[0]
        self.code         = self.parse('B', 1)[0]
        
        if self.total_length < 3:
            self.fail('RESP_TOO_SMALL')
            return
    
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
    
    def div1024(self, value):
        return round(float(value) / 1024, 2)

class ModsListResponse(Response):
    __slots__ = {'mods', 'time_exp'}
    
    def __init__(self, *args):
        super(ModsListResponse, self).__init__(*args)
        
        self.mods     = {}
        self.time_exp = 0
        
        self.init()
        
        g_AUShared.addRequest(self)
    
    def init(self):
        if self.code != ErrorCode.index('SUCCESS'):
            self.fail('GETTING_MODS')
            return
        
        try:
            self.time_exp = self.parse('I', 4)[0]
            self.mods = json.loads(self.read())
        except ValueError:
            self.fail('READING_MODS')
    
    def slots(self):
        return super(ModsListResponse, self).slots() | self.__slots__

class DepsResponse(Response):
    __slots__ = {'dependencies', 'time_exp'}
    
    def __init__(self, *args):
        super(DepsResponse, self).__init__(*args)
        
        self.dependencies = {}
        
        self.init()
        
        g_AUShared.addRequest(self)
    
    def init(self):
        if self.code != ErrorCode.index('SUCCESS'):
            self.fail('GETTING_DEPS')
            return
        
        try:
            self.dependencies = json.loads(self.read())
        except ValueError:
            self.fail('READING_DEPS')
    
    def slots(self):
        return super(DepsResponse, self).slots() | self.__slots__
            
class FilesResponse(Response):
    __slots__ = {'files_count', 'files'}
    
    def __init__(self, *args):
        super(FilesResponse, self).__init__(*args)
        
        self.files_count = 0
        self.files = []
        
        self.init()
        
        g_AUShared.addRequest(self)
    
    def init(self):
        if self.code != ErrorCode.index('SUCCESS'):
            self.fail('GETTING_FILES')
            return
        
        self.files_count = self.parse('I', 4)[0]
        
        for i in xrange(self.files_count):
            path_len = self.parse('H', 2)[0]
            path = self.read(path_len)
            file_size = self.parse('I', 4)[0]
            file_data = ''
            if file_size > self.total_length:
                self.fail('INVALID_FILE_SIZE')
                return
            elif file_size > 0:
                file_data = file_data = self.read(file_size)
            
            self.files.append({
                'path'      : path,
                'path_len'  : path_len,
                'file_size' : file_size
            })
            
            print {
                'path'      : path,
                'path_len'  : path_len,
                'file_size' : file_size
            }
            
            try:
                with open('./' + path, 'wb') as fil:
                    fil.write(file_data)
            except:
                self.fail('CREATING_FILE')
                
                filename_pos = path.rfind('/')
                trimmed_path = path if filename_pos == -1 else path[:filename_pos + 1]
                
                failed_dir  = Directory['FAIL_DIR'] + trimmed_path
                failed_path = Directory['FAIL_DIR'] + path
                if not exists(failed_dir):
                    makedirs(failed_dir)
                
                with open(failed_path, 'wb') as fil:
                    fil.write(file_data)
    
    def slots(self):
        return super(FilesResponse, self).slots() | self.__slots__