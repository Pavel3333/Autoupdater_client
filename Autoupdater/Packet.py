from Common import ErrorCodes

from urllib import urlopen


class Packet(object):
    __slots__ = {'__string', 'code'}
    
    def __init__(self):
        code = ErrorCodes.SUCCESS
        self.__string = ''
        
    def __str__(self): return self.__string
    def __len__(self): return len(self.__string)

class StreamPacket(object):
    __slots__ = { 'conn', 'chunk', 'offset', 'total_processed', 'total_length', 'code', 'onDataProcessed' }
    
    def __init__(self, url, urldata):
        self.conn = urlopen(url, urldata)
        
        self.chunk           = ''
        
        self.offset          = 0
        self.total_processed = 0
        self.total_length    = 0
        
        self.onDataProcessed = None
        
        self.code            = ErrorCodes.SUCCESS
    
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        self.chunk = ''
