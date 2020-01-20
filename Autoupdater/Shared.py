from Common import ErrorCodes, Event

class Events:
    def __init__(self):
        self.onModsProcessingStart     = Event()
        self.onModsDataProcessed       = Event()
        self.onModsProcessingDone      = Event()
        
        self.onDepsProcessingStart     = Event()
        self.onDepsDataProcessed       = Event()
        self.onDepsProcessingDone      = Event()
        
        self.onFilesProcessingStart    = Event()
        self.onModFilesProcessingStart = Event()
        self.onModFilesDataProcessed   = Event()
        self.onModFilesProcessingDone  = Event()
        self.onFilesProcessingDone     = Event()

class Shared:
    def __init__(self):
        self.mods         = {}
        self.dependencies = {}
        
        self.__requestsData = []
        
        self.window = None
        
        self.err = ErrorCodes.SUCCESS
    
    def setSuccess(self):
        self.err = ErrorCodes.SUCCESS
        
    def setErr(self, errCode, extraCode=0):
        self.err = (errCode, extraCode)
        
        if errCode == ErrorCodes.SUCCESS: return
        
        import os
        import codecs
        import json
        from time import strftime
        from Common import Constants
        
        print 'Autoupdater failed with error %s (%s)'%(errCode, extraCode)
        
        dump = {
            'name' : 'dump ' + strftime('%d.%m.%Y %H_%M_%S') + '.json',
            'data' : {
                'mods'         : [mod.dict()        for mod        in self.mods.values()],
                'dependencies' : [dependency.dict() for dependency in self.dependencies.values()],
                'requestsData' : self.__requestsData
            }
        }
        
        #try:
        if not os.path.exists(Constants.DUMP_DIR):
            os.makedirs(Constants.DUMP_DIR)
        
        with codecs.open(Constants.DUMP_DIR + dump['name'], 'w', 'utf-8') as dump_file:
            json.dump(dump['data'], dump_file, ensure_ascii=False, sort_keys=True, indent=4)
        
        print 'Dump data was saved to', Constants.DUMP_DIR + dump['name']
        #except Exception:
        #    pass

    def getErr(self):
        return self.err
    
    def addRequestData(self, requestData):
        self.__requestsData.append(requestData)

g_AutoupdaterEvents = Events()
g_AutoupdaterShared = Shared()
