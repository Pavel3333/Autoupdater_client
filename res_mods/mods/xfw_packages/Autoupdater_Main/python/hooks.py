from .shared import *

__all__ = ('hookFini', )

def onGameFini(func, *args):
    g_AUShared.logger.log('starting helper process...')
    
    import subprocess
    DETACHED_PROCESS = 0x00000008
    subprocess.Popen(Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
    
    func(*args)

def hookFini():
    if g_AUShared.finiHooked: return
    
    g_AUShared.logger.log('hooking fini...')
    
    try:
        import game
        _game__fini = game.fini
        game.fini = lambda *args: onGameFini(_game__fini, *args)
        g_AUShared.finiHooked = True
    except:
        import traceback
        g_AUShared.logger.log('Unable to hook fini:\n%s'%(traceback.format_exc()))