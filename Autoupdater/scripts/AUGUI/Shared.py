from constants import AUTH_REALM

from AUMain import *

from Common import *

import json

from os.path import exists

__all__ = ('cases_by_postfix', 'htmlMsg', 'g_AUGUIShared')

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
                    "not_updated"  : "Not found any updates",
                    "updated"      : "Updated %s mods",
                    "deleted"      : "Deleted %s mods",
                    "partially"    : "Not all mods were updated successfully",
                    "unexpected"   : "Unexpected error %s (%s)",
                    
                    "dep"          : "Dependency \"%s\":",
                    "mod"          : "Mod \"%s\":",
                    
                    "no_upd"       : "Not found any updates. You are using latest version %s #%s",
                    "upd"          : "Updated to version %s #%s",
                    "del"          : "Deleted",
                    
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
                    "TRANSLATIONS"      : "An error occured while loading autoupdater translations.\nPlease redownload the autoupdater",
                    "CONFIG"            : "An error occured while loading autoupdater config.\nPlease redownload the autoupdater",
                    "CHECKING_ID"       : "An error occured while checking player ID",
                    "FILES_NOT_FOUND"   : "An error occured while loading autoupdater files.\nPlease redownload the autoupdater",
                    "LIC_INVALID"       : "License key is invalid",
                    "RESP_TOO_SMALL"    : "An error occured: getted empty response",
                    "RESP_SIZE_INVALID" : "An error occured: getted invalid response",
                    "GETTING_MODS"      : "An error occured while getting mod list. Error code %s",
                    "READING_MODS"      : "An error occured while reading mod list",
                    "GETTING_DEPS"      : "An error occured while getting dependencies list. Error code %s",
                    "READING_DEPS"      : "An error occured while reading dependencies list",
                    "INVALID_FILE_SIZE" : "Got invalid file size",
                    "GETTING_FILES"     : "An error occured while getting files. Error code %s",
                    "CREATING_FILE"     : "Unable to update some files.\nThey will be updated after game restart",
                    "DECODE_MOD_FIELDS" : "Getted incorrect mod data",
                    "DELETING_FILE"     : "Unable to delete some files.\nThey will be deleted after game restart"
                },
                "msg_warn" : {
                    "CHECKING_ID"      : "Unable to check player ID",
                    "LIC_INVALID"      : "Invalid license key",
                    "ID_NOT_FOUND"     : "ID was not found",
                    "USER_NOT_FOUND"   : "You are not subscribed to Autoupdater.<br>You can subscribe it on \"https://pavel3333.ru/trajectorymod/lk\"",
                    "TIME_EXPIRED"     : "Autoupdater subscription has expired.<br >You can renew the subscription on \"https://pavel3333.ru/trajectorymod/lk\"",
                    "MOD_NOT_FOUND"    : "Mod was not found"
                },
                "titles" : {
                    "main" : Constants.MOD_NAME,
                    "procStart" : {
                        "GET_MODS_LIST" : "Getting mods list...",
                        "GET_DEPS"      : "Getting dependicies list...",
                        "DEL_FILES"     : "Deleting old files...",
                        "GET_FILES"     : "Getting files..."
                    },
                    "procDone"  : {
                        "GET_MODS_LIST" : "Getting mods list done",
                        "GET_DEPS"      : "Getting dependicies list done",
                        "DEL_FILES"     : "Deleting old files done",
                        "GET_FILES"     : "Getting files done"
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
        
        translations = getJSON(GUIPaths.TRANSLATION_PATH, self.translations)
        
        if not translations:
            g_AUShared.setErr(ErrorCode.index('TRANSLATIONS'))
            return
        else:
            self.translations = translations
        
        self.translation = self.translations.get(AUTH_REALM, self.translations['EU'])
    
    def getMsg(self, key):
        return self.translation['msg'][key]
    
    def getErrMsg(self, err):
        if isinstance(err, int) and err in xrange(len(ErrorCode)):
            err = ErrorCode[err]
        return self.translation['msg_err'][err]
    
    def getWarnMsg(self, err):
        return self.translation['msg_warn'][getKey(err, WarningCode)]
    
    def getTitle(self, key, err=None):
        result = self.translation['titles'][key]
        
        if isinstance(result, dict):
            if err is not None:
                if isinstance(err, int) and err in xrange(len(ResponseType)):
                    err = ResponseType[err]
                return result[err]
            raise KeyError('getTitle: err is None')
        return result
    
    def handleErr(self, respType, err, code):
        if respType in {
            ResponseType.index('GET_MODS_LIST'),
            ResponseType.index('GET_DEPS')
            }:
            if err == ErrorCode.index('SUCCESS'):
                return
            
            if code in WarningCode.values():
                msg = g_AUGUIShared.getWarnMsg(code)
                if err == ErrorCode.index('GETTING_MODS'):
                    code_key = {
                        WarningCode['USER_NOT_FOUND'] : 'subscribe',
                        WarningCode['TIME_EXPIRED']   : 'renew'
                    }
                    
                    if code in code_key:
                        key = code_key[code]
                        
                        self.createDialog(title=g_AUGUIShared.getMsg('warn'), message=msg, submit=g_AUGUIShared.getMsg(key), close=g_AUGUIShared.getMsg('close'), url='https://pavel3333.ru/trajectorymod/lk')
            else:
                msg = g_AUGUIShared.getMsg('unexpected')%(err, code)
                
            err_status = {
                ErrorCode.index('GETTING_MODS') : StatusType.index('MODS_LIST'),
                ErrorCode.index('GETTING_DEPS') : StatusType.index('DEPS')
            }
            
            if self.window:
                window.setStatus(err_status[err], htmlMsg(g_AUGUIShared.getMsg('warn') + ' ' + msg, color='ff0000'))
    
    def handleServerErr(self, err, code):
        if code in AllErr:
            msg = self.getErrMsg(err)
            if code in FormatErr:
                msg = msg%(code)
            return msg
        return self.getMsg('unexpected')%(err, code)
    
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

g_AUGUIShared = Shared()
