from gui.mods.Autoupdater.Common import Constants, ErrorCodes

SimplyErrorCodes = map(str, (
    ErrorCodes.FAIL_TRANSLATIONS,
    ErrorCodes.FAIL_CHECKING_ID,
    ErrorCodes.FILES_NOT_FOUND,
    ErrorCodes.LIC_INVALID,
    ErrorCodes.RESP_TOO_SMALL,
    #ErrorCodes.RESP_SIZE_INVALID,
    ErrorCodes.FAIL_READING_MODS,
    ErrorCodes.FAIL_READING_DEPS,
    ErrorCodes.FAIL_CREATING_FILE,
    ErrorCodes.FAIL_GET_MOD_FIELDS,
    ErrorCodes.FAIL_DECODE_MOD_FIELDS
))

FormattedErrorCodes = map(str, (
    ErrorCodes.FAIL_GETTING_MODS,
    ErrorCodes.FAIL_GETTING_DEPS,
    ErrorCodes.FAIL_GETTING_FILES
))

class GUIPaths:
    GUI_DIR = Constants.MOD_DIR + 'GUI'
    
    #ICON_PATH        = GUI_DIR + '/winicon.ico'
    TRANSLATION_PATH = GUI_DIR + '/i18n.json'
