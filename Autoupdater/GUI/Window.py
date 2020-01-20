from gui.mods.Autoupdater.Common import ErrorCodes, WarningCodes, warningCodes, DataUnits, StatusType, ProgressType, Constants, Event
from gui.mods.Autoupdater.Shared import g_AutoupdaterEvents, g_AutoupdaterShared

from Common import SimplyErrorCodes, FormattedErrorCodes
from Shared import g_AutoupdaterGUIShared, htmlMsg
from Dialog import SimpleDialog

import BigWorld
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator

from time import sleep

class AutoupdaterLobbyWindow(AbstractWindowView):
    def __init__(self):
        super(AutoupdaterLobbyWindow, self).__init__()
        
        self.onWindowPopulate = Event()
        g_AutoupdaterShared.window = self
    
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
        if   statusType == StatusType.MODS_LIST or statusType == StatusType.DEPS:
            fobj.as_setModsListStatus(status)
        elif statusType == StatusType.FILES:
            fobj.as_setFilesStatus(status)
        else:
            raise NotImplementedError('Status type is not exists')
    
    def setRawProgress(self, progressType, value):
        fobj = self.flashObject
        if fobj is None: return
        #print 'setRawProgress', progressType, value
        if   progressType == ProgressType.MODS_LIST_DATA:
            fobj.as_setModsListRawProgress(value)
        elif progressType == ProgressType.FILES_DATA:
            fobj.as_setFilesDataRawProgress(value)
        elif progressType == ProgressType.FILES_TOTAL:
            fobj.as_setFilesTotalRawProgress(value)
        else:
            raise NotImplementedError('Progress type is not exists')
    
    def setProgress(self, progressType, processed, total, unit):
        fobj = self.flashObject
        if fobj is None: return

        curr_unit = unit if isinstance(unit, str) else Constants.DATA_UNITS.get(unit, '')
        
        progressValue = self.getProgress(processed, total)
        progressText  = '%s/%s %s'%(processed, total, curr_unit)
        #print 'setProgress', progressText, progressValue
        if   progressType == ProgressType.MODS_LIST_DATA:
            fobj.as_setModsListProgress(progressText, progressValue)
        elif progressType == ProgressType.FILES_DATA:
            fobj.as_setFilesDataProgress(progressText, progressValue)
        elif progressType == ProgressType.FILES_TOTAL:
            fobj.as_setFilesTotalProgress(progressText, progressValue)
        else:
            raise NotImplementedError('Progress type is not exists')
    
    def writeFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeFilesText(text)
    
    def writeLineFilesText(self, text):
        if self.flashObject is not None:
            self.flashObject.as_writeLineFilesText(text)
    
    def onWindowClose(self):
        g_AutoupdaterShared.window = None
        self.destroy()

if not g_entitiesFactories.getSettings('AutoupdaterLobbyWindow'):
    g_entitiesFactories.addSettings(ViewSettings('AutoupdaterLobbyWindow', AutoupdaterLobbyWindow, 'AutoupdaterLobbyWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.VIEW_SCOPE))

class WindowCommon:
    def __init__(self):
        g_AutoupdaterEvents.onModsProcessingStart     += self.onModsProcessingStart
        g_AutoupdaterEvents.onModsDataProcessed       += self.onModsDataProcessed
        g_AutoupdaterEvents.onModsProcessingDone      += self.onModsProcessingDone
        
        g_AutoupdaterEvents.onDepsProcessingStart     += self.onDepsProcessingStart
        g_AutoupdaterEvents.onDepsDataProcessed       += self.onDepsDataProcessed
        g_AutoupdaterEvents.onDepsProcessingDone      += self.onDepsProcessingDone
        
        g_AutoupdaterEvents.onFilesProcessingStart    += self.onFilesProcessingStart
        g_AutoupdaterEvents.onModFilesProcessingStart += self.onModFilesProcessingStart
        g_AutoupdaterEvents.onModFilesDataProcessed   += self.onFilesDataProcessed
        g_AutoupdaterEvents.onModFilesProcessingDone  += self.onModFilesProcessingDone
        g_AutoupdaterEvents.onFilesProcessingDone     += self.onFilesProcessingDone
        
    def createWindow(self):
        self.closeWindow()
        
        appLoader = ServicesLocator.appLoader
        if appLoader is None: return None
        
        app = appLoader.getApp()
        if app is None: return None
        
        app.loadView(SFViewLoadParams('AutoupdaterLobbyWindow'))
        
        return g_AutoupdaterShared.window

    def closeWindow(self):
        window = g_AutoupdaterShared.window
        if window is not None:
            window.onWindowClose()
    
    def getWindowStatus(self, respType, isStartProc):
        key = 'procStart' if isStartProc else 'procDone'
        return g_AutoupdaterGUIShared.translation['titles'][key].get(str(respType), '')
    
    def getWindowTitle(self, respType, isStartProc):
        mainTitle = g_AutoupdaterGUIShared.translation['titles']['main']
        status = self.getWindowStatus(respType, isStartProc)
        
        if status:
            return mainTitle + ': ' + status
        else:
            return mainTitle
    
    def onModsProcessingStart(self):
        respType = Constants.GET_MODS_LIST
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.MODS_LIST, status)
        window.setRawProgress(ProgressType.MODS_LIST_DATA, 0)
        
        #sleep(5)
    
    def onModsDataProcessed(self, processed, total, unit):
        window = g_AutoupdaterShared.window
        if window is not None:
            window.setProgress(ProgressType.MODS_LIST_DATA, processed, total, unit)
            #sleep(1)
    
    def onModsProcessingDone(self, exp_time, err, code):
        respType = Constants.GET_MODS_LIST
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        translation = g_AutoupdaterGUIShared.translation
        
        msg      = translation['msg']
        msg_warn = translation['msg_warn']
        
        err_s  = str(err)
        code_s = str(code)
        err_msg = ''
        
        if err == ErrorCodes.FAIL_GETTING_MODS:
            if code_s in warningCodes:
                err_msg = msg_warn[code_s]
                if code in (
                    WarningCodes.USER_NOT_FOUND,
                    WarningCodes.TIME_EXPIRED
                    ):
                    simpleDialog = SimpleDialog()
                    
                    key = 'subscribe'
                    if code == WarningCodes.TIME_EXPIRED:
                        key = 'renew'
                    
                    simpleDialog._submit(title=msg['warn'], message=err_msg, submit=msg[key], close=msg['close'], url='https://pavel3333.ru/trajectorymod/lk')
            else:
                err_msg = msg['unexpected']%(err, code)
            
            window.setStatus(StatusType.MODS_LIST, htmlMsg(msg['warn'] + ' ' + err_msg, color='ff0000'))
            return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus(StatusType.MODS_LIST, htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.MODS_LIST_DATA, 100)

        if exp_time:
            window.setExpTime('%s %s'%(msg['expires'], g_AutoupdaterGUIShared.exp_time(exp_time)))
        
        #sleep(5)
    
    def onDepsProcessingStart(self):
        respType = Constants.GET_DEPS
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.DEPS, status)
        window.setRawProgress(ProgressType.MODS_LIST_DATA, 0)
        
        #sleep(5)
    
    def onDepsDataProcessed(self, processed, total, unit):
        window = g_AutoupdaterShared.window
        if window is not None:
            window.setProgress(ProgressType.MODS_LIST_DATA, processed, total, unit)
            #sleep(1)
    
    def onDepsProcessingDone(self, err, code):
        respType = Constants.GET_DEPS
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        translation = g_AutoupdaterGUIShared.translation
        
        msg      = translation['msg']
        msg_warn = translation['msg_warn']
        
        err_s  = str(err)
        code_s = str(code)
        err_msg = ''
        
        if err == ErrorCodes.FAIL_GETTING_DEPS:
            if code_s in warningCodes:
                err_msg = msg_warn[code_s]
                if code in (
                    WarningCodes.USER_NOT_FOUND,
                    WarningCodes.TIME_EXPIRED
                    ):
                    simpleDialog = SimpleDialog()
                    
                    key = 'subscribe'
                    if code == WarningCodes.TIME_EXPIRED:
                        key = 'renew'
                    
                    simpleDialog._submit(title=msg['warn'], message=err_msg, submit=msg[key], close=msg['close'], url='https://pavel3333.ru/trajectorymod/lk')
            else:
                err_msg = msg['unexpected']%(err, code)
            
            window.setStatus(StatusType.DEPS, htmlMsg(msg['warn'] + ' ' + err_msg, color='ff0000'))
            return
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window.setTitle(title)
        window.setStatus(StatusType.DEPS, htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.MODS_LIST_DATA, 100)
        
        #sleep(5)
    
    def onFilesProcessingStart(self, mods_cnt):
        respType = Constants.GET_FILES
        
        title  = self.getWindowTitle( respType, True)
        status = self.getWindowStatus(respType, True)
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        window.setTitle(title)
        window.setStatus(StatusType.FILES, status)
        window.setRawProgress(ProgressType.FILES_DATA, 0)
        window.setProgress(ProgressType.FILES_TOTAL, 0, mods_cnt, g_AutoupdaterGUIShared.translation['msg']['mods'])
        
        #sleep(5)
    
    def onModFilesProcessingStart(self, i, name, isDependency):
        respType = Constants.GET_FILES
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        key = 'dep' if isDependency else 'mod'
        msg = g_AutoupdaterGUIShared.translation['msg'][key]%(name)
        window.writeFilesText('%s. %s'%(i+1, msg))
        
        #sleep(5)
    
    def onModFilesProcessingDone(self, mod, processed, total, err, code=0):
        respType = Constants.GET_FILES
        
        window = g_AutoupdaterShared.window
        if window is None: return
        
        translation = g_AutoupdaterGUIShared.translation
        
        msg     = translation['msg']
        msg_err = translation['msg_err']
        
        color = None
        err_s = str(err)
        err_msg = ''
        
        if   err == ErrorCodes.SUCCESS:
            color = '228b22'
            
            key = 'mod_upd' if mod.needToUpdate else 'no_upd'
            err_msg = msg[key]%(mod.version, mod.build)
        else:
            color = 'ff0000'
            if err_s in SimplyErrorCodes:
                err_msg = msg_err[err_s]
            elif err_s in FormattedErrorCodes:
                err_msg = msg_err[err_s]%(code)
            else:
                err_msg = msg['unexpected']%(err, code)
        
        window.writeLineFilesText(htmlMsg(err_msg, color=color))
        window.setProgress(ProgressType.FILES_TOTAL, processed, total, g_AutoupdaterGUIShared.translation['msg']['mods'])
        
        #sleep(5)
    
    def onFilesDataProcessed(self, processed, total, unit):
        window = g_AutoupdaterShared.window
        if window is not None:
            window.setProgress(ProgressType.FILES_DATA, processed, total, unit)
            #sleep(1)
    
    def onFilesProcessingDone(self, mods_cnt, updated, unpackAfterGameFini):
        respType = Constants.GET_FILES
        
        title  = self.getWindowTitle( respType, False)
        status = self.getWindowStatus(respType, False)
        
        window = g_AutoupdaterShared.window
        window.setTitle(title)
        window.setStatus(StatusType.FILES, htmlMsg(status, color='228b22'))
        window.setRawProgress(ProgressType.FILES_DATA, 100)
        window.setProgress(ProgressType.FILES_TOTAL, mods_cnt, mods_cnt, g_AutoupdaterGUIShared.translation['msg']['mods'])
        
        translation = g_AutoupdaterGUIShared.translation
        
        msg     = translation['msg']
        msg_err = translation['msg_err']

        func = lambda proceed: self.onDialogProceed() if proceed else None
        
        simpleDialog = SimpleDialog()
        
        if unpackAfterGameFini:
            simpleDialog._submit(title=msg['warn'], message=msg_err[str(ErrorCodes.FAIL_CREATING_FILE)], submit=msg['restart'], close=msg['close'], func=func)
        elif updated:
            simpleDialog._submit(title=msg['updated']%(mods_cnt), message=msg['updated_desc'], submit=msg['restart'], close=msg['close'], func=func)
        #sleep(5)
        
        #window.onWindowClose()
    def onDialogProceed(self):
        BigWorld.wg_quitAndStartLauncher()

g_WindowCommon = WindowCommon()

INIT_DATA = {
    "window": {
        "title": g_AutoupdaterGUIShared.translation['titles']['main'],
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
        "label":g_AutoupdaterGUIShared.translation['msg']['close']
    }
}

#def lobbyPopulate(func, *args):
#    g_WindowCommon.createWindow()
#    func(*args)

#from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView

#_LobbyView__populate = LobbyView._populate
#LobbyView._populate = lambda *args: lobbyPopulate(_LobbyView__populate, *args)
