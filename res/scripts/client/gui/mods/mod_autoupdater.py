import BigWorld
import BattleReplay

from PlayerEvents import g_playerEvents

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

import json
import sys

from os      import listdir, makedirs, remove, rmdir
from os.path import exists, isfile

class Autoupdater:
    hangarSpace = dependency.descriptor(IHangarSpace)
    
    def __init__(self):
        for directory in AUMain.Directory.values():
            if not exists(directory):
                makedirs(directory)

        self.exp = 0 # AHHH SHIT MOVE IT TO CYTHON PLS
        self.ID  = 0
        self.lic = ''
        
        self.langID = AUMain.getLangID()
        
        self.unpackAfterFini = False
        self.deleteAfterFini = False
        self.finiHooked      = False
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, ctx, *args):
        self.ID = ctx.get('databaseID', 0)
        
        if not self.ID:
            AUMain.g_AUShared.fail('CHECKING_ID')
            return
            
        lic_path = AUMain.Paths.LIC_PATH%(self.ID^0xb7f5cba9)
        if not exists(lic_path):
            AUMain.g_AUShared.fail('FILES_NOT_FOUND')
            return
            
        with open(lic_path, 'rb') as lic_file:
            self.lic = lic_file.read()

        if len(self.lic) != AUMain.Constants.LIC_LEN:
            AUMain.g_AUShared.fail('LIC_INVALID')
            return
        
        self.hangarSpace.onHeroTankReady += self.start
    
    def start(self, *args):
        self.hangarSpace.onHeroTankReady -= self.start
        
        if not AUMain.g_AUShared.check(): return
        
        if AUGUI is not None:
            g_WindowCommon = AUGUI.g_WindowCommon
            
            AUMain.g_AUShared.windowCommon = g_WindowCommon
            
            window = g_WindowCommon.createWindow()
            if window is not None:
                window.onWindowPopulate += self.getModsList
                return
        
        self.getModsList()
    
    def getModsList(self):
        if not AUMain.g_AUShared.check(): return
        
        respType = AUMain.ResponseType.index('GET_MODS_LIST')
        
        req_header = AUMain.RequestHeader(self.ID, self.lic, respType)
        req        = AUMain.Request(req_header)
        req.parse('B', self.langID)
        req.parse('B', int(AUMain.g_AUShared.config['enable_GUI']))
        
        AUMain.g_AUEvents.onModsProcessingStart()
        
        resp = AUMain.ModsListResponse(req.get_data(), req.get_type())
        if resp.failed:
            AUMain.g_AUShared.fail(resp.failed, resp.code)
            return
        
        self.exp = resp.time_exp
        
        AUMain.g_AUEvents.onModsProcessingDone(self.exp)
        AUMain.g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        self.getDepsList(resp.mods)
    
    def getDepsList(self, mods):
        if not AUMain.g_AUShared.check(): return
        
        respType = AUMain.ResponseType.index('GET_DEPS')
        
        dependencies = {
            'enabled'  : set(),
            'disabled' : set()
        }
        
        toUpdate = set()
        toDelete = {
            'file' : set(),
            'dir'  : set()
        }
        
        for modID in mods:
            mod = AUMain.g_AUShared.mods[modID] = AUMain.Mod(mods[modID])
            if mod.failed:
                AUMain.g_AUShared.fail(mod.failed, mod.code)
                return
            mod.parseTree('./', mod.tree)
            
            dependencies['enabled' if mod.enabled else 'disabled'].update(mod.dependencies)
            
            toUpdate.update(mod.needToUpdate['file'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['dir'])
        
        dependencies['disabled'] -= dependencies['enabled']
        
        req_header = AUMain.RequestHeader(self.ID, self.lic, respType)
        req        = AUMain.Request(req_header)
        req.parse('B', self.langID)
        req.parse('H', len(dependencies['enabled'] | dependencies['disabled']))
        for key in dependencies:
            for dependencyID in dependencies[key]:
                req.parse('H', dependencyID)
                req.parse('B', 1 if key == 'enabled' else 0)
        
        AUMain.g_AUEvents.onDepsProcessingStart()
        
        resp = AUMain.DepsResponse(req.get_data(), req.get_type())
        if resp.failed:
            AUMain.g_AUShared.fail(resp.failed)
            return
        
        AUMain.g_AUEvents.onDepsProcessingDone()
        AUMain.g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = AUMain.g_AUShared.dependencies[dependencyID] = AUMain.Mod(deps[dependencyID])
            if dependency.failed:
                AUMain.g_AUShared.fail(dependency.failed)
                return
            dependency.parseTree('./', dependency.tree)
            
            toUpdate.update(dependency.needToUpdate['file'])
            toDelete['file'].update(dependency.needToDelete['file'])
            toDelete['dir'].update(dependency.needToDelete['dir'])
        
        toDelete['file'] -= DeleteExclude['file'] | toUpdate
        toDelete['dir']  -= DeleteExclude['dir']
        
        toDelete['dir'] = sorted(
            toDelete['dir'],
            key = getLevels,
            reverse = True
        )
        
        deleted = self.delFiles(toDelete)
        
        updated_deps = self.getFiles(AUMain.g_AUShared.dependencies, True)
        updated_mods = self.getFiles(AUMain.g_AUShared.mods,         False)
        
        updated = updated_mods + updated_deps
        
        key = None
        
        if self.deleteAfterFini:
            key = 'delete'
            with open(AUMain.Paths.DELETED_PATH, 'wb') as fil:
                for path in AUMain.g_AUShared.undeletedPaths:
                    fil.write(path + '\n')
            self.hookFini()
        elif self.unpackAfterFini:
            key = 'create'
            self.hookFini()
        elif updated:
            key = 'update'
        
        AUMain.g_AUShared.createDialogs(key, updated)
    
    def delFiles(self, paths):
        if not AUMain.g_AUShared.check(): return 0
        
        paths_count = len(paths['file']) + len(paths['dir'])
        
        undeletedPaths = []
        
        AUMain.g_AUEvents.onDeletingStart(paths_count)
        
        deleted = 0
        for path in paths['file']:
            if exists(path):
                try:
                    remove(path)
                    deleted += 1
                except Exception:
                    AUMain.g_AUShared.undeletedPaths.append(path)
                    AUMain.g_AUShared.logger.log('Unable to delete file %s'%(path))
            #else:
            #    g_AUShared.logger.log('File %s is not exists'%(path))
        
        for path in paths['dir']:
            if exists(path) and not listdir(path):
                try:
                    rmdir(path)
                    deleted += 1
                except Exception:
                    AUMain.g_AUShared.undeletedPaths.append(path)
                    AUMain.g_AUShared.logger.log('Unable to delete directory %s'%(path))
                    AUMain.g_AUShared.fail('DELETING_FILE')
                    break
            #else:
            #    g_AUShared.logger.log('Directory %s is not empty'%(path))
        
        self.deleteAfterFini = bool(AUMain.g_AUShared.undeletedPaths)
        
        AUMain.g_AUEvents.onDeletingDone(deleted, paths_count)
        
        return deleted
    
    def getFiles(self, mods, isDependency):
        if not AUMain.g_AUShared.check(): return 0
        
        mods_count = len(filter(lambda mod: mod.needToUpdate['ID'], mods.values()))
        
        AUMain.g_AUEvents.onFilesProcessingStart(mods_count)
        
        updated = 0
        for modID in mods:
            mod = mods[modID]
            if not mod.needToUpdate['ID']:
                continue
            
            req_header = AUMain.RequestHeader(self.ID, self.lic, AUMain.ResponseType.index('GET_FILES'))
            req = AUMain.Request(req_header)
            req.parse('H', int(modID))
            req.parse('I', len(mod.needToUpdate['ID']))
            for updID in mod.needToUpdate['ID']:
                req.parse('I', int(updID))
            AUMain.g_AUEvents.onModFilesProcessingStart(updated, mod.name, isDependency)
            
            resp = AUMain.FilesResponse(req.get_data(), req.get_type())
            
            AUMain.g_AUEvents.onModFilesProcessingDone(mod, updated, mods_count, resp.failed, resp.code)
            
            if resp.failed == AUMain.ErrorCode.index('SUCCESS'):
                updated += 1
            elif resp.failed == AUMain.ErrorCode.index('CREATING_FILE'):
                self.unpackAfterFini = True
            else:
                AUMain.g_AUShared.fail(resp.failed, resp.code)
                break
        
        AUMain.g_AUEvents.onFilesProcessingDone(updated, mods_count)
        
        return updated
    
    def hookFini(self):
        if self.finiHooked: return
        
        print 'hooking fini...'
        
        try:
            import game
            _game__fini = game.fini
            game.fini = lambda *args: self.onGameFini(_game__fini, *args)
            self.finiHooked = True
        except:
            AUMain.g_AUShared.logger.log('Unable to hook fini')
    
    def onGameFini(self, func, *args):
        print 'starting helper process...'
        
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(AUMain.Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
        
        func(*args)
    
try:
    import xfw_loader.python as loader
except:
    print '[CRITICAL ERROR] Autoupdater: Unable to get XFW Loader'
    sys.exit()

AUMain = loader.get_mod_module('com.pavel3333.Autoupdater')
AUGUI  = loader.get_mod_module('com.pavel3333.Autoupdater.GUI')

if AUMain is None:
    print '[CRITICAL ERROR] Autoupdater: Unable to load mod files. Autoupdater will not loaded!'
    sys.exit()

if AUGUI is None:
    print '[INFO] Autoupdater: Cannot find GUI module'

if not BattleReplay.isPlaying():
    g_Autoupdater = Autoupdater()
