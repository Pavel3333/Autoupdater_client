import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

from constants import AUTH_REALM

from .common import *

import json

from os.path import exists

__all__ = ('cases_by_postfix', 'htmlMsg', 'g_AUGUIShared')

def cases_by_postfix(case, data, types):
    prefix  = data // 10
    postfix = data  % 10

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
        ErrorCode    = AUMain.ErrorCode
        WarningCode  = AUMain.WarningCode
        ResponseType = AUMain.ResponseType
        
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
                str(ErrorCode.Translations)     : "An error occured while loading autoupdater translations.\nPlease redownload the autoupdater",
                str(ErrorCode.Config)           : "An error occured while loading autoupdater config.\nPlease redownload the autoupdater",
                str(ErrorCode.LoadXFWNative)    : "An error occured while loading XFW Native files.\nPlease redownload the autoupdater",
                str(ErrorCode.UnpackNative)     : "An error occured while unpacking native module.\nPlease redownload the autoupdater",
                str(ErrorCode.LoadNative)       : "An error occured while loading native module.\nPlease redownload the autoupdater",
                str(ErrorCode.CheckID)          : "An error occured while checking player ID",
                str(ErrorCode.FilesNotFound)    : "An error occured while loading autoupdater files.\nPlease redownload the autoupdater",
                str(ErrorCode.LicInvalid)       : "License key is invalid",
                str(ErrorCode.Connect)          : "Unable to connect to the server",
                str(ErrorCode.RespTooSmall)     : "An error occured: got empty response",
                str(ErrorCode.RespInvalid)      : "An error occured: got invalid response",
                str(ErrorCode.TokenExpired)     : "Unable to prolong the token.\nPlease contact us",
                str(ErrorCode.GetMods)          : "An error occured while getting mod list. Error code %s",
                str(ErrorCode.ReadMods)         : "An error occured while reading mod list",
                str(ErrorCode.GetDeps)          : "An error occured while getting dependencies list. Error code %s",
                str(ErrorCode.ReadDeps)         : "An error occured while reading dependencies list",
                str(ErrorCode.GetFiles)         : "An error occured while getting files. Error code %s",
                str(ErrorCode.InvalidPathLen)   : "Got invalid path length",
                str(ErrorCode.InvalidFileSize)  : "Got invalid file size",
                str(ErrorCode.CreateFile)       : "Unable to update some files.\nThey will be updated after game restart",
                str(ErrorCode.CreateManualFile) : "Unable to update some files and copy it to manual directory.\nPlease contact us",
                str(ErrorCode.GetModFields)     : "Could not get mod data",
                str(ErrorCode.DecodeModFields)  : "Got incorrect mod data",
                str(ErrorCode.DeleteFile)       : "Unable to delete some files.\nThey will be deleted after game restart",
                # native module errors
                str(ErrorCode.CurlGInit)        : "CURL global initialization failed. Error code %s.\nPlease contact us",
                str(ErrorCode.CurlEInit)        : "CURL initialization failed. Error code %s.\nPlease contact us"    
            },
            "msg_warn" : {
                str(WarningCode.CheckID)      : "ID was not found",
                str(WarningCode.GetUserData)  : "You are not subscribed to Autoupdater.<br>You can subscribe it on \"https://pavel3333.ru/trajectorymod/lk\"",
                str(WarningCode.TokenExpired) : "Unable to prolong the token.\nPlease contact us",
                str(WarningCode.Expired)      : "Autoupdater subscription has expired.<br >You can renew the subscription on \"https://pavel3333.ru/trajectorymod/lk\"",
                str(WarningCode.GetModDesc)   : "Mod was not found"
            },
            "titles" : {
                "main" : AUMain.Constants.MOD_NAME,
                "procStart" : {
                    str(ResponseType.GetModsList) : "Getting mods list...",
                    str(ResponseType.GetDeps)     : "Getting dependicies list...",
                    str(ResponseType.DelFiles)    : "Deleting old files...",
                    str(ResponseType.GetFiles)    : "Getting files..."
                },
                "procDone"  : {
                    str(ResponseType.GetModsList) : "Getting mods list done",
                    str(ResponseType.GetDeps)     : "Getting dependicies list done",
                    str(ResponseType.DelFiles)    : "Deleting old files done",
                    str(ResponseType.GetFiles)    : "Getting files done"
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
        
        translation = AUMain.getJSON(GUIPaths.TRANSLATION_PATH%(str(AUMain.AUTH_REALM).lower()), self.translation)
        
        if translation is None:
            AUMain.g_AUShared.fail(AUMain.ErrorCode.Translations)
            return
        elif isinstance(translation, int):
            AUMain.g_AUShared.fail(AUMain.ErrorCode.Translations, translation)
            return
        else:
            self.translation = translation
    
    def getMsg(self, key):
        return self.translation['msg'][key]
    
    def getErrMsg(self, err):
        if isinstance(err, int):
            err = AUMain.ErrorCode.__getattr__(err)
        return self.translation['msg_err'][str(err)]
    
    def getWarnMsg(self, code):
        if isinstance(code, int):
            code = AUMain.WarningCode.__getattr__(err)
        return self.translation['msg_warn'][str(code)]
    
    def getTitle(self, key):
        result = self.translation['titles'][key]
        
        if isinstance(result, dict):
            return result[str(AUMain.g_AUShared.respType)]
        return result
    
    def handleErr(self, err, code=0):
        if err == AUMain.ErrorCode.Success:
            return
        
        msg = self.handleServerErr(err, code)
        
        if AUMain.g_AUShared.respType == AUMain.ResponseType.GetModsList:
            code_key = {
                AUMain.WarningCode.GetUserData : 'subscribe',
                AUMain.WarningCode.Expired     : 'renew'
            }
            
            if code in code_key:
                key = code_key[code]
                
                self.createDialog(
                    title=self.getMsg('warn'),
                    message=msg,
                    submit=self.getMsg(key),
                    close=self.getMsg('close'),
                    url='https://pavel3333.ru/trajectorymod/lk'
                )
        
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setStatus(htmlMsg(self.getMsg('warn') + ' ' + msg, color='ff0000'))
    
    def handleServerErr(self, err, code):
        if AUMain.WarningCode.__hasattr__(code):
            return self.getWarnMsg(code)
        elif SimpleErr.__hasattr__(err):
            return self.getErrMsg(err)
        elif FormatErr.__hasattr__(err):
            return self.getErrMsg(err)%(code)
        return self.getMsg('unexpected')%(err, code)
    
    def show_format_date(self, case, data):
        if not data:
            return ''
        times = ''
        if AUMain.AUTH_REALM == 'RU':
            times = cases_by_postfix(case, data, self.translation['times_ru'])
        else:
            times = self.translation['times_en'][case]
            if data > 1:
                times += 's'
        return '%s <u><b>%s</b></u> '%(data, times)
    
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
