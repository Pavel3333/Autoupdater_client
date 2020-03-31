from common import *

from urllib import urlopen

__all__ = ('Packet', 'StreamPacket')

class Packet(object):
    __slots__ = {'__string', 'code'}
    
    def __init__(self):
        code = ErrorCode.index('SUCCESS')
        self.__string = ''
        
    def __str__(self): return self.__string
    def __len__(self): return len(self.__string)

class StreamPacket(object):
    __slots__ = {'conn', 'chunk', 'debug_data', 'offset', 'total_processed', 'total_length', 'onDataProcessed'}
    
    def __init__(self, url, urldata):
        try:
            self.conn = urlopen(url, urldata)
        except:
            self.conn = None
        
        self.chunk           = ''
        self.debug_data      = ''
        
        self.offset          = 0
        self.total_processed = 0
        
        self.onDataProcessed = None
    
    def read_stream(self, size=None):
        data = self.conn.read(size)
        if DEBUG:
            self.debug_data += data
        return data
    
    def slots(self):
        return frozenset()
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())
    
    def bin(self):
        return self.debug_data
    
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        self.chunk = ''
