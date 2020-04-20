import xfw_loader.python as loader

MOD_ID   = 'com.pavel3333.Autoupdater'
MOD_NAME = 'Autoupdater_Main'

def error(msg):
    global MOD_NAME
    raise StandardError, '[%s][ERROR]: %s'%(MOD_NAME, msg)

xfwnative = loader.get_mod_module('com.modxvm.xfw.native')
if xfwnative is None:
    error('Unable to get XFW Native module')

if not xfwnative.unpack_native(MOD_ID):
    error('Unable to unpack native. Please contact us')

native_module = xfwnative.load_native(MOD_ID, MOD_NAME + '.pyd', MOD_NAME)
if not native_module:
    error('Unable to load native module')

def onGameFini(func, *args):
    native_module.g_AUShared.logger.log('starting helper process...')
    
    import subprocess
    DETACHED_PROCESS = 0x00000008
    subprocess.Popen(native_module.Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
    
    func(*args)

def hookFini():
    if native_module.g_AUShared.finiHooked: return
    
    native_module.g_AUShared.logger.log('hooking fini...')
    
    try:
        import game
        _game__fini = game.fini
        game.fini = lambda *args: onGameFini(_game__fini, *args)
        native_module.g_AUShared.finiHooked = True
    except:
        import traceback
        native_module.g_AUShared.logger.log('Unable to hook fini:\n%s'%(traceback.format_exc()))
