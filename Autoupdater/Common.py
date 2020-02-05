__all__ = ('LangID', 'AUTH_REALM', 'ErrorCode', 'WarningCode', 'ResponseType', 'DataUnits', 'StatusType', 'ProgressType', 'getKey', 'Constants', 'Paths', 'Event', 'Mod')

LangID = (
    'RU',
    'EU',
    'CN'
)

AUTH_REALM = 'EU'

try:
    from constants import AUTH_REALM
except ImportError:
    pass

ErrorCode = (
    'SUCCESS',           # 0
    'TRANSLATIONS',      # 1
    'CHECKING_ID',       # 2
    'FILES_NOT_FOUND',   # 3
    'LIC_INVALID',       # 4
    'RESP_TOO_SMALL',    # 5
    'RESP_SIZE_INVALID', # 6
    'GETTING_MODS',      # 7
    'READING_MODS',      # 8
    'GETTING_DEPS',      # 9
    'READING_DEPS',      # 10
    'GETTING_FILES',     # 11
    'CREATING_FILE',     # 12
    'GET_MOD_FIELDS',    # 13
    'DECODE_MOD_FIELDS', # 14
    'DELETING_FILE'      # 15
)

WarningCode = {
    'CHECKING_ID'    : 7,
    'LIC_INVALID'    : 8,
    'ID_NOT_FOUND'   : 11,
    'USER_NOT_FOUND' : 12,
    'TIME_EXPIRED'   : 13,
    'MOD_NOT_FOUND'  : 19
}

ResponseType = (
    'GET_MODS_LIST', # 0
    'GET_DEPS',      # 1
    'DEL_FILES',     # 2
    'GET_FILES'      # 3
)

DataUnits = (
    'B',  # 0
    'KB', # 1
    'MB', # 2
    'GB'  # 3
)

StatusType = (
    'MODS_LIST', # 0
    'DEPS',      # 1
    'DEL',       # 2
    'FILES'      # 3
)

ProgressType = (
    'MODS_LIST_DATA', # 0
    'FILES_DATA',     # 1
    'FILES_TOTAL'     # 2
)

def getKey(err, codes={}):
    if isinstance(err, str):
        return err
    elif isinstance(err, int):
        for key, code in codes.iteritems():
            if code == err:
                return key
    raise KeyError('Error %s was not found'%(err))

class Constants:
    MOD_NAME = 'Autoupdater'
    
    MOD_DIR  = './res/scripts/client/gui/mods/%s/'%(MOD_NAME)
    FAIL_DIR = './%s_manual/'%(MOD_NAME)
    DUMP_DIR = './%s_dumps/'%(MOD_NAME)

    AUTOUPDATER_URL = 'http://api.pavel3333.ru/autoupdate.php'

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

class Paths:
    LIC_PATH        = Constants.MOD_DIR + Constants.MOD_NAME.upper() + '_%s.lic'
    EXE_HELPER_PATH = './com.pavel3333.%s.exe'%(Constants.MOD_NAME)
    DELETED_PATH    = './%s_delete.txt'%(Constants.MOD_NAME)
    LOG_PATH        = './%s_log.txt'%(Constants.MOD_NAME)

class Event(object):
    def __init__(self):
        self.queue = []

    def __call__(self, *args):
        for func in self.queue:
            func(*args)
    
    def __iadd__(self, func):
        self.queue.append(func)
        return self

import json

from os      import makedirs
from os.path import exists
from hashlib import md5

class Mod(object):
    __slots__ = { 'failed', 'needToUpdate', 'needToUpdatePaths', 'needToDeletePaths', 'id', 'enabled', 'name', 'description', 'version', 'build', 'tree', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        self.failed = ErrorCode.index('SUCCESS')
        
        self.needToUpdate = set()
        
        self.needToUpdatePaths = set()
        self.needToDeletePaths = set()
        
        try:
            self.id          = mod['id'], 
            self.enabled     = bool(mod['enabled']),
            self.name        = mod['name']
            self.description = mod['description']
            self.version     = mod['version']
            self.build       = mod['build']
        except KeyError:
            self.failed = ErrorCode.index('GET_MOD_FIELDS')
            return
        
        try:
            self.tree   = json.loads(mod['tree'])
            self.names  = json.loads(mod['names'])
            self.hashes = json.loads(mod['hashes'])
            if 'dependencies' in mod:
                self.dependencies = json.loads(mod['dependencies'])
        except Exception:
            self.failed = ErrorCode.index('DECODE_MOD_FIELDS')
    
    def parseTree(self, path, curr_dic):
        for ID in curr_dic:
            ID_i = int(ID)
            
            subpath = path + self.names[ID]
            if curr_dic[ID] == 0:
                if not exists(subpath):
                    if self.enabled:
                        self.needToUpdate.add(ID)
                        self.needToUpdatePaths.add(subpath)
                    continue
                elif not self.enabled:
                    self.needToDeletePaths.add(subpath)
                    continue
                
                hash_ = md5(open(subpath, 'rb').read()).hexdigest()

                if hash_ != self.hashes[ID]:
                    self.needToUpdate.add(ID)
                    self.needToUpdatePaths.add(subpath)
            else:
                if self.enabled and not exists(subpath):
                    makedirs(subpath)
                    
                self.parseTree(subpath + '/', curr_dic[ID])
                
                if not self.enabled:
                    self.needToDeletePaths.add(subpath)
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.__slots__)