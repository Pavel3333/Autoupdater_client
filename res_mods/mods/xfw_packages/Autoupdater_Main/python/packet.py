from .common import *

from urllib import urlopen, urlencode

__all__ = ('Packet', 'StreamPacket')

class Packet(object):
    __slots__ = {'__string'}
    
    def __init__(self):
        self.__string = ''
        
    def __str__(self): return self.__string
    def __len__(self): return len(self.__string)

class StreamPacket(Error):
    __slots__ = { 'conn', 'chunk', 'debug_data', 'offset', 'total_processed', 'total_length' }
    
    def __init__(self, url, urldata):
        super(StreamPacket, self).__init__(url, urldata)
        
        try:
            self.conn = urlopen(url, urlencode({'request' : urldata}))
        except IOError as exc:
            self.fail(ErrorCode.Connect, exc.errno)
            return
        except:
            self.fail(ErrorCode.Connect)
            return
        
        self.chunk           = ''
        self.debug_data      = ''
        if DEBUG:
            self.debug_data = 'request:%s;response:'%(urldata)
        
        self.offset          = 0
        self.total_processed = 0
    
    def read_stream(self, size=None):
        data = self.conn.read(size)
        if DEBUG:
            self.debug_data += data
        return data
    
    def slots(self):
        return super(StreamPacket, self).slots()
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())
    
    def bin(self):
        return self.debug_data
    
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
