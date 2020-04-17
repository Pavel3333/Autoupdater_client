from .common import *

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
        self.onDataProcessed           = Event()
        
        self.onModsProcessingStart     = Event()
        self.onModsProcessingDone      = Event()
        
        self.onDepsProcessingStart     = Event()
        self.onDepsProcessingDone      = Event()
        
        self.onDeletingStart           = Event()
        self.onDeletingDone            = Event()
        
        self.onFilesProcessingStart    = Event()
        self.onModFilesProcessingStart = Event()
        self.onModFilesProcessingDone  = Event()
        self.onFilesProcessingDone     = Event()

class Shared(Error):
    def __init__(self):
        super(Shared, self).__init__()
        
        self.ID       = None
        self.lic_key  = None
        self.exp_time = None
        self.token    = None
        
        self.respType = ResponseType.GetModsList
    
        self.mods         = {}
        self.dependencies = {}
        
        self.undeletedPaths = []
        
        self.__responseData = []
        self.__debugData    = []
        
        self.window       = None
        self.windowCommon = None
        
        self.logger = Logger()
        
        self.config = {
            'enable_GUI' : True
        }
        
        config = getJSON(Paths.CONFIG_PATH, self.config)
        
        if config is None:
            self.fail(ErrorCode.Config)
            return
        elif isinstance(config, int):
            self.fail(ErrorCode.Config, config)
            return
        else:
            self.config = config
        
    def fail(self, err, extraCode=0):
        super(Shared, self).fail(err, extraCode)
        
        if isinstance(err, tuple):
            err, extraCode = err
        if isinstance(err, int) or isinstance(err, str):
            err = ErrorCode.__getattr__(err)
        
        self.handleErr(err, extraCode)
        
        import os
        import codecs
        import json
        from time import strftime
        
        self.logger.log('Error %s (%s)'%(err, extraCode))
        
        if not DEBUG:
            return
        
        dump = {
            'name' : 'dump ' + strftime('%d.%m.%Y %H_%M_%S'),
            'data' : {
                'mods'         : [mod.dict()        for mod        in self.mods.values()],
                'dependencies' : [dependency.dict() for dependency in self.dependencies.values()],
                'requestsData' : self.__responseData
            },
            'debug' : self.__debugData
        }
        
        try:
            with codecs.open(Directory['DUMP_DIR'] + dump['name'] + '.json', 'wb', 'utf-8') as dump_file:
                json.dump(dump['data'], dump_file, ensure_ascii=False, sort_keys=True, indent=4)
            
            if DEBUG:
                with open(Directory['DUMP_DIR'] + dump['name'] + '_debug.bin', 'wb') as dbg_file:
                    for i, data in enumerate(dump['debug']):
                        dbg_file.write('packet %s:%s'%(i, data))
            
            self.logger.log('Dump data was saved to', Directory['DUMP_DIR'] + dump['name'])
        except:
            import traceback
            self.logger.log('Unable to save dump data:\n%s'%(traceback.format_exc()))
            
     
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
    
    def addResponse(self, response):
        self.__responseData.append(response.dict())
        if DEBUG:
            self.__debugData.append(response.bin())

g_AUEvents = Events()
g_AUShared = Shared()
