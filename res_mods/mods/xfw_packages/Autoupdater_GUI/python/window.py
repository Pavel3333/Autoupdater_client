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
        return int(100.0 * (float(processed) / float(total)))
    
    def setTitle(self, title):
        self.as_setTitleS(title)
    
    def onRestartClicked(self, *args):
        BigWorld.wg_quitAndStartLauncher()
    
    def setExpTime(self, text):
        self.as_setExpTimeS(text)
    
    def setStatus(self, statusType, status):
        statuses = (
            'MODS_LIST', # 0 -> ModsList
            'DEPS',      # 1 -> ModsList
            'FILES',     # 2 -> Files
            'DEL'        # 3 -> Files
        )
        
        if isinstance(statusType, str) and statusType in statuses:
            self.as_setStatusS(statuses.index(statusType), status)
        elif isinstance(statusType, int) and statusType in xrange(len(statuses)):
            self.as_setStatusS(statusType, status)
        else:
            raise NotImplementedError('Status type is not exists')
    
    def setRawProgress(self, progressType, value):
        progresses = (
            'MODS_LIST_DATA', # 0 -> ModsList
            'FILES_DATA',     # 1 -> FilesData
            'FILES_TOTAL'     # 2 -> FilesTotal
        )
        
        if isinstance(progressType, str) and progressType in progresses:
            self.as_setRawProgressS(progresses.index(progressType), value)
        elif isinstance(progressType, int) and progressType in xrange(len(progresses)):
            self.as_setRawProgressS(progressType, value)
        else:
            raise NotImplementedError('Progress type is not exists')
    
    def setProgress(self, progressType, processed, total, unit):
        if isinstance(unit, int):
            unit = AUMain.DataUnits[unit] if unit in xrange(len(AUMain.DataUnits)) else ''
        
        progressText  = '%s/%s %s'%(processed, total, unit)
        progressValue = self.getProgress(processed, total)
        
        progresses = (
            'MODS_LIST_DATA', # 0 -> ModsList
            'FILES_DATA',     # 1 -> FilesData
            'FILES_TOTAL'     # 2 -> FilesTotal
        )
        
        if isinstance(progressType, str) and progressType in progresses:
            self.as_setProgressS(progresses.index(progressType), progressText, progressValue)
        elif isinstance(progressType, int) and progressType in xrange(len(progresses)):
            self.as_setProgressS(progressType, progressText, progressValue)
        else:
            raise NotImplementedError('Progress type is not exists')
    
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
        AUMain.g_AUEvents.onModsProcessingStart     += self.onModsProcessingStart
        AUMain.g_AUEvents.onModsDataProcessed       += self.onModsDataProcessed
        AUMain.g_AUEvents.onModsProcessingDone      += self.onModsProcessingDone
        
        AUMain.g_AUEvents.onDepsProcessingStart     += self.onDepsProcessingStart
        AUMain.g_AUEvents.onDepsDataProcessed       += self.onDepsDataProcessed
        AUMain.g_AUEvents.onDepsProcessingDone      += self.onDepsProcessingDone
        
        AUMain.g_AUEvents.onDeletingStart           += self.onDeletingStart
        AUMain.g_AUEvents.onDeletingProcessed       += self.onDeletingProcessed
        AUMain.g_AUEvents.onDeletingDone            += self.onDeletingDone
        
        AUMain.g_AUEvents.onFilesProcessingStart    += self.onFilesProcessingStart
        AUMain.g_AUEvents.onModFilesProcessingStart += self.onModFilesProcessingStart
        AUMain.g_AUEvents.onModFilesDataProcessed   += self.onModFilesDataProcessed
        AUMain.g_AUEvents.onModFilesProcessingDone  += self.onModFilesProcessingDone
        AUMain.g_AUEvents.onFilesProcessingDone     += self.onFilesProcessingDone
        
        self.countMods     = 0
        self.processedMods = 0
    
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
    
    def getWindowStatus(self, respType, isStartProc):
        key = 'procStart' if isStartProc else 'procDone'
        return g_AUGUIShared.getTitle(key, respType)
    
    def getWindowTitle(self, respType, isStartProc):
        mainTitle = g_AUGUIShared.getTitle('main')
        
        status = self.getWindowStatus(respType, isStartProc)
        if status:
            mainTitle += ': ' + status
        
        return mainTitle
    
    def onModsProcessingStart(self):
        respType = AUMain.ResponseType.index('GET_MODS_LIST')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus('MODS_LIST', status)
        window.setRawProgress('MODS_LIST_DATA', 0)
    
    def onModsDataProcessed(self, processed, total, unit):
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress('MODS_LIST_DATA', processed, total, unit)
    
    def onModsProcessingDone(self, exp_time):
        respType = AUMain.ResponseType.index('GET_MODS_LIST')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus('MODS_LIST', htmlMsg(status, color='228b22'))
        window.setRawProgress('MODS_LIST_DATA', 100)
        
        if exp_time:
            window.setExpTime('%s %s'%(g_AUGUIShared.getMsg('expires'), g_AUGUIShared.exp_time(exp_time)))
    
    def onDepsProcessingStart(self):
        respType = AUMain.ResponseType.index('GET_DEPS')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus('DEPS', status)
        window.setRawProgress('MODS_LIST_DATA', 0)
    
    def onDepsDataProcessed(self, processed, total, unit):
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress('MODS_LIST_DATA', processed, total, unit)
    
    def onDepsProcessingDone(self):
        respType = AUMain.ResponseType.index('GET_DEPS')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus('DEPS', htmlMsg(status, color='228b22'))
        window.setRawProgress('MODS_LIST_DATA', 100)
    
    def onDeletingStart(self, count):
        respType = AUMain.ResponseType.index('DEL_FILES')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus('DEL', status)
        window.setRawProgress('FILES_DATA', 0)
        window.setProgress('FILES_TOTAL', 0, count, g_AUGUIShared.getMsg('mods'))
    
    def onDeletingProcessed(self, processed, total, unit):
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress('FILES_DATA', processed, total, unit)
    
    def onDeletingDone(self, deleted, count):
        respType = AUMain.ResponseType.index('GET_FILES')
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus('FILES', htmlMsg(status, color='228b22'))
        window.setRawProgress('FILES_DATA', 100)
        window.setProgress('FILES_TOTAL', deleted, count, g_AUGUIShared.getMsg('mods'))
    
    def onFilesProcessingStart(self, count):
        print 'onFilesProcessingStart(%s)'%(count)
        
        self.processedMods = 0
        self.countMods     = count
        
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window.setTitle(title)
        window.setStatus('FILES', status)
        window.setRawProgress('FILES_DATA', 0)
        window.setProgress('FILES_TOTAL', self.processedMods, self.countMods, g_AUGUIShared.getMsg('mods'))
    
    def onModFilesProcessingStart(self, name, isDependency):
        print 'onModFilesProcessingStart(%s, %s)'%(name, isDependency)
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        key = 'dep' if isDependency else 'mod'
        window.writeFilesText('%s. %s'%(self.processedMods + 1, g_AUGUIShared.getMsg(key)%(name)))
    
    def onModFilesDataProcessed(self, processed, total, unit):
        print 'onModFilesDataProcessed(%s, %s, %s)'%(processed, total, unit)
        
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress('FILES_DATA', processed, total, unit)
    
    def onModFilesProcessingDone(self, mod, err, code=0):
        print 'onModFilesProcessingDone(%s, %s, %s)'%(mod, err, code)
        
        window = AUMain.g_AUShared.window
        if window is not None:
            color = None
            msg = ''
            
            if   err == AUMain.ErrorCode.index('SUCCESS'):
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
                msg = g_AUGUIShared.handleServerErr(err, code)
            
            window.writeLineFilesText(htmlMsg(msg, color=color))
            window.setProgress('FILES_TOTAL', self.processedMods, self.countMods, g_AUGUIShared.getMsg('mods'))
        
        if err == AUMain.ErrorCode.index('SUCCESS'):
            self.processedMods += 1
    
    def onFilesProcessingDone(self):
        print 'onFilesProcessingDone()'
        
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus('FILES', htmlMsg(status, color='228b22'))
        window.setRawProgress('FILES_DATA', 100)
        window.setProgress('FILES_TOTAL', self.processedMods, self.countMods, g_AUGUIShared.getMsg('mods'))
    
    def handleErr(self, *args, **kw):
        g_AUGUIShared.handleErr(*args, **kw)
    
    def createDialog(self, *args, **kw):
        simpleDialog = SimpleDialog()
        simpleDialog._submit(*args, **kw)
    
    def createDialogs(self, key):
        func = self.onRestartClicked if self.processedMods else None
        
        messages_titles = {
            'delete' : (g_AUGUIShared.getMsg('warn'),              g_AUGUIShared.getErrMsg('DELETE_FILE')),
            'create' : (g_AUGUIShared.getMsg('warn'),              g_AUGUIShared.getErrMsg('CREATE_FILE')),
            'update' : (g_AUGUIShared.getMsg('updated')%(self.processedMods), g_AUGUIShared.getMsg('updated_desc'))
        }
        
        if key is not None:
            title, message = messages_titles[key]
            self.createDialog(title=title, message=message, submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)

AUMain.g_AUShared.windowCommon = g_WindowCommon = WindowCommon()