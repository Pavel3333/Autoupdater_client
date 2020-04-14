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
            print 'fail: LOAD_NATIVE'
            g_AUShared.fail('LOAD_NATIVE')
            return
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, ctx, *args):
        g_AUShared.ID = ctx.get('databaseID', 0)
        
        if not g_AUShared.ID:
            g_AUShared.fail('CHECKING_ID')
            return
            
        lic_path = Paths.LIC_PATH%(g_AUShared.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AUShared.fail('FILES_NOT_FOUND')
            return
            
        with open(lic_path, 'rb') as lic_file:
            self.lic = lic_file.read()
        
        if len(g_AUShared.lic_key) != Constants.LIC_LEN:
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
        
        g_AUEvents.onModsProcessingStart()
        
        req = Request()
        req.parse('B', self.langID)
        req.parse('B', int(g_AUShared.config['enable_GUI']))
        
        resp = getResponse(ModsListResponse, 'GET_MODS_LIST', req)
        if resp.failed:
            g_AUShared.fail(resp.failed, resp.code)
            return
        
        g_AUEvents.onModsProcessingDone()
        g_AUShared.handleErr(resp.failed, resp.code)
        
        self.getDepsList(resp.mods)
    
    def getDepsList(self, mods):
        if not g_AUShared.check(): return
        
        dependencies = {
            'enabled'  : set(),
            'disabled' : set()
        }
        
        toUpdate = {
            'file' : set(),
            'dir'  : set()
        }
        toDelete = {
            'file' : set(),
            'dir'  : set()
        }
        
        g_AUEvents.onDepsProcessingStart()
        
        for modID in mods:
            mod = g_AUShared.mods[modID] = Mod(mods[modID])
            if mod.failed:
                g_AUShared.fail(mod.failed, mod.code)
                return
            mod.parseTree('./', mod.tree)
            
            dependencies['enabled' if mod.enabled else 'disabled'].update(mod.dependencies)
            
            toUpdate['file'].update(mod.needToUpdate['file'])
            toUpdate['dir'].update(mod.needToUpdate['dir'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['dir'])
        
        dependencies['disabled'] -= dependencies['enabled']
        
        req = Request(req_header)
        req.parse('B', self.langID)
        req.parse('H', len(dependencies['enabled'] | dependencies['disabled']))
        for key in dependencies:
            for dependencyID in dependencies[key]:
                req.parse('H', dependencyID)
                req.parse('B', 1 if key == 'enabled' else 0)
        
        resp = getResponse(DepsResponse, 'GET_DEPS', req)
        if resp.failed:
            g_AUShared.fail(resp.failed)
            return
        
        g_AUEvents.onDepsProcessingDone()
        g_AUShared.handleErr(resp.failed, resp.code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = g_AUShared.dependencies[dependencyID] = Mod(deps[dependencyID])
            if dependency.failed:
                g_AUShared.fail(dependency.failed)
                return
            dependency.parseTree('./', dependency.tree)
            
            toUpdate['file'].update(dependency.needToUpdate['file'])
            toUpdate['dir'].update(dependency.needToUpdate['dir'])
            toDelete['file'].update(dependency.needToDelete['file'])
            toDelete['dir'].update(dependency.needToDelete['dir'])
        
        toDelete['file'] -= DeleteExclude['file'] | toUpdate['file']
        toDelete['dir']  -= DeleteExclude['dir']  | toUpdate['dir']
        
        toDelete['dir'] = sorted(
            toDelete['dir'],
            key = getLevels,
            reverse = True
        )
        
        print 'toDelete:', toDelete
        
        self.delFiles(toDelete)
        self.getFiles()
        
    def onModsUpdated(self, updated):
        if self.deleteAfterFini:
            key = 'delete'
            self.hookFini()
        elif self.unpackAfterFini:
            key = 'create'
            self.hookFini()
        elif updated:
            key = 'update'
        else:
            return
        
        g_AUShared.createDialogs(key)
    
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
                    g_AUShared.fail('DELETE_FILE')
                    break
            #else:
            #    g_AUShared.logger.log('Directory %s is not empty'%(path))
        
        if g_AUShared.undeletedPaths:
            with open(Paths.DELETED_PATH, 'wb') as fil:
                for path in g_AUShared.undeletedPaths:
                    fil.write(path + '\n')
        
        self.deleteAfterFini = bool(g_AUShared.undeletedPaths)
        
        g_AUEvents.onDeletingDone(deleted, paths_count)
    
    def getFiles(self):
        if not g_AUShared.check(): return
        
        mods = g_AUShared.mods.copy()
        mods.update(g_AUShared.dependencies)
        
        mods_count = len(
            filter(
                lambda mod: mod.needToUpdate['ID'],
                mods.values()
            )
        )
        self.module.get_files(mods_count)
    
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
