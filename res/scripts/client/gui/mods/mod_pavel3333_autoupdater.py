import BigWorld
import BattleReplay

from PlayerEvents import g_playerEvents

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

import json

from os      import listdir, makedirs, remove, rmdir
from os.path import exists, isfile

class Autoupdater:
    hangarSpace = dependency.descriptor(IHangarSpace)
    
    def __init__(self):
        for directory in Directories.values():
            if not exists(directory):
                makedirs(directory)

        self.exp = 0 # AHHH SHIT MOVE IT TO CYTHON PLS
        self.ID  = 0
        self.lic = ''
        
        self.langID = LangID.index(AUTH_REALM) if AUTH_REALM in LangID else LangID.index('EU')
        
        self.finiHooked = False
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, ctx, *args):
        self.ID = ctx.get('databaseID', 0)
        
        if not self.ID:
            g_AUShared.setErr(ErrorCode.index('CHECKING_ID'))
            return
            
        lic_path = Paths.LIC_PATH%(self.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AUShared.setErr(ErrorCode.index('FILES_NOT_FOUND'))
            return
            
        with open(lic_path, 'rb') as lic_file:
            self.lic = lic_file.read()

        if len(self.lic) != Constants.LIC_LEN:
            g_AUShared.setErr(ErrorCode.index('LIC_INVALID'))
            return
        
        self.hangarSpace.onHeroTankReady += self.start
    
    def start(self, *args):
        self.hangarSpace.onHeroTankReady -= self.start
        
        if g_AUShared.getErr() != ErrorCode.index('SUCCESS'): return
        
        #try:
        from gui.mods.Autoupdater.GUI.Window import g_WindowCommon
        
        window = g_WindowCommon.createWindow()
        if window is not None:
            window.onWindowPopulate += self.getModsList
            return
        #except Exception:
        #    g_AUShared.logger.log('Unable to load GUI module')
        
        self.getModsList()
    
    def getModsList(self):
        if g_AUShared.getErr() != ErrorCode.index('SUCCESS'): return
        
        respType = ResponseType.index('GET_MODS_LIST')
        
        req_header = RequestHeader(self.ID, self.lic, respType)
        req        = Request(req_header)
        req.parse('B', self.langID)
        
        g_AUEvents.onModsProcessingStart()
        
        resp = ModsListResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AUShared.setErr(resp.failed, resp.code)
            return
        
        self.exp = resp.time_exp
        
        g_AUEvents.onModsProcessingDone(self.exp)
        g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        self.getDepsList(resp.mods)
    
    def getDepsList(self, mods):
        if g_AUShared.getErr() != ErrorCode.index('SUCCESS'): return
        
        respType = ResponseType.index('GET_DEPS')
        
        dependencies = set()
        
        toUpdate = set()
        toDelete = {
            'file' : set(),
            'dir'  : set()
        }
        
        for modID in mods:
            mod = g_AUShared.mods[modID] = Mod(mods[modID])
            mod.parseTree('./', mod.tree)
            
            dependencies.update(mod.dependencies)
            
            toUpdate.update(mod.needToUpdate['file'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['del'])
        
        req_header = RequestHeader(self.ID, self.lic, respType)
        req        = Request(req_header)
        req.parse('B', self.langID)
        req.parse('H', len(dependencies))
        for dependencyID in dependencies:
            req.parse('H', dependencyID)
        
        g_AUEvents.onDepsProcessingStart()
        
        resp = DepsResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AUShared.setErr(resp.failed, resp.code)
            return
        
        g_AUEvents.onDepsProcessingDone()
        g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = g_AUShared.dependencies[dependencyID] = Mod(deps[dependencyID])
            dependency.parseTree('./', dependency.tree)
            
            toUpdate.update(dependency.needToUpdate['file'])
            toDelete['file'].update(dependency.needToDelete['file'])
            toDelete['dir'].update(dependency.needToDelete['del'])
        
        toDelete['file'] -= toUpdate['file']
        toDelete['dir']  -= toUpdate['dir']
        
        toDelete['file'] -= DeleteExclude['file']
        toDelete['dir']  -= DeleteExclude['dir']
        
        toDelete['dir'] = sorted(
            toDelete['dir'],
            key = getLevels,
            reverse = True
        )
        
        print 'toDelete["dir"]', toDelete['dir']
        
        self.delFiles(toDelete)
    
    def delFiles(self, paths):
        if g_AUShared.getErr() != ErrorCode.index('SUCCESS'): return
        
        paths_count = len(paths['file']) + len(paths['dir'])
        
        undeletedPaths = []
        
        g_AUEvents.onDeletingStart(paths_count)
        
        i = 0
        for path in paths['file']:
            if exists(path):
                try:
                    remove(path)
                    i += 1
                except Exception:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete file %s'%(path))
                    g_AUShared.setErr(ErrorCode.index('DELETING_FILE'))
            else:
                g_AUShared.logger.log('File %s is not exists'%(path))
        
        for path in paths['dir']:
            if exists(path) and not listdir(path):
                try:
                    rmdir(path)
                    i += 1
                except Exception:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s'%(path))
                    g_AUShared.setErr(ErrorCode.index('DELETING_FILE'))
            else:
                g_AUShared.logger.log('Directory %s is not exists'%(path))
        
        deleteAfterFini = bool(g_AUShared.undeletedPaths)
        
        g_AUEvents.onDeletingDone(paths_count, i, deleteAfterFini)
        
        if deleteAfterFini:
            with open(Paths.DELETED_PATH, 'wb') as fil:
                for path in g_AUShared.undeletedPaths:
                    fil.write(path + '\n')
            self.hookFini()
        
        self.getFiles(g_AUShared.dependencies)
        self.getFiles(g_AUShared.mods)
    
    def getFiles(self, mods):
        if g_AUShared.getErr() != ErrorCode.index('SUCCESS'): return
        
        mods_count = len(mods)
        
        unpackAfterFini = False
        
        g_AUEvents.onFilesProcessingStart(mods_count)
        
        i = 0
        for modID in mods:
            mod = mods[modID]
            
            req_header = RequestHeader(self.ID, self.lic, ResponseType.index('GET_FILES'))
            req = Request(req_header)
            req.parse('H', int(modID))
            req.parse('I', len(mod.needToUpdate['ID']))
            for updID in mod.needToUpdate['ID']:
                req.parse('I', int(updID))
            
            g_AUEvents.onModFilesProcessingStart(i, mod.name)
            resp = FilesResponse(req.get_data(), req.get_type())
            
            g_AUEvents.onModFilesProcessingDone(mod, i, mods_count, resp.failed, resp.code)
            
            if resp.failed == ErrorCode.index('SUCCESS'):
                i += 1
            elif resp.failed == ErrorCode.index('CREATING_FILE'):
                unpackAfterFini = True
            else:
                g_AUShared.setErr(resp.failed, resp.code)
        
        g_AUEvents.onFilesProcessingDone(mods_count, i, unpackAfterFini)
        
        if unpackAfterFini: self.hookFini()
    
    def hookFini(self):
        if self.finiHooked: return
        
        try:
            import game
            _game__fini = game.fini
            game.fini = lambda *args: self.onGameFini(_game__fini, *args)
            self.finiHooked = True
        except:
            g_AUShared.logger.log('Unable to hook fini')
    
    def onGameFini(self, func, *args):
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(Paths.EXE_HELPER_PATH, shell=True, creationflags=DETACHED_PROCESS)
        
        func(*args)
    
try:
    from gui.mods.Autoupdater import *
    
    if not BattleReplay.isPlaying():
        g_Autoupdater = Autoupdater()
except ImportError:
    print '[CRITICAL ERROR] Autoupdater: Unable to load mod files. Autoupdater will not loaded!'
