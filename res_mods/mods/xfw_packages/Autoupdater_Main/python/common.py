__all__ = ('LangID', 'AUTH_REALM', 'getLangID', 'DEBUG', 'ErrorCode', 'WarningCode', 'ResponseType', 'DataUnits', 'StatusType', 'ProgressType', 'Error', 'getKey', 'getJSON', 'checkSeqs', 'Constants', 'Directory', 'Paths', 'getLevels', 'Event', 'DeleteExclude', 'Mod')

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

def getLangID():
    return LangID.index(AUTH_REALM) if AUTH_REALM in LangID else LangID.index('EU')

DEBUG = True

ErrorCode = (
    'SUCCESS',           # 0
    'TRANSLATIONS',      # 1
    'CONFIG',            # 2
    'LOAD_XFW_NATIVE',   # 3
    'UNPACK_NATIVE',     # 4
    'LOAD_NATIVE',       # 5
    'CHECKING_ID',       # 6
    'FILES_NOT_FOUND',   # 7
    'LIC_INVALID',       # 8
    'CONNECT',           # 9
    'RESP_TOO_SMALL',    # 10
    'RESP_SIZE_INVALID', # 11
    'GETTING_MODS',      # 12
    'READING_MODS',      # 13
    'GETTING_DEPS',      # 14
    'READING_DEPS',      # 15
    'GETTING_FILES',     # 16
    'INVALID_PATH_LEN',  # 17
    'INVALID_FILE_SIZE', # 18
    'CREATING_FILE',     # 19
    'GET_MOD_FIELDS',    # 20
    'DECODE_MOD_FIELDS', # 21
    'DELETING_FILE'      # 22
)

WarningCode = {
    'CHECKING_ID'    : 7,
    'LIC_INVALID'    : 8,
    'ID_NOT_FOUND'   : 11,
    'USER_NOT_FOUND' : 12,
    'TIME_EXPIRED'   : 13,
    'MOD_NOT_FOUND'  : 21
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

class Error(object):
    def __init__(self, *args):
        self.failed = ErrorCode.index('SUCCESS')
    
    def check(self):
        return self.failed == ErrorCode.index('SUCCESS')
    
    def fail(self, err, extraCode=0):
        if isinstance(err, str):
            err = ErrorCode.index(err)
        
        if err == ErrorCode.index('SUCCESS'):
            self.failed = err
        else:
            self.failed = (err, extraCode)

def getKey(err, codes={}):
    if isinstance(err, str):
        return err
    elif isinstance(err, int):
        for key, code in codes.iteritems():
            if code == err:
                return key
    raise KeyError('Error %s was not found'%(err))

def getJSON(path, pattern):
    import json
    
    from os.path import exists
    
    try:
        raw = {}
        
        if exists(path):
            with open(path, 'r') as fil:
                raw = json.load(fil)
        else:
            with open(path, 'w') as fil:
                json.dump(pattern, fil, sort_keys=True, indent=4)
            raw = pattern
        
        if all(checkSeqs(pattern[key], raw.get(key, {})) for key in pattern):
            return raw
        else:
            with open(path, 'w') as fil:
                json.dump(pattern, fil, sort_keys=True, indent=4)
            return pattern
    except:
        return False

def checkSeqs(seq1, seq2): # Check if dic1 contains keys of dic2
    if not isinstance(seq1, type(seq2)):
        string_types = (str, unicode)
        if type(seq1) not in string_types or type(seq2) not in string_types:
            return False
    if isinstance(seq1, dict):
        return all(key in seq2 and checkSeqs(seq1[key], seq2[key]) for key in seq1)
    elif isinstance(seq1, list):
        return len(seq1) == len(seq2) and all(checkSeqs(seq1[i], seq2[i]) for i in xrange(len(seq1)))
    return True
    

class Constants:
    MOD_NAME = 'Autoupdater'
    MOD_ID   = 'com.pavel3333.' + MOD_NAME

    AUTOUPDATER_URL = 'http://api.pavel3333.ru/autoupdate.php'

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

Directory = {
    'MOD_DIR'  : Constants.MOD_NAME + '/'
}
Directory.update({
    'FAIL_DIR'   : Directory['MOD_DIR'] + 'manual/',
    'DUMP_DIR'   : Directory['MOD_DIR'] + 'dumps/',
    'X86_DIR'    : './win32/'
})

class Paths:
    LIC_PATH        = Directory['MOD_DIR'] + Constants.MOD_NAME.upper() + '_%s.lic'
    EXE_HELPER_PATH = Directory['X86_DIR'] + Constants.MOD_ID + '.Helper.exe'
    CONFIG_PATH     = Directory['MOD_DIR'] + 'config.json'
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
        'mods/1.8.0.1', #TODO
        'replays',
        'res',
        'res_mods',
        'res_mods/1.8.0.1', #TODO
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

class Mod(Error):
    __slots__ = { 'failed', 'needToUpdate', 'needToDelete', 'id', 'enabled', 'name', 'description', 'version', 'build', 'tree', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        super(Mod, self).__init__()
    
        self.needToUpdate = { # Updating only files
            'ID'   : set(),
            'file' : set()
        }
        self.needToDelete = { # Deleting files and directories
            'file' : set(),
            'dir'  : set()
        }
        
        try:
            self.id          = mod['id']
            self.enabled     = mod['enabled']
            self.name        = mod['name']
            self.description = mod['description']
            self.version     = mod['version']
            self.build       = mod['build']
        except KeyError:
            self.fail('GET_MOD_FIELDS')
            return
        
        try:
            self.tree   = json.loads(mod['tree'])
            self.names  = json.loads(mod['names'])
            self.hashes = json.loads(mod['hashes'])
            if 'dependencies' in mod:
                self.dependencies = json.loads(mod['dependencies'])
        except:
            self.fail('DECODE_MOD_FIELDS')
    
    def parseTree(self, path, curr_dic):
        for ID in curr_dic:
            ID_i = int(ID)
            
            subpath = path + self.names[ID]
            if curr_dic[ID] == 0:
                if not exists(subpath):
                    if self.enabled:
                        if subpath not in self.needToUpdate['file']:
                            print 'update file', subpath, '(not exists)'
                        self.needToUpdate['ID'].add(ID)
                        self.needToUpdate['file'].add(subpath)
                    continue
                elif not self.enabled:
                    if subpath not in self.needToDelete['file']:
                        print 'delete', subpath
                    self.needToDelete['file'].add(subpath)
                    continue
                
                hash_ = md5(open(subpath, 'rb').read()).hexdigest()
                if ID in self.hashes and hash_ != self.hashes[ID]:
                    if subpath not in self.needToUpdate['file']:
                        print 'update file', subpath ,'(hash)'
                    self.needToUpdate['ID'].add(ID)
                    self.needToUpdate['file'].add(subpath)
            else:
                if self.enabled and not exists(subpath):
                    makedirs(subpath)
                    
                self.parseTree(subpath + '/', curr_dic[ID])
                
                if not self.enabled:
                    if subpath not in self.needToDelete['dir']:
                        print 'del dir', subpath
                    self.needToDelete['dir'].add(subpath)
    
    def slots(self):
        return self.__slots__ - {'needToUpdate', 'needToDelete'}
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())