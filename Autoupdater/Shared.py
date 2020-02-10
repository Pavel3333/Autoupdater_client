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
        
        self.undeletedPaths = set()
        
        self.__requestsData = []
        
        self.window = None
        self.logger = Logger()
        
        self.err = ErrorCode.index('SUCCESS')
    
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
            'name' : 'dump ' + strftime('%d.%m.%Y %H_%M_%S') + '.json',
            'data' : {
                'mods'         : [mod.dict()        for mod        in self.mods.values()],
                'dependencies' : [dependency.dict() for dependency in self.dependencies.values()],
                'requestsData' : self.__requestsData
            }
        }
        
        #try:
        with codecs.open(Directories['DUMP_DIR'] + dump['name'], 'w', 'utf-8') as dump_file:
            json.dump(dump['data'], dump_file, ensure_ascii=False, sort_keys=True, indent=4)
        
        self.logger.log('Dump data was saved to', Directories['DUMP_DIR'] + dump['name'])
        #except Exception:
        #    self.logger.log('Unable to save dump data')
    
    def getErr(self):
        return self.err
    
    def handleErr(self, respType, err, code):
        if respType in {
            ResponseType.index('GET_MODS_LIST'),
            ResponseType.index('GET_DEPS')
            }:
            if err == ErrorCode.index('SUCCESS'):
                return
            
            if code in WarningCode.values():
                msg = g_AUGUIShared.getWarnMsg(code)
                if err == ErrorCode.index('GETTING_MODS'):
                    code_key = {
                        WarningCode['USER_NOT_FOUND'] : 'subscribe',
                        WarningCode['TIME_EXPIRED']   : 'renew'
                    }
                    
                    if code in code_key:
                        key = code_key[code]
                        
                        self.createDialog(title=g_AUGUIShared.getMsg('warn'), message=msg, submit=g_AUGUIShared.getMsg(key), close=g_AUGUIShared.getMsg('close'), url='https://pavel3333.ru/trajectorymod/lk')
            else:
                msg = g_AUGUIShared.getMsg('unexpected')%(err, code)
                
            err_status = {
                ErrorCode.index('GETTING_MODS') : StatusType.index('MODS_LIST'),
                ErrorCode.index('GETTING_DEPS') : StatusType.index('DEPS')
            }
            
            if self.window:
                window.setStatus(err_status[err], htmlMsg(g_AUGUIShared.getMsg('warn') + ' ' + msg, color='ff0000'))
    
    def handleServerErr(err, code):
        if code in AllErr:
            msg = g_AUGUIShared.getErrMsg(err)
            if code in FormatErr:
                msg = msg%(code)
            return msg
        return g_AUGUIShared.getMsg('unexpected')%(err, code)
    
    def createDialog(*args, **kw):
        if self.window is not None:
            self.window.createDialog(*args, **kw)
        else:
            keys = ('title', 'message')
            msg = ''
            for key in keys:
                if key in kw:
                    msg += kw[key] + ' '
            
            if 'url' in kw:
                msg += ' (%s)'%(kw['url'])
            
            self.logger.log(msg)
    
    def addRequestData(self, requestData):
        self.__requestsData.append(requestData)

g_AUEvents = Events()
g_AUShared = Shared()
