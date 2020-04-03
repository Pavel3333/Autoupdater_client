from .common   import *
from .packet   import *
from .request  import *
from .response import *
from .shared   import *

import BigWorld
import BattleReplay

from PlayerEvents import g_playerEvents

from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

import traceback
import json

from os      import listdir, makedirs, remove, rmdir
from os.path import exists, isfile

class Autoupdater:
    MOD_ID = 'com.pavel3333.Autoupdater'
    
    hangarSpace = dependency.descriptor(IHangarSpace)
    
    def __init__(self):
        for directory in Directory.values():
            if not exists(directory):
                makedirs(directory)

        self.exp = 0 # AHHH SHIT MOVE IT TO CYTHON PLS
        self.ID  = 0
        self.lic = ''
        
        self.langID = getLangID()
        
        self.unpackAfterFini = False
        self.deleteAfterFini = False
        self.finiHooked      = False
        
        import xfw_loader.python as loader
       
        xfwnative = loader.get_mod_module('com.modxvm.xfw.native')
        if xfwnative is None:
            g_AUShared.fail('LOAD_XFW_NATIVE')
            return
        
        if not xfwnative.unpack_native(self.MOD_ID):
            g_AUShared.fail('UNPACK_NATIVE')
            return
        
        self.module = xfwnative.load_native(self.MOD_ID, 'AUGetter.pyd', 'AUGetter')
        if not self.module:
            g_AUShared.fail('LOAD_NATIVE')
            return
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, ctx, *args):
        self.ID = ctx.get('databaseID', 0)
        
        if not self.ID:
            g_AUShared.fail('CHECKING_ID')
            return
            
        lic_path = Paths.LIC_PATH%(self.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AUShared.fail('FILES_NOT_FOUND')
            return
            
        with open(lic_path, 'rb') as lic_file:
            self.lic = lic_file.read()

        if len(self.lic) != Constants.LIC_LEN:
            g_AUShared.fail('LIC_INVALID')
            return
        
        self.hangarSpace.onHeroTankReady += self.start
    
    def start(self, *args):
        self.hangarSpace.onHeroTankReady -= self.start
        
        if not g_AUShared.check(): return
        
        if g_AUShared.windowCommon is not None:
            if g_AUShared.windowCommon.createWindow(self.getModsList) is not None:
                return
        
        self.getModsList()
    
    def getModsList(self):
        if not g_AUShared.check(): return
        
        respType = ResponseType.index('GET_MODS_LIST')
        
        req_header = RequestHeader(self.ID, self.lic, respType)
        req        = Request(req_header)
        req.parse('B', self.langID)
        req.parse('B', int(g_AUShared.config['enable_GUI']))
        
        g_AUEvents.onModsProcessingStart()
        
        resp = ModsListResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AUShared.fail(resp.failed, resp.code)
            return
        
        self.exp = resp.time_exp
        
        g_AUEvents.onModsProcessingDone(self.exp)
        g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        self.getDepsList(resp.mods)
    
    def getDepsList(self, mods):
        if not g_AUShared.check(): return
        
        respType = ResponseType.index('GET_DEPS')
        
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
            mod = g_AUShared.mods[modID] = Mod(mods[modID])
            if mod.failed:
                g_AUShared.fail(mod.failed, mod.code)
                return
            mod.parseTree('./', mod.tree)
            
            dependencies['enabled' if mod.enabled else 'disabled'].update(mod.dependencies)
            
            toUpdate.update(mod.needToUpdate['file'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['dir'])
        
        dependencies['disabled'] -= dependencies['enabled']
        
        req_header = RequestHeader(self.ID, self.lic, respType)
        req        = Request(req_header)
        req.parse('B', self.langID)
        req.parse('H', len(dependencies['enabled'] | dependencies['disabled']))
        for key in dependencies:
            for dependencyID in dependencies[key]:
                req.parse('H', dependencyID)
                req.parse('B', 1 if key == 'enabled' else 0)
        
        g_AUEvents.onDepsProcessingStart()
        
        resp = DepsResponse(req.get_data(), req.get_type())
        if resp.failed:
            g_AUShared.fail(resp.failed)
            return
        
        g_AUEvents.onDepsProcessingDone()
        g_AUShared.handleErr(respType, resp.failed, resp.code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = g_AUShared.dependencies[dependencyID] = Mod(deps[dependencyID])
            if dependency.failed:
                g_AUShared.fail(dependency.failed)
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
        
        self.delFiles(toDelete)
        
        updated_deps = self.getFiles(True)
        updated_mods = self.getFiles(False)
        
        updated = updated_mods + updated_deps
        
        key = None
        
        if self.deleteAfterFini:
            key = 'delete'
            self.hookFini()
        elif self.unpackAfterFini:
            key = 'create'
            self.hookFini()
        elif updated:
            key = 'update'
        
        g_AUShared.createDialogs(key, updated)
    
    def delFiles(self, paths):
        if not g_AUShared.check(): return 0
        
        paths_count = len(paths['file']) + len(paths['dir'])
        
        undeletedPaths = []
        
        g_AUEvents.onDeletingStart(paths_count)
        
        deleted = 0
        for path in paths['file']:
            if exists(path):
                try:
                    remove(path)
                    deleted += 1
                except Exception:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete file %s'%(path))
            #else:
            #    g_AUShared.logger.log('File %s is not exists'%(path))
        
        for path in paths['dir']:
            if exists(path) and not listdir(path):
                try:
                    rmdir(path)
                    deleted += 1
                except Exception:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s'%(path))
                    g_AUShared.fail('DELETING_FILE')
                    break
            #else:
            #    g_AUShared.logger.log('Directory %s is not empty'%(path))
        
        if g_AUShared.undeletedPaths:
            with open(Paths.DELETED_PATH, 'wb') as fil:
                for path in g_AUShared.undeletedPaths:
                    fil.write(path + '\n')
        
        self.deleteAfterFini = bool(g_AUShared.undeletedPaths)
        
        g_AUEvents.onDeletingDone(deleted, paths_count)
    
    def getFiles(self, isDependency):
        if not g_AUShared.check(): return 0
        
        mods = g_AUShared.mods if not isDependency else g_AUShared.dependencies
        
        self.module.get_files(
            self.ID,
            mods,
            g_AUEvents.onFilesProcessingStart,
            g_AUEvents.onModFilesProcessingStart,
            g_AUEvents.onModFilesProcessingDone,
            g_AUEvents.onFilesProcessingDone,
        )
        
        mods_count = len(filter(lambda mod: mod.needToUpdate['ID'], mods.values()))
        
        g_AUEvents.onFilesProcessingStart(mods_count)
        
        updated = 0
        for modID in mods:
            mod = mods[modID]
            if not mod.needToUpdate['ID']:
                continue
            
            req_header = RequestHeader(self.ID, self.lic, ResponseType.index('GET_FILES'))
            req = Request(req_header)
            req.parse('H', int(modID))
            req.parse('I', len(mod.needToUpdate['ID']))
            for updID in mod.needToUpdate['ID']:
                req.parse('I', int(updID))
            g_AUEvents.onModFilesProcessingStart(mod.name, isDependency)
            
            resp = FilesResponse(req.get_data(), req.get_type())
            
            g_AUEvents.onModFilesProcessingDone(mod, resp.failed, resp.code)
        
        g_AUEvents.onFilesProcessingDone()
        
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
            g_AUShared.logger.log('Unable to hook fini')
    
    def onGameFini(self, func, *args):
        print 'starting helper process...'
        
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
        
        func(*args)

if not BattleReplay.isPlaying():
    g_Autoupdater = Autoupdater()
