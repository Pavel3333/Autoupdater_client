from Autoupdater_Main.python.py_external import *

class SimpleErr(Enum):
    Translations     = 1
    Config           = 2
    LoadXFWNative    = 3
    UnpackNative     = 4
    LoadNative       = 5
    CheckID          = 6
    LicNotFound      = 7
    LicInvalid       = 8
    Connect          = 9
    RespTooSmall     = 10
    RespInvalid      = 11
    TokenExpired     = 12
    ReadMods         = 14
    ReadDeps         = 16
    InvalidPathLen   = 18
    InvalidFileSize  = 19
    CreateFile       = 20
    CreateManualFile = 21
    GetModFields     = 22
    DecodeModFields  = 23
    DeleteFile       = 24

class FormatErr(Enum):
    GetMods  = 13
    GetDeps  = 15
    GetFiles = 17
    # native module errors
    CurlGInit = 25
    CurlEInit = 26