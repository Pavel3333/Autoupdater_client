from Common import *

__all__ = ('Logger', 'Events', 'g_AUEvents', 'g_AUShared')

class Logger(object):
    __slots__ = {'log_file'}
    
    def __init__(self):
        self.log_file = open(Paths.LOG_PATH, 'a')
        
        self.log_file.write('Start logging\n\n')
    
    def log(self, *args):
        msg = '[' + Constants.MOD_NAME + ']: '
        
        args_len = len(args)
        for i in xrange(args_len):
            msg += args[i]
            if i < args_len - 1:
                msg += ' '
        
        print msg
        self.log_file.write(msg + '\n')
    
    def __del__(self):
        self.log_file.write('Stop logging')
        self.log_file.close()

class Events:
    def __init__(self):
        self.onModsProcessingStart     = Event()
        self.onModsDataProcessed       = Event()
        self.onModsProcessingDone      = Event()
        
        self.onDepsProcessingStart     = Event()
        self.onDepsDataProcessed       = Event()
        self.onDepsProcessingDone      = Event()
        
        self.onDeletingStart           = Event()
        self.onDeletingProcessed       = Event()
        self.onDeletingDone            = Event()
        
        self.onFilesProcessingStart    = Event()
        self.onModFilesProcessingStart = Event()
        self.onModFilesDataProcessed   = Event()
        self.onModFilesProcessingDone  = Event()
        self.onFilesProcessingDone     = Event()

class Shared:
    def __init__(self):
        self.mods         = {}
        self.dependencies = {}
        
        self.undeletedPaths = []
        
        self.__requestsData = []
        self.__debugData    = []
        
        self.window       = None
        self.windowCommon = None
        
        self.logger = Logger()
        
        self.setSuccess()
    
    def setSuccess(self):
        self.err = ErrorCode.index('SUCCESS')
        
    def setErr(self, errCode, extraCode=0):
        if errCode == ErrorCode.index('SUCCESS'):
            self.err = ErrorCode.index('SUCCESS')
            return
        
        self.err = (errCode, extraCode)
        
        import os
        import codecs
        import json
        from time import strftime
        
        if errCode in xrange(len(ErrorCode)):
            errCode = ErrorCode[errCode]
        self.logger.log('Error %s (%s)'%(errCode, extraCode))
        
        dump = {
            'name' : 'dump ' + strftime('%d.%m.%Y %H_%M_%S'),
            'data' : {
                'mods'         : [mod.dict()        for mod        in self.mods.values()],
                'dependencies' : [dependency.dict() for dependency in self.dependencies.values()],
                'requestsData' : self.__requestsData
            },
            'debug' : self.__debugData
        }
        
        #try:
        with codecs.open(Directory['DUMP_DIR'] + dump['name'] + '.json', 'wb', 'utf-8') as dump_file:
            json.dump(dump['data'], dump_file, ensure_ascii=False, sort_keys=True, indent=4)
        
        if DEBUG:
            with open(Directory['DUMP_DIR'] + dump['name'] + '_debug.bin', 'wb') as dbg_file:
                for i, data in enumerate(dump['debug']):
                    dbg_file.write('%s %s\n'%(i, data))
        
        self.logger.log('Dump data was saved to', Directory['DUMP_DIR'] + dump['name'])
        #except Exception:
        #    self.logger.log('Unable to save dump data')
    
    def getErr(self):
        return self.err
    
    def handleErr(self, *args, **kw):
        if self.windowCommon is not None:
            self.windowCommon.handleErr(*args, **kw)
    
    def createDialog(self, *args, **kw):
        if self.windowCommon is not None:
            self.windowCommon.createDialog(*args, **kw)
        else:
            keys = ('title', 'message')
            msg = ''
            for key in keys:
                if key in kw:
                    msg += kw[key] + ' '
            
            if 'url' in kw:
                msg += ' (%s)'%(kw['url'])
            
            self.logger.log(msg)
    
    def createDialogs(self, *args, **kw):
        if self.windowCommon is not None:
            self.windowCommon.createDialogs(*args, **kw)
    
    def addRequest(self, request):
        self.__requestsData.append(request.dict())
        if DEBUG:
            self.__debugData.append(request.bin())

g_AUEvents = Events()
g_AUShared = Shared()
