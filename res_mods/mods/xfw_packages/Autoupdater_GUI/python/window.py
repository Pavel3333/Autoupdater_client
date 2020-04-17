import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

from .common import *
from .shared import *
from .dialog import *

import BigWorld
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator

from time import sleep

__all__ = ('g_WindowCommon',)

INIT_DATA = {
    "window" : {
        "width"  : 540,
        "height" : 460,
        "title"  : g_AUGUIShared.getTitle('main'),
    },
    "autoupdCloseBtn": {
        "width"  : 100,
        "height" : 22,
        "label"  : g_AUGUIShared.getMsg('close')
    },
    "autoupdRestartBtn": {
        "width"  : 100,
        "height" : 22,
        "label"  : g_AUGUIShared.getMsg('restart')
    }
}

class AutoupdaterLobbyWindowMeta(AbstractWindowView):
    def as_setupUpdateWindowS(self, settings):
        if self._isDAAPIInited():
            self.flashObject.as_setupUpdateWindow(settings)
    
    def as_setExpTimeS(self, text):
        if self._isDAAPIInited():
            self.flashObject.as_setExpTime(text)
    
    def as_setTitleS(self, text):
        if self._isDAAPIInited():
                return self.flashObject.as_setTitle(text)
    
    def as_setStatusS(self, statusType, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setStatus(statusType, text)
    
    def as_setRawProgressS(self, progressType, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setRawProgress(progressType, value)
    
    def as_setProgressS(self, progressType, text, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setProgress(progressType, text, value)
    
    def as_writeFilesTextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_writeFilesText(text)
    
    def as_writeLineFilesTextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_writeLineFilesText(text)
    
    def onWindowClose(self):
        self.destroy()

class AutoupdaterLobbyWindow(AutoupdaterLobbyWindowMeta):
    def __init__(self):
        super(AutoupdaterLobbyWindow, self).__init__()
        
        self.onWindowPopulate = AUMain.Event()
        
        AUMain.g_AUShared.window = self
    
    def _populate(self):
        super(AutoupdaterLobbyWindow, self)._populate()
        self.as_setupUpdateWindowS(INIT_DATA)
        
        self.onWindowPopulate()
    
    def getProgress(self, processed, total):
        if not total: return 0
        return int(100.0 * float(processed) / float(total))
    
    def setTitle(self, title):
        self.as_setTitleS(title)
    
    def onRestartClicked(self, *args):
        BigWorld.wg_quitAndStartLauncher()
    
    def setExpTime(self, text):
        self.as_setExpTimeS(text)
    
    def setStatus(self, status):
        # 0 -> ModsList
        # 1 -> ModsList
        # 2 -> Files
        # 3 -> Files
        self.as_setStatusS(int(AUMain.g_AUShared.respType), status)
    
    def setRawProgress(self, progressType, value):
        self.as_setRawProgressS(int(progressType), value)
    
    def setProgress(self, progressType, processed, total, unit):
        progressText  = '%s/%s %s'%(processed, total, str(unit))
        progressValue = self.getProgress(processed, total)
        
        self.as_setProgressS(int(progressType), progressText, progressValue)
    
    def writeFilesText(self, text):
        self.as_writeFilesTextS(text)
    
    def writeLineFilesText(self, text):
        self.as_writeLineFilesTextS(text)
    
    def onWindowClose(self):
        AUMain.g_AUShared.window = None
        super(AutoupdaterLobbyWindow, self).onWindowClose()

if not g_entitiesFactories.getSettings('AutoupdaterLobbyWindow'):
    g_entitiesFactories.addSettings(ViewSettings('AutoupdaterLobbyWindow', AutoupdaterLobbyWindow, 'AutoupdaterLobbyWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.VIEW_SCOPE))

class WindowCommon:
    def __init__(self):
        AUMain.g_AUEvents.onDataProcessed           += self.onDataProcessed
        
        AUMain.g_AUEvents.onModsProcessingStart     += self.onModsProcessingStart
        AUMain.g_AUEvents.onModsProcessingDone      += self.onModsProcessingDone
        
        AUMain.g_AUEvents.onDepsProcessingStart     += self.onDepsProcessingStart
        AUMain.g_AUEvents.onDepsProcessingDone      += self.onDepsProcessingDone
        
        AUMain.g_AUEvents.onDeletingStart           += self.onDeletingStart
        AUMain.g_AUEvents.onDeletingDone            += self.onDeletingDone
        
        AUMain.g_AUEvents.onFilesProcessingStart    += self.onFilesProcessingStart
        AUMain.g_AUEvents.onModFilesProcessingStart += self.onModFilesProcessingStart
        AUMain.g_AUEvents.onModFilesProcessingDone  += self.onModFilesProcessingDone
        AUMain.g_AUEvents.onFilesProcessingDone     += self.onFilesProcessingDone
        
        self.itemsCount     = 0
        self.itemsProcessed = 0
    
    def createWindow(self, handler):
        self.closeWindow()
        
        appLoader = ServicesLocator.appLoader
        if appLoader is None: return None
        
        app = appLoader.getApp()
        if app is None: return None
        
        app.loadView(SFViewLoadParams('AutoupdaterLobbyWindow'))
        
        window = AUMain.g_AUShared.window
        if window is not None:
            window.onWindowPopulate += handler
        
        return window
    
    def closeWindow(self):
        window = AUMain.g_AUShared.window
        if window is not None:
            window.onWindowClose()
    
    def getWindowStatus(self, isStartProc):
        key = 'procStart' if isStartProc else 'procDone'
        return g_AUGUIShared.getTitle(key)
    
    def getWindowTitle(self, isStartProc):
        mainTitle = g_AUGUIShared.getTitle('main')
        
        status = self.getWindowStatus(isStartProc)
        if status:
            mainTitle += ': ' + status
        
        return mainTitle
    
    def onDataProcessed(self, responseType, processed, total, unit):
        if isinstance(unit, int):
            unit = AUMain.DataUnits.__getattr__(unit)
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress(AUMain.Resp2ProgressTypeMap[int(responseType)], processed, total, unit)
    
    def onModsProcessingStart(self):
        title  = self.getWindowTitle(True)
        status = self.getWindowStatus(True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(status)
        window.setRawProgress(AUMain.ProgressType.ModsListData, 0)
    
    def onModsProcessingDone(self):
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle(False)
        status = self.getWindowStatus(False)
        
        window.setTitle(title)
        window.setStatus(htmlMsg(status, color='228b22'))
        window.setRawProgress(AUMain.ProgressType.ModsListData, 100)
        
        exp_time = AUMain.g_AUShared.exp_time
        if exp_time:
            window.setExpTime('%s %s'%(g_AUGUIShared.getMsg('expires'), g_AUGUIShared.exp_time(exp_time)))
    
    def onDepsProcessingStart(self):
        title  = self.getWindowTitle(True)
        status = self.getWindowStatus(True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(status)
        window.setRawProgress(AUMain.ProgressType.ModsListData, 0)
    
    def onDepsProcessingDone(self):
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle(False)
        status = self.getWindowStatus(False)
        
        window.setTitle(title)
        window.setStatus(htmlMsg(status, color='228b22'))
        window.setRawProgress(AUMain.ProgressType.ModsListData, 100)
    
    def onDeletingStart(self, count):
        title  = self.getWindowTitle(True)
        status = self.getWindowStatus(True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(status)
        window.setRawProgress(AUMain.ProgressType.FilesData, 0)
        window.setProgress(AUMain.ProgressType.FilesTotal, 0, count, g_AUGUIShared.getMsg('mods'))
    
    def onDeletingDone(self, deleted, count):
        title  = self.getWindowTitle(False)
        status = self.getWindowStatus(False)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(htmlMsg(status, color='228b22'))
        window.setRawProgress(AUMain.ProgressType.FilesData, 100)
        window.setProgress(AUMain.ProgressType.FilesTotal, deleted, count, g_AUGUIShared.getMsg('mods'))
    
    def onFilesProcessingStart(self, count):
        self.itemsProcessed = 0
        self.itemsCount     = count
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle(True)
        status = self.getWindowStatus(True)
        
        window.setTitle(title)
        window.setStatus(status)
        window.setRawProgress(AUMain.ProgressType.FilesData, 0)
        window.setProgress(AUMain.ProgressType.FilesTotal, self.itemsProcessed, self.itemsCount, g_AUGUIShared.getMsg('mods'))
    
    def onModFilesProcessingStart(self, name, isDependency):
        window = AUMain.g_AUShared.window
        if window is None: return
        
        key = 'dep' if isDependency else 'mod'
        window.writeFilesText('%s. %s'%(self.itemsProcessed + 1, g_AUGUIShared.getMsg(key)%(name)))
        window.setRawProgress(AUMain.ProgressType.FilesData, 0)
    
    def onModFilesProcessingDone(self, mod, err, code=0):
        window = AUMain.g_AUShared.window
        if window is not None:
            color = None
            msg = ''
            
            if err == AUMain.ErrorCode.Success:
                color = '228b22'
                
                if mod.needToDelete['file'] or mod.needToDelete['dir']:
                    msg = g_AUGUIShared.getMsg('del')
                else:
                    key = 'no_upd'
                    if mod.needToUpdate['ID']:
                        key = 'upd'
                    msg = g_AUGUIShared.getMsg(key)%(mod.version, mod.build)
            else:
                color = 'ff0000'
                print ''
                msg = g_AUGUIShared.handleServerErr(err, code)
            
            window.writeLineFilesText(htmlMsg(msg, color=color))
            window.setRawProgress(AUMain.ProgressType.FilesData, 100)
            window.setProgress(AUMain.ProgressType.FilesTotal, self.itemsProcessed, self.itemsCount, g_AUGUIShared.getMsg('mods'))
        
        if err == AUMain.ErrorCode.Success:
            self.itemsProcessed += 1
    
    def onFilesProcessingDone(self):
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle(False)
        status = self.getWindowStatus(False)
        
        window.setTitle(title)
        window.setStatus(htmlMsg(status, color='228b22'))
        window.setRawProgress(AUMain.ProgressType.FilesData, 100)
        window.setProgress(AUMain.ProgressType.FilesTotal, self.itemsProcessed, self.itemsCount, g_AUGUIShared.getMsg('mods'))
    
    def handleErr(self, *args, **kw):
        g_AUGUIShared.handleErr(*args, **kw)
    
    def createDialog(self, *args, **kw):
        simpleDialog = SimpleDialog()
        simpleDialog._submit(*args, **kw)
    
    def createDialogs(self, key):
        func = lambda proceed: BigWorld.wg_quitAndStartLauncher() if proceed else None
        
        messages_titles = {
            'delete' : (g_AUGUIShared.getMsg('warn'),                          g_AUGUIShared.getErrMsg(AUMain.ErrorCode.DeleteFile)),
            'create' : (g_AUGUIShared.getMsg('warn'),                          g_AUGUIShared.getErrMsg(AUMain.ErrorCode.CreateFile)),
            'update' : (g_AUGUIShared.getMsg('updated')%(self.itemsProcessed), g_AUGUIShared.getMsg('updated_desc'))
        }
        
        if key is not None:
            title, message = messages_titles[key]
            self.createDialog(title=title, message=message, submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)

AUMain.g_AUShared.windowCommon = g_WindowCommon = WindowCommon()