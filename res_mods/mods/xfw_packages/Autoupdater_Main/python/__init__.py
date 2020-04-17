from .enum     import *
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
        
        self.unpackAfterFini = False
        self.deleteAfterFini = False
        self.finiHooked      = False
        
        import xfw_loader.python as loader
       
        xfwnative = loader.get_mod_module('com.modxvm.xfw.native')
        if xfwnative is None:
            g_AUShared.fail(ErrorCode.LoadXFWNative)
            return
        
        if not xfwnative.unpack_native(self.MOD_ID):
            g_AUShared.fail(ErrorCode.UnpackNative)
            return
        
        self.module = xfwnative.load_native(self.MOD_ID, 'AUGetter.pyd', 'AUGetter')
        if not self.module:
            g_AUShared.fail(ErrorCode.LoadNative)
            return
        
        g_playerEvents.onAccountShowGUI += self.getID
    
    def getID(self, ctx, *args):
        g_AUShared.ID = ctx.get('databaseID', 0)
        
        if not g_AUShared.ID:
            g_AUShared.fail(ErrorCode.CheckID)
            return
            
        lic_path = Paths.LIC_PATH%(g_AUShared.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AUShared.fail(ErrorCode.FilesNotFound)
            return
        
        try:
            with open(lic_path, 'rb') as lic_file:
                g_AUShared.lic_key = lic_file.read()
        except IOError as exc:
            g_AUShared.fail(ErrorCode.FilesNotFound, exc.errno)
            return
        except:
            g_AUShared.fail(ErrorCode.FilesNotFound)
            return
        
        if len(g_AUShared.lic_key) != Constants.LIC_LEN:
            g_AUShared.fail(ErrorCode.LicInvalid)
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
        
        g_AUShared.respType = ResponseType.GetModsList
        
        g_AUEvents.onModsProcessingStart()
        
        req = Request()
        req.parse('B', AUTH_REALM)
        req.parse('B', int(g_AUShared.config['enable_GUI']))
        
        resp = getResponse(ModsListResponse, req)
        
        g_AUEvents.onModsProcessingDone()
        
        if resp.fail_err != ErrorCode.Success:
            g_AUShared.fail(resp.fail_err, resp.fail_code)
            return
        
        g_AUShared.handleErr(resp.fail_err, resp.fail_code)
        
        self.getDepsList(resp.mods)
    
    def getDepsList(self, mods):
        if not g_AUShared.check(): return
        
        g_AUShared.respType = ResponseType.GetDeps
        
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
            if mod.fail_err != ErrorCode.Success:
                g_AUShared.fail(mod.fail_err, mod.fail_code)
                return
            mod.parseTree('./', mod.tree)
            
            dependencies['enabled' if mod.enabled else 'disabled'].update(mod.dependencies)
            
            toUpdate['file'].update(mod.needToUpdate['file'])
            toUpdate['dir'].update(mod.needToUpdate['dir'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['dir'])
        
        dependencies['disabled'] -= dependencies['enabled']
        
        req = Request()
        req.parse('B', AUTH_REALM)
        req.parse('H', len(dependencies['enabled'] | dependencies['disabled']))
        for key in dependencies:
            for dependencyID in dependencies[key]:
                req.parse('H', dependencyID)
                req.parse('B', 1 if key == 'enabled' else 0)
        
        resp = getResponse(DepsResponse, req)
        
        g_AUEvents.onDepsProcessingDone()
        
        if resp.fail_err != ErrorCode.Success:
            g_AUShared.fail(resp.fail_err, resp.fail_code)
            return
        
        g_AUShared.handleErr(resp.fail_err, resp.fail_code)
        
        deps = resp.dependencies
        for dependencyID in deps:
            dependency = g_AUShared.dependencies[dependencyID] = Mod(deps[dependencyID])
            if dependency.fail_err != ErrorCode.Success:
                g_AUShared.fail(dependency.fail_err, dependency.fail_code)
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
        
        g_AUShared.respType = ResponseType.DelFiles
        
        paths_count = len(paths['file']) + len(paths['dir'])
        
        undeletedPaths = []
        
        g_AUEvents.onDeletingStart(paths_count)
        
        deleted = 0
        for path in paths['file']:
            if exists(path):
                try:
                    remove(path)
                    deleted += 1
                    g_AUEvents.onDataProcessed(g_AUShared.respType, deleted, paths_count, '')
                except OSError as exc:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete file %s (errno %s)'%(path, exc.errno))
                except:
                    import traceback
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete file %s:\n%s'%(path, traceback.format_exc()))
            #else:
            #    g_AUShared.logger.log('File %s is not exists'%(path))
        
        for path in paths['dir']:
            if exists(path) and not listdir(path):
                try:
                    rmdir(path)
                    deleted += 1
                    g_AUEvents.onDataProcessed(g_AUShared.respType, deleted, paths_count, '')
                except OSError as exc:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s (errno %s)'%(path, exc.errno))
                    g_AUShared.fail(ErrorCode.DeleteFile, exc.errno)
                    break
                except:
                    import traceback
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s:\n%s'%(path, traceback.format_exc()))
                    g_AUShared.fail(ErrorCode.DeleteFile, exc.errno)
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
        
        g_AUShared.respType = ResponseType.GetFiles
        
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
        
        g_AUShared.logger.log('hooking fini...')
        
        try:
            import game
            _game__fini = game.fini
            game.fini = lambda *args: self.onGameFini(_game__fini, *args)
            self.finiHooked = True
        except:
            import traceback
            g_AUShared.logger.log('Unable to hook fini:\n%s'%(traceback.format_exc()))
    
    def onGameFini(self, func, *args):
        g_AUShared.logger.log('starting helper process...')
        
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
        
        func(*args)

if not BattleReplay.isPlaying():
    g_Autoupdater = Autoupdater()
