__all__ = ('MOD_ID', 'MOD_NAME', 'native_module', 'py_external')

import BattleReplay

import xfw_loader.python as loader

MOD_ID   = 'com.pavel3333.Autoupdater.GUI'
MOD_NAME = 'Autoupdater_GUI'

def error(msg):
    global MOD_NAME
    raise StandardError, '[%s][ERROR]: %s'%(MOD_NAME, msg)

if BattleReplay.isPlaying():
    error('Autoupdater GUI doesn\t work on replays')

xfwnative = loader.get_mod_module('com.modxvm.xfw.native')
if xfwnative is None:
    error('Unable to get XFW Native module')

if not xfwnative.unpack_native(MOD_ID):
    error('Unable to unpack native. Please contact us')

import py_external

native_module = xfwnative.load_native(MOD_ID, MOD_NAME + '.pyd', MOD_NAME)
if not native_module:
    error('Unable to load native module')