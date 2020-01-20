class LangID:
    RU = 0
    EN = 1
    CN = 2

class ErrorCodes:
    SUCCESS                = 0
    FAIL_TRANSLATIONS      = 1
    FAIL_CHECKING_ID       = 2
    FILES_NOT_FOUND        = 3
    LIC_INVALID            = 4
    RESP_TOO_SMALL         = 5
    #RESP_SIZE_INVALID     = 6
    FAIL_GETTING_MODS      = 7
    FAIL_READING_MODS      = 8
    FAIL_GETTING_DEPS      = 9
    FAIL_READING_DEPS      = 10
    FAIL_GETTING_FILES     = 11
    FAIL_CREATING_FILE     = 12
    FAIL_GET_MOD_FIELDS    = 13
    FAIL_DECODE_MOD_FIELDS = 14

class WarningCodes:
    FAIL_CHECKING_ID = 7
    LIC_INVALID      = 8
    ID_NOT_FOUND     = 11
    USER_NOT_FOUND   = 12
    TIME_EXPIRED     = 13
    MOD_NOT_FOUND    = 19

warningCodes = map(str, (
    WarningCodes.FAIL_CHECKING_ID,
    WarningCodes.LIC_INVALID,
    WarningCodes.ID_NOT_FOUND,
    WarningCodes.USER_NOT_FOUND,
    WarningCodes.TIME_EXPIRED,
    WarningCodes.MOD_NOT_FOUND
))

class DataUnits:
    BYTES     = 0
    KILOBYTES = 1
    MEGABYTES = 2
    GIGABYTES = 3

class StatusType:
    MODS_LIST = 0
    DEPS      = 1
    FILES     = 2

class ProgressType:
    MODS_LIST_DATA = 0
    FILES_DATA     = 1
    FILES_TOTAL    = 2

class Constants:
    MOD_DIR  = './res/scripts/client/gui/mods/Autoupdater/' #'Autoupdater' #'res/scripts/client/gui/mods/Autoupdater'
    FAIL_DIR = './Autoupdater_manual/'
    DUMP_DIR = './Autoupdater_dumps/'

    AUTOUPDATER_URL = 'http://api.pavel3333.ru/autoupdate.php'

    GET_MODS_LIST = 0
    GET_DEPS      = 1
    GET_FILES     = 2

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

    DATA_UNITS = {
        DataUnits.BYTES     : 'B',
        DataUnits.KILOBYTES : 'KB',
        DataUnits.MEGABYTES : 'MB',
        DataUnits.GIGABYTES : 'GB'
    }

class Paths:
    LIC_PATH        = Constants.MOD_DIR + 'AUTOUPDATER_%s.lic'
    EXE_HELPER_PATH = './com.pavel3333.Autoupdater.exe'

import json

from os      import makedirs
from os.path import exists
from hashlib import md5

class Mod(object):
    __slots__ = { 'failed', 'needToUpdate', 'id', 'name', 'description', 'version', 'build', 'tree', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        self.failed = ErrorCodes.SUCCESS
        
        self.needToUpdate = []
        
        try:
            self.id          = mod['id'], 
            self.name        = mod['name']
            self.description = mod['description']
            self.version     = mod['version']
            self.build       = mod['build']
        except KeyError:
            self.failed = ErrorCodes.FAIL_GET_MOD_FIELDS
            return
        
        try:
            self.tree   = json.loads(mod['tree'])
            self.names  = json.loads(mod['names'])
            self.hashes = json.loads(mod['hashes'])
            if 'dependencies' in mod:
                self.dependencies = json.loads(mod['dependencies'])
        except Exception:
            self.failed = ErrorCodes.FAIL_DECODE_MOD_FIELDS

    def parseTree(self, path, curr_dic):
        for ID in curr_dic:
            ID_i = int(ID)
            
            subpath = path + self.names[ID]
            if curr_dic[ID] == 0:
                #print 'File  :', subpath
                #print 'Hash:', self.hashes[ID]
                
                if not exists(subpath):
                    self.needToUpdate.append(ID_i)
                    continue
                
                hash_ = md5(open(subpath, 'rb').read()).hexdigest()

                if hash_ != self.hashes[ID]:
                    self.needToUpdate.append(ID_i)
            else:
                #print 'Folder:', subpath
                if not exists(subpath):
                    makedirs(subpath)
                    
                self.parseTree(subpath + '/', curr_dic[ID])
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.__slots__)

class Event(object):
    def __init__(self):
        self.queue = []

    def __call__(self, *args):
        for func in self.queue:
            func(*args)
    
    def __iadd__(self, func):
        self.queue.append(func)
        return self

def div1024(value):
    return round(float(value) / 1024, 2)
