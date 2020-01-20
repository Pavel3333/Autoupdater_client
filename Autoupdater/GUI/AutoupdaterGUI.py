import BigWorld

import re
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.SystemMessages import SM_TYPE, pushMessage
from notification.settings import NOTIFICATION_TYPE
from notification.actions_handlers import NotificationsActionsHandlers

import json

from gui.mods.Autoupdater.Shared import g_AutoupdaterEvents, g_AutoupdaterShared

class AutoupdaterGUI:
    def __init__(self):
        self.window       = None
    
        self.battles_ctr    = 0
        self.showed_info    = 0
        self.showed_success = False
        
        g_AutoupdaterEvents.onDataProcessed        += self.onDataProcessed
        g_AutoupdaterEvents.onModsProcessingStart  += self.onModsProcessingStart
        g_AutoupdaterEvents.onModsProcessingDone   += self.onModsProcessingDone
        g_AutoupdaterEvents.onDepsProcessingStart  += self.onDepsProcessingStart
        g_AutoupdaterEvents.onDepsProcessingDone   += self.onDepsProcessingDone
        g_AutoupdaterEvents.onFilesProcessingStart += self.onFilesProcessingStart
        g_AutoupdaterEvents.onFilesProcessingDone  += self.onFilesProcessingDone
        
        #hooks
        _NotificationsActionsHandlers__handleAction = NotificationsActionsHandlers.handleAction
        NotificationsActionsHandlers.handleAction = lambda *args: self.handleAction(_NotificationsActionsHandlers__handleAction, *args)
        
        _LobbyView__populate = LobbyView._populate
        LobbyView._populate = lambda *args: self.lobbyPopulate(_LobbyView__populate, *args)
        
        #print self.checkFails()

    def lobbyPopulate(self, func, *args):
        func(*args)
        
        info = self.translation['info']
        
        if not self.showed_info % 3:
            txt_dial =  self.htmlMsg(info[0], size=20, nl=2)
            txt_dial += self.htmlMsg(info[1], color='228b22', size=16, nl=1)
            txt_dial += self.htmlMsg('<a href="event:https://www.youtube.com/c/RAINNVOD">%s</a>'%(info[2]), size=16, nl=1)
            txt_dial += self.htmlMsg('<a href="event:https://vk.com/rainn_vod">%s</a>'%(info[3]), size=16, nl=1)
            
            pushMessage(txt_dial, SM_TYPE.GameGreeting)
        
        self.showed_info += 1
        
        if not self.battles_ctr % 4:
            message = self.checkFails()
            print message
            
            if not self.showed_success:
                pushMessage(message, SM_TYPE.GameGreeting)
                self.showed_success = True
        
        self.battles_ctr += 1
    
    def handleAction(self, func, *args):
        if args[2] == NOTIFICATION_TYPE.MESSAGE and re.match('https?://', args[4], re.I):
            BigWorld.wg_openWebBrowser(args[4])
        else:
            func(*args)
    
    def checkFails(self):
        msg     = self.translation['msg']
        msg_err = self.translation['msg_err']

        err_code = g_AutoupdaterShared.getErr()
        if err_code != ErrorCodes.SUCCESS:
            self.showed_success = False
            err, code = map(str, err_code)

            err_msg = ''
            
            if   err in SimplyErrorCodes:
                err_msg = msg_err[err]
            elif err in FormattedErrorCodes:
                err_msg = msg_err[err]%(code)
            else:
                err_msg = msg['unexpected']%(err, code)

            return self.htmlMsg(err_msg, color='ff0000')
        
        
        failed        = any(mod.failed != ErrorCodes.SUCCESS for mod in self.mods.values())
        updated_count = len(filter(lambda mod: bool(mod.needToUpdate), self.mods.values()))
        
        messages = ''
        
        if failed:
            self.showed_success = False
            messages += self.htmlMsg(msg['partially'], color='ff0000', size=20, nl=2)
        else:
            if updated_count:
                messages += self.htmlMsg(msg['updated']%(updated_count), color='228b22', size=20, nl=2)
            else:
                messages += self.htmlMsg(msg['no_upd'], color='228b22', size=20)
        
        for mod in self.mods.values():
            if mod.failed == ErrorCodes.SUCCESS:
                messages += self.htmlMsg(msg['mod']%(mod.name), size=16)
                messages += self.htmlMsg(msg['mod_upd'] if mod.needToUpdate else msg['no_upd'], color='228b22', size=16, nl=1)
            else:
                err, code = map(str, mod.failed)
                
                messages += self.htmlMsg(msg['mod']%(mod.name), size=16)

                err_msg = ''
                if err in SimplyErrorCodes:
                    err_msg = msg_err[err]
                elif err in FormattedErrorCodes:
                    err_msg = msg_err[err]%(code)
                else:
                    err_msg = msg['unexpected']%(err, code)
                
                messages += self.htmlMsg(err_msg, color='ffff00', size=16, nl=1)

        return messages

g_AutoupdaterGUI = AutoupdaterGUI()
