import BigWorld

import re
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.SystemMessages import SM_TYPE, pushMessage
from notification.settings import NOTIFICATION_TYPE
from notification.actions_handlers import NotificationsActionsHandlers

import json

from gui.mods.Autoupdater import *

class AutoupdaterGUI:
    def __init__(self):
        self.window       = None
    
        self.battles_ctr    = 0
        self.showed_info    = 0
        self.showed_success = False
        
        g_AUEvents.onDataProcessed        += self.onDataProcessed
        g_AUEvents.onModsProcessingStart  += self.onModsProcessingStart
        g_AUEvents.onModsProcessingDone   += self.onModsProcessingDone
        g_AUEvents.onDepsProcessingStart  += self.onDepsProcessingStart
        g_AUEvents.onDepsProcessingDone   += self.onDepsProcessingDone
        g_AUEvents.onFilesProcessingStart += self.onFilesProcessingStart
        g_AUEvents.onFilesProcessingDone  += self.onFilesProcessingDone
        
        # Hooks
        _NotificationsActionsHandlers__handleAction = NotificationsActionsHandlers.handleAction
        NotificationsActionsHandlers.handleAction = lambda *args: self.handleAction(_NotificationsActionsHandlers__handleAction, *args)
        
        _LobbyView__populate = LobbyView._populate
        LobbyView._populate = lambda *args: self.lobbyPopulate(_LobbyView__populate, *args)

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
            g_AUShared.logger.log(message)
            
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
        err_code = g_AUShared.getErr()
        if err_code != ErrorCode.index('SUCCESS'):
            self.showed_success = False
            err, code = err_code
            
            return self.htmlMsg(g_AUGUIShared.handleServerErr(err, code), color='ff0000')
        
        
        failed        = any(mod.failed != ErrorCode.index('SUCCESS') for mod in self.mods.values())
        updated_count = len(filter(lambda mod: bool(mod.needToUpdate), self.mods.values()))
        deleted_count = len(filter(lambda mod: bool(mod.needToDelete), self.mods.values()))
        
        messages = ''
        
        if failed:
            self.showed_success = False
            messages += self.htmlMsg(g_AUGUIShared.getMsg('partially'), color='ff0000', size=20, nl=2)
        else:
            message = g_AUGUIShared.getMsg('success')
            if updated_count or deleted_count:
                message = g_AUGUIShared.getMsg('success')
                if updated_count:
                    message += ' ' + g_AUGUIShared.getMsg('updated')%(updated_count) + ';'
                if deleted_count:
                    message += ' ' + g_AUGUIShared.getMsg('updated')%(deleted_count) + ';'
                messages += self.htmlMsg(message, color='228b22', size=20, nl=2)
            else:
                messages += self.htmlMsg(g_AUGUIShared.getMsg('not_updated'), color='228b22', size=20)
        
        for mod in self.mods.values():
            if mod.failed == ErrorCode.index('SUCCESS'):
                messages += self.htmlMsg(g_AUGUIShared.getMsg('mod')%(mod.name), size=16)
                messages += self.htmlMsg(g_AUGUIShared.getMsg('mod_upd') if mod.needToUpdate else g_AUGUIShared.getMsg('no_upd'), color='228b22', size=16, nl=1)
            else:
                err, code = mod.failed
                
                messages += self.htmlMsg(g_AUGUIShared.getMsg('mod')%(mod.name), size=16)
                messages += self.htmlMsg(g_AUGUIShared.handleServerErr(err, code), color='ffff00', size=16, nl=1)

        return messages

g_AutoupdaterGUI = AutoupdaterGUI()
