import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

from constants import AUTH_REALM

from common import *

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
        self.translation = {
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
                "CONNECT"           : "Unable to connect to the server",
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
                "main" : AUMain.Constants.MOD_NAME,
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
        
        translation = AUMain.getJSON(GUIPaths.TRANSLATION_PATH%(AUMain.AUTH_REALM.lower()), self.translation)
        
        if not translation:
            AUMain.g_AUShared.fail('TRANSLATIONS')
            return
        else:
            self.translation = translation
    
    def getMsg(self, key):
        return self.translation['msg'][key]
    
    def getErrMsg(self, err):
        if isinstance(err, int) and err in xrange(len(AUMain.ErrorCode)):
            err = AUMain.ErrorCode[err]
        return self.translation['msg_err'][err]
    
    def getWarnMsg(self, err):
        return self.translation['msg_warn'][getKey(err, AUMain.WarningCode)]
    
    def getTitle(self, key, respType=None):
        result = self.translation['titles'][key]
        
        if isinstance(result, dict):
            if respType is not None:
                if isinstance(respType, int) and respType in xrange(len(AUMain.ResponseType)):
                    respType = AUMain.ResponseType[respType]
                return result[respType]
            raise KeyError('getTitle: respType is None')
        return result
    
    def handleErr(self, respType, err, code):
        if respType not in map(AUMain.ResponseType.index, {
            'GET_MODS_LIST',
            'GET_DEPS'
            }):
            return
        
        if isinstance(err, int) and err in xrange(len(AUMain.ErrorCode)):
            err = AUMain.ErrorCode[err]
        
        if err == 'SUCCESS':
            return
        
        if code in AUMain.WarningCode.values():
            msg = self.getWarnMsg(code)
            if err == 'GETTING_MODS':
                code_key = {
                    'USER_NOT_FOUND' : 'subscribe',
                    'TIME_EXPIRED'   : 'renew'
                }
                
                if code in map(AUMain.WarningCode.__getitem__, code_key):
                    key = code_key[code]
                    
                    self.createDialog(title=self.getMsg('warn'), message=msg, submit=self.getMsg(key), close=self.getMsg('close'), url='https://pavel3333.ru/trajectorymod/lk')
        else:
            msg = self.getMsg('unexpected')%(err, code)
            
        err_status = {
            'GETTING_MODS' : 'MODS_LIST',
            'GETTING_DEPS' : 'DEPS'
        }
        
        if self.window and err in err_status:
            window.setStatus(err_status[err], htmlMsg(self.getMsg('warn') + ' ' + msg, color='ff0000'))
    
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
            if AUMain.AUTH_REALM == 'RU':
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
