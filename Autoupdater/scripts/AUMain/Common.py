__all__ = ('LangID', 'AUTH_REALM', 'DEBUG', 'ErrorCode', 'WarningCode', 'ResponseType', 'DataUnits', 'StatusType', 'ProgressType', 'getKey', 'Constants', 'Directory', 'Paths', 'getLevels', 'Event', 'DeleteExclude', 'Mod')

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

DEBUG = True

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
    MOD_ID   = 'com.pavel3333.' + MOD_NAME + '.Helper'

    AUTOUPDATER_URL = 'http://api.pavel3333.ru/autoupdate.php'

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

Directory = {
    'MOD_DIR'  : Constants.MOD_NAME + '/'
}
Directory.update({
    'FAIL_DIR'   : Directory['MOD_DIR'] + 'manual/',
    'DUMP_DIR'   : Directory['MOD_DIR'] + 'dumps/',
    'SCRIPT_DIR' : Directory['MOD_DIR'] + 'scripts/',
    'X86_DIR'    : './win32/'
})

class Paths:
    LIC_PATH        = Directory['MOD_DIR'] + Constants.MOD_NAME.upper() + '_%s.lic'
    EXE_HELPER_PATH = Directory['X86_DIR'] + Constants.MOD_ID + '.exe'
    DELETED_PATH    = Directory['MOD_DIR'] + 'delete.txt'
    LOG_PATH        = Directory['MOD_DIR'] + 'log.txt'

def getLevels(path):
    return len(filter(lambda level: bool(level), path.split('/')))

class Event(object):
    def __init__(self):
        self.queue = []

    def __call__(self, *args):
        for func in self.queue:
            func(*args)
    
    def __iadd__(self, func):
        self.queue.append(func)
        return self

DeleteExclude = {
    'dir' : {
        'game_metadata',
        'mods',
        'mods/1.7.1.2', #TODO
        'replays',
        'res',
        'res_mods',
        'res_mods/1.7.1.2', #TODO
        'screenshots',
        'updates',
        'win32',
        'win64'
    },
    'file': {
        'app_type.xml',
        'game_info.xml',
        'Licenses.txt',
        'paths.xml',
        'version.xml',
        'wgc_api.exe',
        'WorldOfTanks.exe',
        'WorldOfTanks.ico'
    }
}

import json

from os      import makedirs
from os.path import exists
from hashlib import md5

class Mod(object):
    __slots__ = { 'failed', 'needToUpdate', 'needToDelete', 'id', 'enabled', 'name', 'description', 'version', 'build', 'tree', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        self.failed = ErrorCode.index('SUCCESS')
        
        self.needToUpdate = { # Updating only files
            'ID'   : set(),
            'file' : set()
        }
        self.needToDelete = { # Deleting files and directories
            'file' : set(),
            'dir'  : set()
        }
        
        #try:
        self.id          = mod['id'], 
        self.enabled     = bool(mod['enabled']),
        self.name        = mod['name']
        self.description = mod['description']
        self.version     = mod['version']
        self.build       = mod['build']
        #except KeyError:
        #    self.failed = ErrorCode.index('GET_MOD_FIELDS')
        #    return
        
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
                        self.needToUpdate['ID'].add(ID)
                        self.needToUpdate['file'].add(subpath)
                    continue
                elif not self.enabled:
                    self.needToDelete['file'].add(subpath)
                    continue
                
                hash_ = md5(open(subpath, 'rb').read()).hexdigest()

                if hash_ != self.hashes[ID]:
                    self.needToUpdate['ID'].add(ID)
                    self.needToUpdate['file'].add(subpath)
            else:
                if self.enabled and not exists(subpath):
                    makedirs(subpath)
                    
                self.parseTree(subpath + '/', curr_dic[ID])
                
                if not self.enabled:
                    self.needToDelete['dir'].add(subpath)
    
    def slots(self):
        return self.__slots__ - {'needToUpdate', 'needToDelete'}
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())