import xfw_loader.python as loader
AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')

from common import *
from shared import *
from dialog import *

import BigWorld
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator

from time import sleep

__all__ = ('g_WindowCommon',)

INIT_DATA = {
    "window" : {
        "title"         : g_AUGUIShared.getTitle('main'),
        "useBottomBtns" : True
    },
    "modsListPrBar" : {
        "width"    : 255,
        "height"   : 12,
        "minValue" : 0,
        "maxValue" : 100,
        "useAnim"  : True,
        "value"    : 0
    },
    "filesDataPrBar" : {
        "width"    : 255,
        "height"   : 12,
        "minValue" : 0,
        "maxValue" : 100,
        "useAnim"  : True,
        "value"    : 0
    },
    "filesTotalPrBar" : {
        "width"    : 255,
        "height"   : 12,
        "minValue" : 0,
        "maxValue" : 100,
        "useAnim"  : True,
        "value"    : 0
    },
    "autoupdCloseBtn": {
        "width"  : 100,
        "height" : 22,
        "label"  : g_AUGUIShared.getMsg('close')
    }
}

class AutoupdaterLobbyWindow(AbstractWindowView):
    def __init__(self):
        super(AutoupdaterLobbyWindow, self).__init__()
        
        self.onWindowPopulate = Event()
        
        AUMain.g_AUShared.window = self
    
    def _populate(self):
        super(AutoupdaterLobbyWindow, self)._populate()
        self.flashObject.as_setupUpdateWindow(INIT_DATA)
        
        self.onWindowPopulate()
    
    def getProgress(self, processed, total):
        if not total: return 0
        return int(100.0 * (float(processed) / float(total)))
    
    def setTitle(self, title):
        if self.flashObject is not None:
            self.flashObject.as_setTitle(title)
    
    def setExpTime(self, text):
        if self.flashObject is not None:
            self.flashObject.as_setExpTime(text)
    
    def setStatus(self, statusType, status):
        fobj = self.flashObject
        if fobj is None: return
        
        status_func = {
            'MODS_LIST' : 'ModsList',
            'DEPS'      : 'ModsList',
            'FILES'     : 'Files',
            'DEL'       : 'Files'
        }
        
        if  (isinstance(statusType, str) and statusType, str not in status_func) or \
            (isinstance(statusType, int) and statusType, str not in map(AUMain.StatusType.index, status_func)):
                raise NotImplementedError('Status type is not exists')
        
        if isinstance(statusType, int):
            statusType = AUMain.StatusType[statusType]
        
        getattr(fobj, 'as_set%sStatus'%(status_func[statusType]))(status)
    
    def setRawProgress(self, progressType, value):
        fobj = self.flashObject
        if fobj is None: return
        
        progress_func = {
            'MODS_LIST_DATA' : 'ModsList',
            'FILES_DATA'     : 'FilesData',
            'FILES_TOTAL'    : 'FilesTotal'
        }
        
        if  (isinstance(progressType, str) and progressType not in progress_func) or \
            (isinstance(progressType, int) and progressType not in map(AUMain.ProgressType.index, progress_func)):
                raise NotImplementedError('Progress type is not exists')
        
        if isinstance(progressType, int):
            progressType = AUMain.ProgressType[progressType]
        
        getattr(fobj, 'as_set%sRawProgress'%(progressType))(value)
    
    def setProgress(self, progressType, processed, total, unit):
        fobj = self.flashObject
        if fobj is None: return
        
        if isinstance(unit, int):
            unit = AUMain.DataUnits[unit] if unit in xrange(len(AUMain.DataUnits)) else ''
        
        progressValue = self.getProgress(processed, total)
        progressText  = '%s/%s %s'%(processed, total, unit)
        
        progress_func = {
            'MODS_LIST_DATA' : 'ModsList',
            'FILES_DATA'     : 'FilesData',
            'FILES_TOTAL'    : 'FilesTotal'
        }
        
        if  (isinstance(progressType, str) and progressType not in progress_func) or \
            (isinstance(progressType, int) and progressType not in map(AUMain.ProgressType.index, progress_func)):
                raise NotImplementedError('Progress type is not exists')
        
        if isinstance(progressType, int):
            progressType = AUMain.ProgressType[progressType]
        
        getattr(fobj, 'as_set%sProgress'%(progressType))(progressText, progressValue)
    
    def writeFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeFilesText(text)
    
    def writeLineFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeLineFilesText(text)
    
    def onWindowClose(self):
        AUMain.g_AUShared.window = None
        self.destroy()

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
        AUMain.g_AUEvents.onModFilesDataProcessed   += self.onFilesDataProcessed
        AUMain.g_AUEvents.onModFilesProcessingDone  += self.onModFilesProcessingDone
        AUMain.g_AUEvents.onFilesProcessingDone     += self.onFilesProcessingDone
    
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
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window.setTitle(title)
        window.setStatus('FILES', status)
        window.setRawProgress('FILES_DATA', 0)
        window.setProgress('FILES_TOTAL', 0, count, g_AUGUIShared.getMsg('mods'))
    
    def onModFilesProcessingStart(self, processed, name, isDependency):
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        key = 'dep' if isDependency else 'mod'
        window.writeFilesText('%s. %s'%(processed+1, g_AUGUIShared.getMsg(key)%(name)))
    
    def onModFilesProcessingDone(self, mod, processed, total, err, code=0):
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
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
        window.setProgress('FILES_TOTAL', processed, total, g_AUGUIShared.getMsg('mods'))
    
    def onFilesDataProcessed(self, processed, total, unit):
        window = AUMain.g_AUShared.window
        if window is not None:
            window.setProgress('FILES_DATA', processed, total, unit)
    
    def onFilesProcessingDone(self, updated, count):
        respType = AUMain.ResponseType.index('GET_FILES')
        
        window = AUMain.g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus('FILES', htmlMsg(status, color='228b22'))
        window.setRawProgress('FILES_DATA', 100)
        window.setProgress('FILES_TOTAL', updated, count, g_AUGUIShared.getMsg('mods'))
    
    def handleErr(self, *args, **kw):
        g_AUGUIShared.handleErr(*args, **kw)
    
    def createDialog(self, *args, **kw):
        simpleDialog = SimpleDialog()
        simpleDialog._submit(*args, **kw)
    
    def createDialogs(self, key, updated):
        func = lambda proceed: BigWorld.wg_quitAndStartLauncher() if proceed else None
        
        messages_titles = {
            'delete' : (g_AUGUIShared.getMsg('warn'),              g_AUGUIShared.getErrMsg('DELETING_FILE')),
            'create' : (g_AUGUIShared.getMsg('warn'),              g_AUGUIShared.getErrMsg('CREATING_FILE')),
            'update' : (g_AUGUIShared.getMsg('updated')%(updated), g_AUGUIShared.getMsg('updated_desc'))
        }
        
        if key is not None:
            title, message = messages_titles[key]
            self.createDialog(title=title, message=message, submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)

AUMain.g_AUShared.windowCommon = g_WindowCommon = WindowCommon()