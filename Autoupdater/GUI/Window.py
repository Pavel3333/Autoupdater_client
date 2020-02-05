from gui.mods.Autoupdater import *

from Common import *
from Shared import *
from Dialog import *

import BigWorld
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator

from time import sleep

__all__ = ('g_WindowCommon',)

INIT_DATA = {
    "window": {
        "title": g_AUGUIShared.getTitle('main'),
        "useBottomBtns": True
    },
    "modsListPrBar": {
        "width":255,
        "height":12,
        "minValue": 0,
        "maxValue": 100,
        "useAnim": True,
        "value": 0
    },
    "filesDataPrBar": {
        "width":255,
        "height":12,
        "minValue": 0,
        "maxValue": 100,
        "useAnim": True,
        "value": 0
    },
    "filesTotalPrBar": {
        "width":255,
        "height":12,
        "minValue": 0,
        "maxValue": 100,
        "useAnim": True,
        "value": 0
    },
    "autoupdCloseBtn": {
        "width":100,
        "height":22,
        "label":g_AUGUIShared.getMsg('close')
    }
}

class AutoupdaterLobbyWindow(AbstractWindowView):
    def __init__(self):
        super(AutoupdaterLobbyWindow, self).__init__()
        
        self.onWindowPopulate = Event()
        g_AUShared.window = self
    
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
            StatusType.index('MODS_LIST') : 'ModsList',
            StatusType.index('DEPS')      : 'ModsList',
            StatusType.index('FILES')     : 'Files',
            StatusType.index('DEL')       : 'Files'
        }
        
        if statusType in status_func:
            getattr(fobj, 'as_set%sStatus'%(status_func[statusType]))(status)
        else:
            raise NotImplementedError('Status type is not exists')
    
    def setRawProgress(self, progressType, value):
        fobj = self.flashObject
        if fobj is None: return
        
        progress_func = {
            ProgressType.index('MODS_LIST_DATA') : 'ModsList',
            ProgressType.index('FILES_DATA')     : 'FilesData',
            ProgressType.index('FILES_TOTAL')    : 'FilesTotal'
        }
        
        if progressType in progress_func:
            getattr(fobj, 'as_set%sRawProgress'%(progress_func[progressType]))(value)
        else:
            raise NotImplementedError('Progress type is not exists')
    
    def setProgress(self, progressType, processed, total, unit):
        fobj = self.flashObject
        if fobj is None: return
        
        if isinstance(unit, int):
            unit = DataUnits[unit] if unit < len(DataUnits) else ''
        
        progressValue = self.getProgress(processed, total)
        progressText  = '%s/%s %s'%(processed, total, unit)
        
        progress_func = {
            ProgressType.index('MODS_LIST_DATA') : 'ModsList',
            ProgressType.index('FILES_DATA')     : 'FilesData',
            ProgressType.index('FILES_TOTAL')    : 'FilesTotal'
        }
        
        if progressType in progress_func:
            getattr(fobj, 'as_set%sProgress'%(progress_func[progressType]))(progressText, progressValue)
        else:
            raise NotImplementedError('Progress type is not exists')
    
    def writeFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeFilesText(text)
    
    def writeLineFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeLineFilesText(text)
    
    def onWindowClose(self):
        g_AUShared.window = None
        self.destroy()

if not g_entitiesFactories.getSettings('AutoupdaterLobbyWindow'):
    g_entitiesFactories.addSettings(ViewSettings('AutoupdaterLobbyWindow', AutoupdaterLobbyWindow, 'AutoupdaterLobbyWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.VIEW_SCOPE))

class WindowCommon:
    def __init__(self):
        g_AUEvents.onModsProcessingStart     += self.onModsProcessingStart
        g_AUEvents.onModsDataProcessed       += self.onModsDataProcessed
        g_AUEvents.onModsProcessingDone      += self.onModsProcessingDone
        
        g_AUEvents.onDepsProcessingStart     += self.onDepsProcessingStart
        g_AUEvents.onDepsDataProcessed       += self.onDepsDataProcessed
        g_AUEvents.onDepsProcessingDone      += self.onDepsProcessingDone
        
        g_AUEvents.onDeletingStart           += self.onDeletingStart
        g_AUEvents.onDeletingProcessed       += self.onDeletingProcessed
        g_AUEvents.onDeletingDone            += self.onDeletingDone
        
        g_AUEvents.onFilesProcessingStart    += self.onFilesProcessingStart
        g_AUEvents.onModFilesProcessingStart += self.onModFilesProcessingStart
        g_AUEvents.onModFilesDataProcessed   += self.onFilesDataProcessed
        g_AUEvents.onModFilesProcessingDone  += self.onModFilesProcessingDone
        g_AUEvents.onFilesProcessingDone     += self.onFilesProcessingDone
        
    def createWindow(self):
        self.closeWindow()
        
        appLoader = ServicesLocator.appLoader
        if appLoader is None: return None
        
        app = appLoader.getApp()
        if app is None: return None
        
        app.loadView(SFViewLoadParams('AutoupdaterLobbyWindow'))
        
        return g_AUShared.window

    def closeWindow(self):
        window = g_AUShared.window
        if window is not None:
            window.onWindowClose()
    
    def getWindowStatus(self, respType, isStartProc):
        key = 'procStart' if isStartProc else 'procDone'
        return g_AUGUIShared.getTitle(key, respType)
    
    def getWindowTitle(self, respType, isStartProc):
        g_AUGUIShared.getTitle('main')
        status = self.getWindowStatus(respType, isStartProc)
        
        if status:
            return mainTitle + ': ' + status
        else:
            return mainTitle
    
    def onModsProcessingStart(self):
        respType = ResponseType.index('GET_MODS_LIST')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.index('MODS_LIST'), status)
        window.setRawProgress(ProgressType.index('MODS_LIST_DATA'), 0)
    
    def onModsDataProcessed(self, processed, total, unit):
        window = g_AUShared.window
        if window is not None:
            window.setProgress(ProgressType.index('MODS_LIST_DATA'), processed, total, unit)
    
    def onModsProcessingDone(self, exp_time):
        respType = ResponseType.index('GET_MODS_LIST')
        
        window = g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus(StatusType.index('MODS_LIST'), htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.index('MODS_LIST_DATA'), 100)

        if exp_time:
            window.setExpTime('%s %s'%(g_AUGUIShared.getMsg('expires'), g_AUGUIShared.exp_time(exp_time)))
    
    def onDepsProcessingStart(self):
        respType = ResponseType.index('GET_DEPS')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.index('DEPS'), status)
        window.setRawProgress(ProgressType.index('MODS_LIST_DATA'), 0)
    
    def onDepsDataProcessed(self, processed, total, unit):
        window = g_AUShared.window
        if window is not None:
            window.setProgress(ProgressType.index('MODS_LIST_DATA'), processed, total, unit)
    
    def onDepsProcessingDone(self):
        respType = ResponseType.index('GET_DEPS')
        
        window = g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus(StatusType.index('DEPS'), htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.index('MODS_LIST_DATA'), 100)
    
    def onDeletingStart(self, count):
        respType = ResponseType.index('DEL_FILES')
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.index('DEL'), status)
        window.setRawProgress(ProgressType.index('FILES_DATA'), 0)
        window.setProgress(ProgressType.index('FILES_TOTAL'), 0, count, g_AUGUIShared.getMsg('mods'))
    
    def onDeletingProcessed(self, processed, total, unit):
        window = g_AUShared.window
        if window is not None:
            window.setProgress(ProgressType.index('FILES_DATA'), processed, total, unit)
    
    def onDeletingDone(self, count, deleteAfterFini):
        respType = ResponseType.index('GET_FILES')
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window = g_AUShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.index('FILES'), htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.index('FILES_DATA'), 100)
        window.setProgress(ProgressType.index('FILES_TOTAL'), count, count, g_AUGUIShared.getMsg('mods'))

        func = lambda proceed: self.onDialogProceed() if proceed else None
        
        if deleteAfterFini:
            self.createDialog(title=g_AUGUIShared.getMsg('warn'), message=g_AUGUIShared.getErrMsg('DELETING_FILE'), submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)
    
    def onFilesProcessingStart(self, mods_cnt):
        respType = ResponseType.index('GET_FILES')
        
        window = g_AUShared.window
        if window is None: return
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window.setTitle(title)
        window.setStatus(StatusType.index('FILES'), status)
        window.setRawProgress(ProgressType.index('FILES_DATA'), 0)
        window.setProgress(ProgressType.index('FILES_TOTAL'), 0, mods_cnt, g_AUGUIShared.getMsg('mods'))
    
    def onModFilesProcessingStart(self, i, name, isDependency):
        respType = ResponseType.index('GET_FILES')
        
        window = g_AUShared.window
        if window is None: return
        
        key = 'dep' if isDependency else 'mod'
        window.writeFilesText('%s. %s'%(i+1, g_AUGUIShared.getMsg(key)%(name)))
    
    def onModFilesProcessingDone(self, mod, processed, total, err, code=0):
        respType = ResponseType.index('GET_FILES')
        
        window = g_AUShared.window
        if window is None: return
        
        color = None
        msg = ''
        
        if   err == ErrorCode.index('SUCCESS'):
            color = '228b22'
            
            if mod.needToDelete:
                msg = g_AUGUIShared.getMsg('del')
            else:
                key = 'no_upd'
                if mod.needToUpdate:
                    key = 'upd'
                msg = g_AUGUIShared.getMsg(key)%(mod.version, mod.build)
        else:
            color = 'ff0000'
            msg = g_AUGUIShared.handleServerErr(err, code)
        
        window.writeLineFilesText(htmlMsg(msg, color=color))
        window.setProgress(ProgressType.index('FILES_TOTAL'), processed, total, g_AUGUIShared.getMsg('mods'))
    
    def onFilesDataProcessed(self, processed, total, unit):
        window = g_AUShared.window
        if window is not None:
            window.setProgress(ProgressType.index('FILES_DATA'), processed, total, unit)
    
    def onFilesProcessingDone(self, mods_cnt, updated, unpackAfterGameFini):
        respType = ResponseType.index('GET_FILES')
        
        window = g_AUShared.window
        if window is not None:
            title  = self.getWindowTitle( respType, False)
            status = self.getWindowStatus(respType, False)
            
            window.setTitle(title)
            window.setStatus(StatusType.index('FILES'), htmlMsg(status, color='228b22'))
            window.setRawProgress(ProgressType.index('FILES_DATA'), 100)
            window.setProgress(ProgressType.index('FILES_TOTAL'), mods_cnt, mods_cnt, g_AUGUIShared.getMsg('mods'))

        func = lambda proceed: BigWorld.wg_quitAndStartLauncher() if proceed else None
        
        if unpackAfterGameFini:
            self.createDialog(title=g_AUGUIShared.getMsg('warn'), message=g_AUGUIShared.getErrMsg('CREATING_FILE'), submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)
        elif updated:
            self.createDialog(title=g_AUGUIShared.getMsg('updated')%(mods_cnt), message=g_AUGUIShared.getMsg('updated_desc'), submit=g_AUGUIShared.getMsg('restart'), close=g_AUGUIShared.getMsg('close'), func=func)
        
    def createDialog(self, *args, **kw):
        simpleDialog = SimpleDialog()
        simpleDialog._submit(*args, **kw)

g_WindowCommon = WindowCommon()