import BigWorld

from PlayerEvents import g_playerEvents

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

import json

from os      import makedirs
from os.path import exists

from time import sleep, time #debug

##AUTH_REALM = 'RU'

class Autoupdater:
    hangarSpace = dependency.descriptor(IHangarSpace)
    
    def __init__(self):
        if not exists(Constants.MOD_DIR):
            makedirs(Constants.MOD_DIR)

        self.exp = 0
        self.ID  = 0
        self.lic = ''
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, *args):
        self.ID = int(getattr(BigWorld.player(), 'databaseID', 0))
        
        if not self.ID:
            g_AutoupdaterShared.setErr(ErrorCodes.FAIL_CHECKING_ID)
            return
            
        lic_path = Paths.LIC_PATH%(self.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AutoupdaterShared.setErr(ErrorCodes.FILES_NOT_FOUND)
            return
            
        with open(lic_path, 'rb') as lic_file:
            self.lic = lic_file.read()

        if len(self.lic) != Constants.LIC_LEN:
            g_AutoupdaterShared.setErr(ErrorCodes.LIC_INVALID)
            return
        
        self.hangarSpace.onVehicleChanged += self.start
    
    def start(self, *args):
        self.hangarSpace.onVehicleChanged -= self.start
        
        if g_AutoupdaterShared.getErr() != ErrorCodes.SUCCESS: return
        
        try:
            from gui.mods.Autoupdater.GUI.Window import g_WindowCommon
            
            window = g_WindowCommon.createWindow()
            if window is not None:
                window.onWindowPopulate += self.getModsList
                return
        except Exception:
            pass
        
        self.getModsList()
    
    def getModsList(self):
        if g_AutoupdaterShared.getErr() != ErrorCodes.SUCCESS: return
        
        langID = 0
        from constants import AUTH_REALM
        if   AUTH_REALM == 'RU': langID = LangID.RU
        elif AUTH_REALM == 'CN': langID = LangID.CN
        else:                    langID = LangID.EN
        
        req_header = RequestHeader(self.ID, self.lic, Constants.GET_MODS_LIST)
        req        = Request(req_header)
        req.parse('B', langID)
        
        g_AutoupdaterEvents.onModsProcessingStart()
        
        resp = ModsListResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AutoupdaterShared.setErr(resp.failed, resp.code)
            return
        
        self.exp = resp.time_exp
        
        g_AutoupdaterEvents.onModsProcessingDone(self.exp, resp.failed, resp.code)
        
        mods = resp.mods
        dependencies = set()
        
        for modID in mods:
            mod = g_AutoupdaterShared.mods[modID] = Mod(mods[modID])
            mod.parseTree('./', mod.tree)
            
            dependencies.update(mod.dependencies)
        
        req_header = RequestHeader(self.ID, self.lic, Constants.GET_DEPS)
        req        = Request(req_header)
        req.parse('B', langID)
        req.parse('H', len(dependencies))
        for dependencyID in dependencies:
            req.parse('H', dependencyID)
        
        g_AutoupdaterEvents.onDepsProcessingStart()
        
        resp = DepsResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AutoupdaterShared.setErr(resp.failed, resp.code)
            return
        
        g_AutoupdaterEvents.onDepsProcessingDone(resp.failed, resp.code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = g_AutoupdaterShared.dependencies[dependencyID] = Mod(deps[dependencyID])
            dependency.parseTree('./', dependency.tree)
        
        self.getFiles(g_AutoupdaterShared.dependencies)
        self.getFiles(g_AutoupdaterShared.mods)
    
    def getFiles(self, mods):
        if g_AutoupdaterShared.getErr() != ErrorCodes.SUCCESS: return
        
        mods_count = len(mods)
        
        unpackAfterGameFini = False
        
        g_AutoupdaterEvents.onFilesProcessingStart(mods_count)
        
        i = 0
        for modID in mods:
            mod = mods[modID]
            
            req_header = RequestHeader(self.ID, self.lic, Constants.GET_FILES)
            req = Request(req_header)
            req.parse('H', int(modID))
            req.parse('I', len(mod.needToUpdate))
            for updID in mod.needToUpdate:
                #print 'updID', updID
                req.parse('I', int(updID))
            
            g_AutoupdaterEvents.onModFilesProcessingStart(i, mod.name)
            resp = FilesResponse(req.get_data(), req.get_type())
            
            g_AutoupdaterEvents.onModFilesProcessingDone(mod, i, mods_count, resp.failed, resp.code)
            
            if resp.failed == ErrorCodes.SUCCESS:
                i += 1
            elif resp.failed == ErrorCodes.FAIL_CREATING_FILE:
                unpackAfterGameFini = True
            else:
                g_AutoupdaterShared.setErr(resp.failed, resp.code)
        
        g_AutoupdaterEvents.onFilesProcessingDone(mods_count, i, unpackAfterGameFini)
        
        if unpackAfterGameFini:
            import game
            _game__fini = game.fini
            game.fini = lambda *args: self.onGameFini(_game__fini, *args)

    def onGameFini(self, func, *args):
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(Paths.EXE_HELPER_PATH, shell=True, creationflags=DETACHED_PROCESS)
        
        func(*args)
        
try:
    from gui.mods.Autoupdater.Common   import *
    from gui.mods.Autoupdater.Request  import RequestHeader, Request
    from gui.mods.Autoupdater.Response import ModsListResponse, DepsResponse, FilesResponse
    from gui.mods.Autoupdater.Shared   import g_AutoupdaterEvents, g_AutoupdaterShared
    
    g_Autoupdater = Autoupdater()
except ImportError:
    print '[CRITICAL ERROR] Autoupdater: Cannot to load mod files. Autoupdater will not loaded!'
