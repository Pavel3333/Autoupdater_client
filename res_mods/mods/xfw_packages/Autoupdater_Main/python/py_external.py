from .enum import *

print 'Autoupdater_Main: py_external'

class LangID(Enum):
    RU = 0
    EU = 1
    CN = 2

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

class Event(object):
    def __init__(self):
        self.queue = []

    def __call__(self, *args):
        for func in self.queue:
            func(*args)
    
    def __iadd__(self, func):
        self.queue.append(func)
        return self

def hookMethod(cls, method, new_method, *args):
    old_method = getattr(cls, method)
    setattr(cls, method, lambda *args: new_method(old_method, *args))