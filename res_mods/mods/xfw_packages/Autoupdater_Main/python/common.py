from .enum import *
__all__ = ('LangID', 'AUTH_REALM', 'DEBUG', 'ErrorCode', 'WarningCode', 'ResponseType', 'DataUnits', 'ProgressType', 'Resp2ProgressTypeMap', 'Error', 'getJSON', 'checkSeqs', 'Constants', 'Directory', 'Paths', 'getLevels', 'Event', 'DeleteExclude', 'Mod')

class LangID(Enum):
    RU = 0
    EU = 1
    CN = 2

AUTH_REALM = LangID.EU

try:
    from constants import AUTH_REALM as game_realm
    if LangID.__hasattr__(game_realm):
        AUTH_REALM = LangID.__getattr__(game_realm)
except ImportError:
    pass

DEBUG = True

class ErrorCode(Enum):
    Success          = 0
    Translations     = 1
    Config           = 2
    LoadXFWNative    = 3
    UnpackNative     = 4
    LoadNative       = 5
    CheckID          = 6
    FilesNotFound    = 7
    LicInvalid       = 8
    Connect          = 9
    RespTooSmall     = 10
    RespInvalid      = 11
    TokenExpired     = 12
    GetMods          = 13
    ReadMods         = 14
    GetDeps          = 15
    ReadDeps         = 16
    GetFiles         = 17
    InvalidPathLen   = 18
    InvalidFileSize  = 19
    CreateFile       = 20
    CreateManualFile = 21
    GetModFields     = 22
    DecodeModFields  = 23
    DeleteFile       = 24
    # native module errors
    CurlGInit        = 25
    CurlEInit        = 26

class WarningCode(Enum):
    #HTTPS          = 1
    #ReqNotFound    = 2
    #ParseHdr       = 3
    #ReqInvalidLen  = 4
    #ParseWGID      = 5
    #ReadLic        = 6
    CheckID         = 7
    GetUserData     = 8
    #ReadToken      = 9
    TokenExpired    = 10
    Expired         = 11
    #ReadCode       = 12
    #IncorrectCode  = 13
    #ReadLang       = 14
    #ReadGUIFlag    = 15
    #ParseDepsCount = 16
    #Parse_GF_Hdr   = 17
    GetModDesc      = 18
    
    #Unknown        = 255

class ResponseType(Enum):
    GetModsList = 0
    GetDeps     = 1
    DelFiles    = 2
    GetFiles    = 3

class DataUnits(Enum):
    B  = 0
    KB = 1
    MB = 2
    GB = 3

class ProgressType(Enum):
    ModsListData = 0
    FilesData    = 1
    FilesTotal   = 2

Resp2ProgressTypeMap = {
    int(ResponseType.GetModsList) : ProgressType.ModsListData,
    int(ResponseType.GetDeps)     : ProgressType.ModsListData,
    int(ResponseType.DelFiles)    : ProgressType.FilesData,
    int(ResponseType.GetFiles)    : ProgressType.FilesData
}

class Error(object):
    __slots__ = { 'fail_err', 'fail_code' }
    
    def __init__(self, *args):
        self.fail_err  = ErrorCode.Success
        self.fail_code = 0
    
    def check(self):
        return self.fail_err == ErrorCode.Success
    
    def fail(self, err, extraCode=0):
        if isinstance(err, int) or isinstance(err, str):
            err = ErrorCode.__getattr__(err)
        
        self.fail_err  = err
        self.fail_code = extraCode
    
    def slots(self):
        return self.__slots__

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
    except IOError as exc:
        return exc.errno
    except:
        return None

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

    AUTOUPDATER_URL = 'https://api.pavel3333.ru/autoupdate.php'

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

Directory = {
    'MOD_DIR'  : Constants.MOD_NAME + '/'
}
Directory.update({
    'FAIL_DIR'   : Directory['MOD_DIR'] + 'manual/',
    'DUMP_DIR'   : Directory['MOD_DIR'] + 'dumps/',
    'X86_DIR'    : 'win32/'
})

class Paths:
    LIC_PATH        = Directory['MOD_DIR'] + Constants.MOD_NAME.upper() + '_%s.lic'
    EXE_HELPER_PATH = Directory['X86_DIR'] + Constants.MOD_ID + '.Helper.exe'
    CONFIG_PATH     = Directory['MOD_DIR'] + 'config.json'
    DELETED_PATH    = Directory['MOD_DIR'] + 'delete.txt'
    LOG_PATH        = Directory['MOD_DIR'] + 'AUMain_log.txt'

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
        'replays',
        'res',
        'res_mods',
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
    __slots__ = { 'needToUpdate', 'needToDelete', 'id', 'enabled', 'name', 'description', 'version', 'build', 'tree', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        super(Mod, self).__init__()
    
        self.needToUpdate = { # Updating only files
            'ID'   : set(),
            'file' : set(),
            'dir'  : set()
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
            self.fail(ErrorCode.GetModFields)
            return
        
        try:
            self.tree   = json.loads(mod['tree'])
            self.names  = json.loads(mod['names'])
            self.hashes = json.loads(mod['hashes'])
            if 'dependencies' in mod:
                self.dependencies = json.loads(mod['dependencies'])
        except:
            self.fail(ErrorCode.DecodeModFields)
    
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
                    print 'dir not exists:', subpath
                    self.needToUpdate['dir'].add(subpath)
                elif not self.enabled and exists(subpath):
                    self.needToDelete['dir'].add(subpath)
                    
                self.parseTree(subpath + '/', curr_dic[ID])
    
    def slots(self):
        return super(Mod, self).slots() | self.__slots__ - {'needToUpdate', 'needToDelete'}
    
    def dict(self):
        return dict((slot, getattr(self, slot, None)) for slot in self.slots())
