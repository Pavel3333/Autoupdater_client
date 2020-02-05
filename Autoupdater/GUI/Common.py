from gui.mods.Autoupdater import *

__all__ = ('SimpleErr', 'FormatErr', 'AllErr', 'GUIPaths')

SimpleErr = {
    ErrorCode.index('TRANSLATIONS'),
    ErrorCode.index('CHECKING_ID'),
    ErrorCode.index('FILES_NOT_FOUND'),
    ErrorCode.index('LIC_INVALID'),
    ErrorCode.index('RESP_TOO_SMALL'),
    ErrorCode.index('RESP_SIZE_INVALID'),
    ErrorCode.index('READING_MODS'),
    ErrorCode.index('READING_DEPS'),
    ErrorCode.index('CREATING_FILE'),
    ErrorCode.index('GET_MOD_FIELDS'),
    ErrorCode.index('DECODE_MOD_FIELDS'),
    ErrorCode.index('DELETING_FILE')
}

FormatErr = {
    ErrorCode.index('GETTING_MODS'),
    ErrorCode.index('GETTING_DEPS'),
    ErrorCode.index('GETTING_FILES')
}

AllErr = SimpleErr | FormatErr

class GUIPaths:
    GUI_DIR = Constants.MOD_DIR + 'GUI'
    
    #ICON_PATH        = GUI_DIR + '/winicon.ico'
    TRANSLATION_PATH = GUI_DIR + '/i18n.json'
