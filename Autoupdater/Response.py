from Common import ErrorCodes, DataUnits, Constants, Event, div1024
from Shared import g_AutoupdaterEvents, g_AutoupdaterShared
from Packet import StreamPacket

import json

from os      import makedirs
from os.path import exists
from struct  import unpack


class Response(StreamPacket):
    __slots__ = { 'failed', 'type', 'total_length', 'code' }
    
    def __init__(self, urldata, resp_type):
        super(Response, self).__init__(Constants.AUTOUPDATER_URL, urldata)
        
        self.failed = ErrorCodes.SUCCESS
        self.type   = resp_type
        
        if   self.type == Constants.GET_MODS_LIST:
            self.onDataProcessed = g_AutoupdaterEvents.onModsDataProcessed
        elif self.type == Constants.GET_DEPS:
            self.onDataProcessed = g_AutoupdaterEvents.onDepsDataProcessed
        elif self.type == Constants.GET_FILES:
            self.onDataProcessed = g_AutoupdaterEvents.onModFilesDataProcessed
        else:
            raise NotImplementedError('Response type is not exists')

        self.total_length = self.parse('I', 4)[0]
        self.code         = self.parse('B', 1)[0]

        if self.total_length < 3:
            self.fail(ErrorCodes.RESP_TOO_SMALL)
            return
    
    def fail(self, code):
        self.failed = code
    
    def getChunkSize(self):
        return len(self.chunk) - self.offset

    def changeProgress(self, size):
        self.total_processed += size
        
        processed = self.total_processed
        total     = self.total_length
        unit      = DataUnits.BYTES
        
        while processed > 1024 or total > 1024:
            if Constants.DATA_UNITS.get(unit + 1, None) is None:
                break
            
            processed = div1024(processed)
            total     = div1024(total)
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
            #print 'cleanup'
            self.chunk = self.chunk[self.offset : ]
            self.offset = 0
        if not size:
            data = self.conn.read()
            if data:
                self.chunk += data
            return self.readAllChunk()
        else:
            #print 'read %s bytes'%(size)
            while self.getChunkSize() < size:
                #print 'get chunk', len(self.chunk)
                self.chunk += self.conn.read(Constants.CHUNK_MAX_SIZE)
            return self.readChunk(size)

    def parse(self, fmt, size):
        data = self.read(size)
        if not data:
            raise EOFError('Could not read the data')
        return unpack(fmt, data)

class ModsListResponse(Response):
    __slots__ = { 'mods', 'time_exp' }
    
    def __init__(self, *args):
        super(ModsListResponse, self).__init__(*args)
        
        self.mods     = {}
        self.time_exp = 0
        
        self.init()
        
        g_AutoupdaterShared.addRequestData(self.dict())
    
    def init(self):
        if self.code != ErrorCodes.SUCCESS:
            self.fail(ErrorCodes.FAIL_GETTING_MODS)
            return
        
        try:
            self.time_exp = self.parse('I', 4)[0]
            self.mods = json.loads(self.read())
        except ValueError:
            self.fail(ErrorCodes.FAIL_READING_MODS)
    
    def slots(self):
        super_slots = super(ModsListResponse, self).__slots__
        super_slots.update(self.__slots__)
        
        return super_slots
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())

class DepsResponse(Response):
    __slots__ = { 'dependencies', 'time_exp' }
    
    def __init__(self, *args):
        super(DepsResponse, self).__init__(*args)
        
        self.dependencies = {}
        
        self.init()
        
        g_AutoupdaterShared.addRequestData(self.dict())
    
    def init(self):
        if self.code != ErrorCodes.SUCCESS:
            self.fail(ErrorCodes.FAIL_GETTING_DEPS)
            return
        
        try:
            self.dependencies = json.loads(self.read())
        except ValueError:
            self.fail(ErrorCodes.FAIL_READING_DEPS)
    
    def slots(self):
        super_slots = super(DepsResponse, self).__slots__
        super_slots.update(self.__slots__)
        
        return super_slots
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())
            
class FilesResponse(Response):
    __slots__ = { 'files_count', 'files' }
    
    def __init__(self, *args):
        super(FilesResponse, self).__init__(*args)
        
        self.files_count = 0
        self.files = []
        
        self.init()
        
        g_AutoupdaterShared.addRequestData(self.dict())
    
    def init(self):
        if self.code != ErrorCodes.SUCCESS:
            self.fail(ErrorCodes.FAIL_GETTING_FILES)
            return
        
        self.files_count = self.parse('I', 4)[0]
        for i in xrange(self.files_count):
            path_len = self.parse('H', 2)[0]
            path = self.read(path_len)
            file_size = self.parse('I', 4)[0]
            file_data = self.read(file_size)
            
            self.files.append({
                'path'      : path,
                'path_len'  : path_len,
                'file_size' : file_size
            })
            
            try:
                with open('./' + path, 'wb') as fil:
                    fil.write(file_data)
            except Exception as e:
                self.fail(ErrorCodes.FAIL_CREATING_FILE)
                
                filename_pos = path.rfind('/')
                trimmed_path = path if filename_pos == -1 else path[:filename_pos + 1]
                
                failed_dir  = Constants.FAIL_DIR + trimmed_path
                failed_path = Constants.FAIL_DIR + path
                if not exists(failed_dir):
                    makedirs(failed_dir)
                
                with open(failed_path, 'wb') as fil:
                    fil.write(file_data)
    
    def slots(self):
        super_slots = super(FilesResponse, self).__slots__
        super_slots.update(self.__slots__)
        
        return super_slots
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())