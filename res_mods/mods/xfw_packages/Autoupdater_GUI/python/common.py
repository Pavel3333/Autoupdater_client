import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

__all__ = ('SimpleErr', 'FormatErr', 'AllErr', 'GUIPaths')

SimpleErr = frozenset(map(AUMain.ErrorCode.index, {
    'TRANSLATIONS',
    'CONFIG',
    'CHECKING_ID',
    'FILES_NOT_FOUND',
    'LIC_INVALID',
    'CONNECT',
    'RESP_TOO_SMALL',
    'RESP_SIZE_INVALID',
    'READING_MODS',
    'READING_DEPS',
    'CREATING_FILE',
    'GET_MOD_FIELDS',
    'DECODE_MOD_FIELDS',
    'DELETING_FILE'
}))

FormatErr = frozenset(map(AUMain.ErrorCode.index, {
    'GETTING_MODS',
    'GETTING_DEPS',
    'GETTING_FILES'
}))

AllErr = SimpleErr | FormatErr

class GUIPaths:
    GUI_DIR = AUMain.Directory['MOD_DIR'] + 'GUI/'
    
    #ICON_PATH       = GUI_DIR + 'winicon.ico'
    TRANSLATION_PATH = GUI_DIR + '%s.json'