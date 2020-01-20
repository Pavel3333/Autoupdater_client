from constants import AUTH_REALM

from gui.mods.Autoupdater.Common     import ErrorCodes, WarningCodes, Constants
from gui.mods.Autoupdater.GUI.Common import GUIPaths
from gui.mods.Autoupdater.Shared     import g_AutoupdaterShared

import json

from os.path import exists

def cases_by_postfix(case, data, types):
    prefix  = data // 10
    postfix = data % 10

    type_ = 0
    if   prefix == 1 or postfix == 0 or postfix > 4:
        type_ = 0
    elif postfix == 1:
        type_ = 1
    elif 1 < postfix < 5:
        type_ = 2
        
    return types[type_][case]

def htmlMsg(msg, color=None, size=None, nl=0):
    fmted =  u'<font%s>%s</font>'
    attrs = ''
    if color is not None:
        attrs += ' color="#%s"'%(color)
    if size is not None:
        attrs += ' size="%s"'%(size)
    
    if not attrs:
        fmted = msg
    else:
        fmted = fmted%(attrs, msg)
    
    return fmted + '<br>'*nl

class Shared:
    def __init__(self):
        self.translations = {
            "EU" : {
                "info" : [
                    "Pavel3333 Mods Autoupdater",
                    "Author: Pavel3333 from RAINN VOD team",
                    "Authors YouTube channel \"RAINN VOD\"",
                    "Authors VK Group \"RAINN VOD\"",
                ],
                "msg" : {
                    "updated"      : "Successfully updated %s mods",
                    "partially"    : "Not all mods were installed successfully",
                    "no_upd"       : "Not found any updates. You are using latest version %s #%s",
                    "unexpected"   : "Unexpected error %s (%s)",
                    
                    "dep"          : "Dependency \"%s\":",
                    "mod"          : "Mod \"%s\":",
                    "mod_upd"      : "Successfully updated to version %s #%s",
                    
                    "mods"         : "mods",
                    "warn"         : "Warning!",
                    
                    "expires"      : "Autoupdater subscription expires after",
                    
                    "subscribe"    : "Subscribe",
                    "renew"        : "Renew subscription",
                    
                    "updated_desc" : "The changes will take effect after the client restarts",
                    "restart"      : "Restart",
                    
                    "close"        : "Close"
                },
                "msg_err" : {
                    str(ErrorCodes.FAIL_TRANSLATIONS)      : "An error occured while loading autoupdater translations.\nPlease redownload the autoupdater",
                    str(ErrorCodes.FAIL_CHECKING_ID)       : "An error occured while checking player ID",
                    str(ErrorCodes.FILES_NOT_FOUND)        : "An error occured while loading autoupdater files.\nPlease redownload the autoupdater",
                    str(ErrorCodes.LIC_INVALID)            : "License key is invalid",
                    str(ErrorCodes.RESP_TOO_SMALL)         : "An error occured: getted empty response",
                    #str(ErrorCodes.RESP_SIZE_INVALID)     : "An error occured: getted invalid response",
                    str(ErrorCodes.FAIL_GETTING_MODS)      : "An error occured while getting mod list. Error code %s",
                    str(ErrorCodes.FAIL_READING_MODS)      : "An error occured while reading mod list",
                    str(ErrorCodes.FAIL_GETTING_DEPS)      : "An error occured while getting dependencies list. Error code %s",
                    str(ErrorCodes.FAIL_READING_DEPS)      : "An error occured while reading dependencies list",
                    str(ErrorCodes.FAIL_GETTING_FILES)     : "An error occured while getting files. Error code %s",
                    str(ErrorCodes.FAIL_CREATING_FILE)     : "Cannot to update some files.\nThey will be updated after game restart",
                    str(ErrorCodes.FAIL_DECODE_MOD_FIELDS) : "Getted incorrect mod data"
                },
                "msg_warn" : {
                    str(WarningCodes.FAIL_CHECKING_ID) : "Cannot to check player ID",
                    str(WarningCodes.LIC_INVALID)      : "Invalid license key",
                    str(WarningCodes.ID_NOT_FOUND)     : "ID was not found",
                    str(WarningCodes.USER_NOT_FOUND)   : "You are not subscribed to Autoupdater.<br>You can subscribe it on \"https://pavel3333.ru/trajectorymod/lk\"",
                    str(WarningCodes.TIME_EXPIRED)     : "Autoupdater subscription has expired.<br >You can renew the subscription on \"https://pavel3333.ru/trajectorymod/lk\"",
                    str(WarningCodes.MOD_NOT_FOUND)    : "Mod was not found"
                },
                "titles" : {
                    "main" : "Autoupdater",
                    "procStart" : {
                        str(Constants.GET_MODS_LIST) : "Getting mods list...",
                        str(Constants.GET_DEPS)      : "Getting dependicies list...",
                        str(Constants.GET_FILES)     : "Getting files..."
                    },
                    "procDone"  : {
                        str(Constants.GET_MODS_LIST) : "Getting mods list done",
                        str(Constants.GET_DEPS)      : "Getting dependicies list done",
                        str(Constants.GET_FILES)     : "Getting files done"
                    }
                },
                "times_ru" : [
                    [
                        "months",
                        "days",
                        "hours",
                        "minutes"
                    ],
                    [
                        "month",
                        "day",
                        "hour",
                        "minute"
                    ],
                    [
                        "month",
                        "day",
                        "hour",
                        "minute"
                    ]
                ],
                "times_en" : [
                    "month",
                    "day",
                    "hour",
                    "minute"
                ]
            }
        }

        translations = {}
        #try:
        if exists(GUIPaths.TRANSLATION_PATH):
            with open(GUIPaths.TRANSLATION_PATH, 'r') as fil:
                translations = json.loads(fil.read())
        else:
            with open(GUIPaths.TRANSLATION_PATH, 'w') as fil:
                fil.write(json.dumps(self.translations, sort_keys=True, indent=4))
            translations = self.translations
        
        if all(self.checkSeqs(self.translations[key], translations.get(key, {})) for key in self.translations):
            self.translations = translations
        else:
            with open(GUIPaths.TRANSLATION_PATH, 'w') as fil:
                fil.write(json.dumps(self.translations, sort_keys=True, indent=4))
        #except Exception:
        #    g_AutoupdaterShared.setErr(ErrorCodes.FAIL_TRANSLATIONS)

        self.translation = self.translations.get(AUTH_REALM, self.translations['EU'])
    
    def checkSeqs(self, seq1, seq2): #check if dic1 contains keys of dic2
        if not isinstance(seq1, type(seq2)):
            return False
        
        if isinstance(seq1, dict):
            return all(key in seq2 and self.checkSeqs(seq1[key], seq2[key]) for key in seq1)
        elif isinstance(seq1, list):
            return len(seq1) == len(seq2) and all(self.checkSeqs(seq1[i], seq2[i]) for i in xrange(len(seq1)))
        return True
    
    def show_format_date(self, case, data):
        if data:
            times = ''
            if AUTH_REALM == 'RU':
                times = cases_by_postfix(case, data, self.translation['times_ru'])
            else:
                times = self.translation['times_en'][case]
                if data > 1:
                    times += 's'
            return '%s <u><b>%s</b></u> '%(data, times)
        else:
            return ''
    
    def exp_time(self, exp):
        from time import time
        dt = exp - int(time());

        if dt < 0: return ''
        
        months =  dt            // 2592000
        days   = (dt % 2592000) // 86400
        hrs    = (dt % 86400)   // 3600
        mins   = (dt % 3600)    // 60
        
        return  self.show_format_date(0, months) + \
                self.show_format_date(1, days)   + \
                self.show_format_date(2, hrs)    + \
                self.show_format_date(3, mins)

g_AutoupdaterGUIShared = Shared()
