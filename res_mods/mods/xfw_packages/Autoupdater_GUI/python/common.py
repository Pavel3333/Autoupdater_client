import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

__all__ = ('SimpleErr', 'FormatErr', 'GUIPaths')

class SimpleErr(AUMain.Enum):
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
    ReadMods         = 14
    ReadDeps         = 16
    InvalidPathLen   = 18
    InvalidFileSize  = 19
    CreateFile       = 20
    CreateManualFile = 21
    GetModFields     = 22
    DecodeModFields  = 23
    DeleteFile       = 24

class FormatErr(AUMain.Enum):
    GetMods  = 13
    GetDeps  = 15
    GetFiles = 17
    # native module errors
    CurlGInit = 25
    CurlEInit = 26

class GUIPaths:
    GUI_DIR = AUMain.Directory['MOD_DIR'] + 'GUI/'
    
    #ICON_PATH       = GUI_DIR + 'winicon.ico'
    TRANSLATION_PATH = GUI_DIR + '%s.json'
