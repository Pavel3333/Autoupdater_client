__all__ = ('Enum', 'SimpleDialog', 'AUTH_REALM', 'DEBUG', 'parseToJSON', 'Error', 'getJSON', 'checkSeqs', 'Constants', 'Directory', 'Paths', 'getLevels', 'DeleteExclude', 'Mod', 'Packet', 'StreamPacket', 'Logger', 'g_AUShared', 'RequestHeader', 'Request', 'getRequest', 'Response', 'ModsListResponse', 'FilesResponse', 'getResponse', 'GUIPaths', 'g_AUGUIShared')


class EnumValue:
    def __init__(self, classname, enumname, value):
        self.__classname = classname
        self.__enumname = enumname
        self.__value = value

    def __int__(self):
        return self.__value

    #def __repr__(self):
    #    return "EnumValue(%r, %r, %r)" % (self.__classname,
    #                                      self.__enumname,
    #                                      self.__value)

    def __str__(self):
        return self.__enumname #"%s.%s" % (self.__classname, self.__enumname)

    def __cmp__(self, other):
        if isinstance(other, str):
            return cmp(self.__enumname, other)
        return cmp(self.__value, int(other))

class EnumMetaClass:
    def __init__(self, name, bases, dict):
        for base in bases:
            if base.__class__ is not EnumMetaClass:
                raise TypeError, "Enumeration base class must be enumeration"
        bases = filter(lambda x: x is not Enum, bases)
        self.__name__ = name
        self.__bases__ = bases
        self.__dict = {}
        for key, value in dict.items():
            if not isinstance(key, str) or not isinstance(value, int): continue
            self.__dict[key] = EnumValue(name, key, value)

    def __hasattr__(self, name):
        if name == '__members__':
            return True
        
        if isinstance(name, str):
            if name in self.__dict:
                return True
        elif int(name) in self.__dict.values():
            return True
        
        return any(base.__hasattr__(name) for base in self.__bases__)
    
    def __getattr__(self, name):
        if name == '__members__':
            return self.__dict.keys()

        if isinstance(name, str) and name in self.__dict:
            return self.__dict[name]
        else:
            for key, value in self.__dict.iteritems():
                if value == name:
                    return value
        
        for base in self.__bases__:
            if base.__hasattr__(name):
                return base.__getattr__(name)

    #def __repr__(self):
    #    s = self.__name__
    #    if self.__bases__:
    #        s = s + '(' + ', '.join(map(lambda x: x.__name__,
    #                                      self.__bases__)) + ')'
    #    if self.__dict:
    #        s = "%s: {%s}" % (s, ', '.join("%s: %s" % (key, int(value)) for key, value in self.__dict.iteritems()))
    #    return s

Enum = EnumMetaClass("Enum", (), {})

class LangID(Enum):
    RU = 0
    EU = 1
    CN = 2

class ErrorCode(Enum):
    Success          = 0
    Translations     = 1
    CheckID          = 2
    LicNotFound      = 3
    LicInvalid       = 4
    Connect          = 5
    RespTooSmall     = 6
    RespInvalid      = 7
    GetMods          = 8
    ReadMods         = 9
    GetDeps          = 10
    ReadDeps         = 11
    GetFiles         = 12
    InvalidPathLen   = 13
    InvalidFileSize  = 14
    CreateFile       = 15
    CreateManualFile = 16
    GetModFields     = 17
    DecodeModFields  = 18
    DeleteFile       = 19

class WarningCode(Enum):
    #HTTPS          = 1
    #ReqNotFound    = 2
    #ParseHdr       = 3
    #ReqInvalidLen  = 4
    #ParseWGID      = 5
    #ReadLic        = 6
    CheckID         = 7
    GetUserData     = 8
    Expired         = 11
    #ReadCode       = 12
    #IncorrectCode  = 13
    #ReadLang       = 14
    #ReadGUIFlag    = 15
    #ParseDepsCount = 16
    #Parse_GF_Hdr   = 17
    GetModDesc      = 18
    
    #Unknown        = 255

class ResponseType(Enum):
    GetModsList = 0
    GetDeps     = 1
    DelFiles    = 2
    GetFiles    = 3

class DataUnits(Enum):
    B  = 0
    KB = 1
    MB = 2
    GB = 3

class Event(object):
    def __init__(self):
        self.queue = []

    def __call__(self, *args):
        for func in self.queue:
            func(*args)
    
    def __iadd__(self, func):
        self.queue.append(func)
        return self

def hookMethod(cls, method, new_method):
    old_method = getattr(cls, method)
    setattr(cls, method, lambda *args: new_method(old_method, *args))
# Author: Ekspoint

import BigWorld
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta


class DialogButtons(object):
    def __init__(self, close=None, submit=None):
        self.close = close
        self.submit = submit
        
    def _close(self, label, focused=True):
        return {'id': DIALOG_BUTTON_ID.CLOSE,
          'label': label, 'focused': focused}
       
    def _submit(self, label, focused=True):
        return {'id': DIALOG_BUTTON_ID.SUBMIT,
          'label': label, 'focused': focused}
  
    def getLabels(self):
        if self.close is not None and self.submit is None:
            return [self._close(self.close, True)]
        if self.submit is not None and self.close is not None:
            return [self._submit(self.submit, True), 
            self._close(self.close, False)]

class SimpleDialog(object):
    def openUrlUp(self, url):
        if url is not None:
            return BigWorld.wg_openWebBrowser(url)
    
    def _close(self, title=None, message=None, close=None):
        return showDialog(SimpleDialogMeta(title=title, message=message, buttons=DialogButtons(close=close)), None)
    
    def _submit(self, title=None, message=None, submit=None, close=None, url=None, func_proceed=None, handler=None):
        def _handler(proceed):
            if proceed:
                if url is not None and func_proceed is None:
                    self.openUrlUp(url)
                elif func_proceed is not None:
                    func_proceed()
            if handler is not None:
                handler()
        
        return showDialog(SimpleDialogMeta(title=title, message=message, buttons=DialogButtons(submit=submit, close=close)), _handler)

import json
import platform

from os.path import exists
from hashlib import md5

AUTH_REALM = LangID.EU

try:
    from constants import AUTH_REALM as game_realm
    if LangID.__hasattr__(game_realm):
        AUTH_REALM = LangID.__getattr__(game_realm)
except ImportError:
    pass

DEBUG = True

def parseToJSON(obj):
    if isinstance(obj, dict):
        for key, value in obj.iteritems():
            obj[key] = parseToJSON(value)
    if  isinstance(obj, set) or \
        isinstance(obj, frozenset) or \
        isinstance(obj, tuple):
        obj = list(obj)
    return obj

class Error(object):
    __slots__ = { 'fail_err', 'fail_code' }
    
    def __init__(self, *args):
        self.fail_err  = ErrorCode.Success
        self.fail_code = 0
    
    def check(self):
        return self.fail_err == ErrorCode.Success
    
    def fail(self, err, extraCode=0):
        if isinstance(err, int) or isinstance(err, str):
            err = ErrorCode.__getattr__(err)
        
        self.fail_err  = err
        self.fail_code = extraCode
    
    def slots(self):
        return self.__slots__
    
    def dict(self):
        return dict((slot, parseToJSON(getattr(self, slot, None))) for slot in self.slots())


def getJSON(path, pattern):
    try:
        raw = {}
        
        if exists(path):
            with open(path, 'r') as fil:
                raw = json.load(fil)
        else:
            with open(path, 'w') as fil:
                json.dump(pattern, fil, sort_keys=True, indent=4)
            raw = pattern
        
        if all(checkSeqs(pattern[key], raw.get(key, {})) for key in pattern):
            return raw
        else:
            with open(path, 'w') as fil:
                json.dump(pattern, fil, sort_keys=True, indent=4)
            return pattern
    except IOError as exc:
        return exc.errno
    except:
        return None

def checkSeqs(seq1, seq2): # Check if dic1 contains keys of dic2
    if not isinstance(seq1, type(seq2)):
        string_types = (str, unicode)
        if type(seq1) not in string_types or type(seq2) not in string_types:
            return False
    if isinstance(seq1, dict):
        return all(key in seq2 and checkSeqs(seq1[key], seq2[key]) for key in seq1)
    elif isinstance(seq1, list):
        return len(seq1) == len(seq2) and all(checkSeqs(seq1[i], seq2[i]) for i in xrange(len(seq1)))
    return True


class Constants:
    MOD_NAME = 'Autoupdater'
    MOD_ID   = 'com.pavel3333.' + MOD_NAME

    AUTOUPDATER_URL = 'https://api.pavel3333.ru/loader.php'

    LIC_LEN        = 32
    CHUNK_MAX_SIZE = 65536

Directory = {
    'MOD_DIR'    : Constants.MOD_NAME + '/'
}
Directory.update({
    'FAIL_DIR'   : Directory['MOD_DIR'] + 'manual/',
    'DUMP_DIR'   : Directory['MOD_DIR'] + 'dumps/',
    'BIN_DIR'    : 'win%s/'%(platform.architecture()[0][:2])
})

class Paths:
    LIC_PATH        = Directory['MOD_DIR'] + Constants.MOD_NAME.upper() + '_%s.lic'
    EXE_HELPER_PATH = Directory['BIN_DIR'] + Constants.MOD_ID + '.Helper.exe'
    DELETED_PATH    = Directory['MOD_DIR'] + 'delete.txt'
    LOG_PATH        = Directory['MOD_DIR'] + 'AULoader_log.txt'

def getLevels(path):
    return len(filter(lambda level: bool(level), path.split('/')))

DeleteExclude = {
    'dir' : {
        'game_metadata',
        'mods',
        'replays',
        'res',
        'res_mods',
        'screenshots',
        'updates',
        'win32',
        'win64'
    },
    'file': {
        'app_type.xml',
        'game_info.xml',
        'Licenses.txt',
        'paths.xml',
        'version.xml',
        'wgc_api.exe',
        'WorldOfTanks.exe',
        'WorldOfTanks.ico'
    }
}

class Mod(Error):
    __slots__ = { 'needToUpdate', 'needToDelete', 'id', 'name', 'description', 'version', 'build', 'tree', 'paths_delete', 'names', 'hashes', 'dependencies' }
    
    def __init__(self, mod):
        super(Mod, self).__init__()
    
        self.needToUpdate = { # Updating only files
            'ID'   : set(),
            'file' : set(),
            'dir'  : set()
        }
        self.needToDelete = { # Deleting files and directories
            'file' : set(),
            'dir'  : set()
        }
        
        try:
            self.id          = mod['id']
            self.name        = mod['name']
            self.description = mod['description']
            self.version     = mod['version']
            self.build       = mod['build']
        except KeyError:
            self.fail(ErrorCode.GetModFields)
            return
        
        try:
            self.tree         = json.loads(mod['tree'])
            self.paths_delete = json.loads(mod['paths_delete'])
            self.names        = json.loads(mod['names'])
            self.hashes       = json.loads(mod['hashes'])
        except:
            self.fail(ErrorCode.DecodeModFields)
            return
        
        for path in self.paths_delete:
            if exists(path):
                self.needToDelete['file'].add(path)
    
    def parseTree(self, path, curr_dic):
        for ID in curr_dic:
            ID_i = int(ID)
            
            subpath = path + self.names[ID]
            if curr_dic[ID] == 0:
                self.needToUpdate['file'].add(subpath)
                if not exists(subpath):
                    self.needToUpdate['ID'].add(ID)
                    continue
                
                hash_ = md5(open(subpath, 'rb').read()).hexdigest()
                if ID in self.hashes and hash_ != self.hashes[ID]:
                    if subpath not in self.needToUpdate['file']:
                        print 'update file', subpath ,'(hash)'
                    self.needToUpdate['ID'].add(ID)
                    self.needToUpdate['file'].add(subpath)
            else:
                self.needToUpdate['dir'].add(subpath)
                self.parseTree(subpath + '/', curr_dic[ID])
    
    def slots(self):
        return super(Mod, self).slots() | self.__slots__

from urllib import urlopen, urlencode


class Packet(object):
    __slots__ = {'__string'}
    
    def __init__(self):
        self.__string = ''
        
    def __str__(self):
        return self.__string
    
    def __len__(self):
        return len(self.__string)

class StreamPacket(Error):
    __slots__ = { 'conn', 'chunk', 'debug_data', 'offset', 'total_processed', 'total_length' }
    
    def __init__(self, url, urldata):
        super(StreamPacket, self).__init__(url, urldata)
        
        try:
            self.conn = urlopen(url, urlencode({'request' : urldata}))
        except IOError as exc:
            self.fail(ErrorCode.Connect, exc.errno)
            return
        except:
            self.fail(ErrorCode.Connect)
            return
        
        self.chunk           = ''
        self.debug_data      = ''
        if DEBUG:
            self.debug_data = 'request:%s;response:'%(urldata)
        
        self.offset          = 0
        self.total_processed = 0
    
    def read_stream(self, size=None):
        data = self.conn.read(size)
        if DEBUG:
            self.debug_data += data
        return data
    
    def slots(self):
        return super(StreamPacket, self).slots()
    
    def bin(self):
        return self.debug_data
    
    def __del__(self):
        if self.conn is not None:
            self.conn.close()


class Logger(object):
    __slots__ = {'log_file'}
    
    def __init__(self):
        self.log_file = open(Paths.LOG_PATH, 'a')
        
        self.log_file.write('Start logging\n\n')
    
    def log(self, *args):
        msg = '[' + Constants.MOD_NAME + ']: '
        
        args_len = len(args)
        for i in xrange(args_len):
            msg += args[i]
            if i < args_len - 1:
                msg += ' '
        
        print msg
        self.log_file.write(msg + '\n')
    
    def __del__(self):
        self.log_file.write('Stop logging')
        self.log_file.close()

class Shared(Error):
    def __init__(self):
        super(Shared, self).__init__()
        
        self.finiHooked = False
        
        self.ID       = None
        self.lic_key  = None
        
        self.respType = ResponseType.GetModsList
        
        self.handlers     = {}
        self.mods         = {}
        self.dependencies = {}
        
        self.undeletedPaths = []
        
        self.__responseData = []
        self.__debugData    = []
        
        self.logger = Logger()
    
    def setupHandler(self, handlerName, func, args):
        self.handlers[handlerName] = {
            'handled' : False,
            'delayed' : False,
            'func'    : func,
            'args'    : tuple(args)
        }
    
    def callHandler(self, handlerName, checkDelayed=False):
        handler = self.handlers[handlerName]
        if handler['handled'] or checkDelayed and handler['delayed']:
            return
        
        handler['handled'] = True
        handler['func'](*handler['args'])
    
    def delayed(self, handlerName):
        self.handlers[handlerName]['delayed'] = True
    
    def fail(self, err, extraCode=0):
        super(Shared, self).fail(err, extraCode)
        
        if isinstance(err, tuple):
            err, extraCode = err
        if isinstance(err, int) or isinstance(err, str):
            err = ErrorCode.__getattr__(err)
        
        self.handleErr(err, extraCode)
        
        import os
        import codecs
        import json
        from time import strftime
        
        self.logger.log('Error %s (%s)'%(err, extraCode))
        
        if not DEBUG:
            return
        
        dump = {
            'name' : 'dump ' + strftime('%d.%m.%Y %H_%M_%S'),
            'data' : {
                'mods'         : [mod.dict()        for mod        in self.mods.values()],
                'dependencies' : [dependency.dict() for dependency in self.dependencies.values()],
                'requestsData' : self.__responseData
            },
            'debug' : self.__debugData
        }
        
        try:
            with codecs.open(Directory['DUMP_DIR'] + dump['name'] + '.json', 'wb', 'utf-8') as dump_file:
                json.dump(dump['data'], dump_file, ensure_ascii=False, sort_keys=True, indent=4)
            
            if DEBUG:
                with open(Directory['DUMP_DIR'] + dump['name'] + '_debug.bin', 'wb') as dbg_file:
                    for i, data in enumerate(dump['debug']):
                        dbg_file.write('packet %s:%s'%(i, data))
            
            self.logger.log('Dump data was saved to', Directory['DUMP_DIR'] + dump['name'])
        except:
            import traceback
            self.logger.log('Unable to save dump data:\n%s'%(traceback.format_exc()))
            
     
    def handleErr(self, err, code):
        g_AUGUIShared.handleErr(err, code)
    
    def createDialogs(self, key):
        g_AUGUIShared.createDialogs(key)
    
    def addResponse(self, response):
        self.__responseData.append(response.dict())
        if DEBUG:
            self.__debugData.append(response.bin())

g_AUShared = Shared()

from struct import pack


class RequestHeader():
    def __init__(self, req_type):
        self.__type = int(req_type)
    
    def get_type(self):
        return self.__type
    
    def __str__(self):
        return chr(self.__type) + pack('I', g_AUShared.ID) + g_AUShared.lic_key

class Request(Packet):
    def __init__(self):
        super(Request, self).__init__()
        
        self.__string = ''
    
    def __iadd__(self, data):
        self.__string += data
        return self
    
    def parse(self, fmt, data):
        self.__string += pack(fmt, data)
    
    def __str__(self):
        return self.__string

def getRequest(req_header, req):
    data = str(req_header) + str(req)
    header = pack('H', 2 + len(data))
    return header + data

import json

from os      import makedirs
from os.path import dirname, exists
from struct  import unpack


class Response(StreamPacket):
    __slots__ = { 'type', 'total_length' }
    
    def __init__(self, urldata, resp_type):
        super(Response, self).__init__(Constants.AUTOUPDATER_URL, urldata)
        
        if not self.check():
            return
        
        self.type         = resp_type
        self.total_length = 0
        
        self.total_length = self.parse('I', 4)[0]
        self.fail_code    = self.parse('B', 1)[0]
        
        if self.total_length < 5:
            self.fail(ErrorCode.RespTooSmall, self.fail_code)
            return
    
    def getChunkSize(self):
        return len(self.chunk) - self.offset
    
    def readChunk(self, size):
        data = self.chunk[self.offset : self.offset + size]
        self.total_processed += size
        self.offset += size
        return data
    
    def readAllChunk(self):
        data = self.chunk[self.offset:]
        self.total_processed += len(data)
        self.offset = len(self.chunk)
        return data
    
    def read(self, size=None):
        if self.offset:
            self.chunk = self.chunk[self.offset : ]
            self.offset = 0
        if not size:
            data = self.read_stream()
            if data:
                self.chunk += data
            return self.readAllChunk()
        else:
            while self.getChunkSize() < size:
                self.chunk += self.read_stream(Constants.CHUNK_MAX_SIZE)
            return self.readChunk(size)
    
    def slots(self):
        return super(Response, self).slots() | self.__slots__
    
    def parse(self, fmt, size):
        data = self.read(size)
        if not data:
            raise EOFError('Could not read the data')
        return unpack(fmt, data)
    
    @staticmethod
    def div1024(value):
        return round(float(value) / 1024, 2)

class ModsListResponse(Response):
    __slots__ = { 'mods', 'deps' }
    
    def __init__(self, *args):
        super(ModsListResponse, self).__init__(*args)
        
        self.mods = {}
        self.deps = {}
        
        self.init()
        
        g_AUShared.addResponse(self)
    
    def init(self):
        if not self.check():
            return
        
        if self.fail_code != ErrorCode.Success:
            self.fail(ErrorCode.GetMods, self.fail_code)
            return
        
        data = {}
        
        try:
            data = json.loads(self.read())
        except:
            self.fail(ErrorCode.RespInvalid, self.fail_code)
            return
        
        if 'mods' not in data:
            self.fail(ErrorCode.ReadMods, self.fail_code)
            return
        
        if 'deps' not in data:
            self.fail(ErrorCode.ReadDeps, self.fail_code)
            return
        
        self.mods = data['mods']
        self.deps = data['deps']
    
    def slots(self):
        return super(ModsListResponse, self).slots() | self.__slots__

class FilesResponse(Response):
    __slots__ = set()
    
    def __init__(self, *args):
        super(FilesResponse, self).__init__(*args)
        
        self.init()
        
        g_AUShared.addResponse(self)
    
    def init(self):
        if not self.check():
            return
        
        files_count = self.parse('I', 4)[0]
        
        for i in xrange(files_count):
            path_len = self.parse('H', 2)[0]
            if path_len > self.total_length:
                self.fail(ErrorCode.InvalidPathLen)
                return
            file_size = self.parse('I', 4)[0]
            if file_size > self.total_length:
                self.fail(ErrorCode.InvalidFileSize)
                return
            
            path = self.read(path_len)
            
            if DEBUG:
                print {
                    'path length' : path_len,
                    'file size'   : file_size,
                    'path'        : path
                }
            
            file_data = self.read(file_size)
            
            try:
                self.createFile(path, file_data)
                return
            except IOError as exc:
                self.fail(ErrorCode.CreateFile, exc.errno)
            except:
                self.fail(ErrorCode.CreateFile)
            
            try:
                self.createManualFile(path, file_data)
                return
            except IOError as exc:
                self.fail(ErrorCode.CreateManualFile, exc.errno)
            except:
                self.fail(ErrorCode.CreateManualFile)
    
    def createFile(self, path, file_data):
        directory = dirname(path)
        if not exists(directory):
            makedirs(directory)
        
        with open('./' + path, 'wb') as fil:
            fil.write(file_data)
    
    def createManualFile(self, path, file_data):
        directory = Directory['FAIL_DIR'] + dirname(path)
        if not exists(directory):
            makedirs(directory)
        
        with open(Directory['FAIL_DIR'] + path, 'wb') as fil:
            fil.write(file_data)
    
    def slots(self):
        return super(FilesResponse, self).slots() | self.__slots__

def getResponse(cls, req):
    respType = g_AUShared.respType
    req_header = RequestHeader(respType)
    
    return cls(getRequest(req_header, req), respType)

import BigWorld
import cPickle

from Account import PlayerAccount

# from PlayerEvents import g_playerEvents

# from helpers import dependency
# from skeletons.gui.shared.utils import IHangarSpace

import traceback
import json

from os      import listdir, makedirs, remove, rmdir
from os.path import exists, isfile

def onGameFini(func, *args):
    g_AUShared.logger.log('starting helper process...')
    
    import platform
    import subprocess
    DETACHED_PROCESS = 0x00000008
    subprocess.Popen(Paths.EXE_HELPER_PATH, creationflags=DETACHED_PROCESS) # shell=True, 
    
    func(*args)

def hookFini():
    if g_AUShared.finiHooked: return
    
    g_AUShared.logger.log('hooking fini...')
    
    try:
        import game
        hookMethod(game, 'fini', onGameFini)
        g_AUShared.finiHooked = True
    except:
        g_AUShared.logger.log('Unable to hook fini:\n%s'%(traceback.format_exc()))

class Autoupdater:
    # hangarSpace = dependency.descriptor(IHangarSpace)
    
    def __init__(self):
        for directory in Directory.values():
            if not exists(directory):
                makedirs(directory)
        
        self.unpackAfterFini = False
        self.deleteAfterFini = False
        
        hookMethod(PlayerAccount, 'showGUI', self.showGUI)
        
        # g_playerEvents.onAccountShowGUI += self.getID
    
    def showGUI(self, func, base, ctx, *args):
        handler_args = [base, ctx]
        handler_args.extend(args)
        g_AUShared.setupHandler('showGUI', func, handler_args)
        
        try:
            self.getID(cPickle.loads(ctx))
        finally:
            g_AUShared.callHandler('showGUI', checkDelayed=True)
    
    def getID(self, ctx): #, *args):
        ID = ctx.get('databaseID', 0)
        
        if not ID:
            g_AUShared.fail(ErrorCode.CheckID)
            return
        
        if ID != g_AUShared.ID:
            g_AUShared.ID = ID
        
        lic_path = Paths.LIC_PATH%(g_AUShared.ID^0xb7f5cba9)
        if not exists(lic_path):
            g_AUShared.fail(ErrorCode.LicNotFound)
            return
        
        try:
            with open(lic_path, 'rb') as lic_file:
                g_AUShared.lic_key = lic_file.read()
        except IOError as exc:
            g_AUShared.fail(ErrorCode.LicNotFound, exc.errno)
            return
        except:
            g_AUShared.fail(ErrorCode.LicNotFound)
            return
        
        if len(g_AUShared.lic_key) != Constants.LIC_LEN:
            g_AUShared.fail(ErrorCode.LicInvalid)
            return
        
        #    self.hangarSpace.onHeroTankReady += self.getModsList
        #
        # def getModsList(self):
        #    self.hangarSpace.onHeroTankReady -= self.getModsList
        #
        #    if not g_AUShared.check(): return
        
        g_AUShared.respType = ResponseType.GetModsList
        
        req = Request()
        req.parse('B', AUTH_REALM)
        
        resp = getResponse(ModsListResponse, req)
        
        if resp.fail_err != ErrorCode.Success:
            g_AUShared.fail(resp.fail_err, resp.fail_code)
            return
        
        g_AUShared.handleErr(resp.fail_err, resp.fail_code)
        
        g_AUShared.respType = ResponseType.GetDeps
        
        toUpdate = {
            'file' : set(),
            'dir'  : set()
        }
        toDelete = {
            'file' : set(),
            'dir'  : set()
        }
        
        for modID in resp.mods:
            mod = g_AUShared.mods[modID] = Mod(resp.mods[modID])
            if mod.fail_err != ErrorCode.Success:
                g_AUShared.fail(mod.fail_err, mod.fail_code)
                return
            mod.parseTree('./', mod.tree)
            
            toUpdate['file'].update(mod.needToUpdate['file'])
            toUpdate['dir'].update(mod.needToUpdate['dir'])
            toDelete['file'].update(mod.needToDelete['file'])
            toDelete['dir'].update(mod.needToDelete['dir'])
        
        for depID in resp.deps:
            dependency = g_AUShared.dependencies[depID] = Mod(resp.deps[depID])
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
    
    def delFiles(self, paths):
        if not g_AUShared.check(): return 0
        
        paths['file'] = filter(lambda path: exists(path),                       paths['file'])
        paths['dir']  = filter(lambda path: exists(path) and not listdir(path), paths['dir'])
        
        g_AUShared.respType = ResponseType.DelFiles
        
        paths_count = len(paths['file']) + len(paths['dir'])
        
        undeletedPaths = []
        
        deleted = 0
        for path in paths['file']:
            try:
                remove(path)
                deleted += 1
                print 'file deleted:', path
            except OSError as exc:
                g_AUShared.undeletedPaths.append(path)
                g_AUShared.logger.log('Unable to delete file %s (errno %s)'%(path, exc.errno))
            except:
                g_AUShared.undeletedPaths.append(path)
                g_AUShared.logger.log('Unable to delete file %s:\n%s'%(path, traceback.format_exc()))
            #else:
            #    g_AUShared.logger.log('File %s is not exists'%(path))
        
        for path in paths['dir']:
            if not listdir(path):
                try:
                    rmdir(path)
                    deleted += 1
                    print 'dir deleted:', path
                except OSError as exc:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s (errno %s)'%(path, exc.errno))
                    #g_AUShared.fail(ErrorCode.DeleteFile, exc.errno)
                    #break
                except:
                    g_AUShared.undeletedPaths.append(path)
                    g_AUShared.logger.log('Unable to delete directory %s:\n%s'%(path, traceback.format_exc()))
                    #g_AUShared.fail(ErrorCode.DeleteFile, exc.errno)
                    #break
            #else:
            #    g_AUShared.logger.log('Directory %s is not empty'%(path))
        
        if g_AUShared.undeletedPaths:
            with open(Paths.DELETED_PATH, 'wb') as fil:
                for path in g_AUShared.undeletedPaths:
                    fil.write(path + '\n')
        
        self.deleteAfterFini = bool(g_AUShared.undeletedPaths)
    
    def process_mods(self, isDependency):
        if not g_AUShared.check(): return
        
        mods = g_AUShared.dependencies if isDependency else g_AUShared.mods
        
        updated = 0
        for modID, mod in mods.iteritems():
            if not mod.needToUpdate['ID']:
                continue
            
            req = Request()
            req.parse('H', int(modID))
            req.parse('I', len(mod.needToUpdate['ID']))
            for updID in mod.needToUpdate['ID']:
                req.parse('I', int(updID))
            
            resp = getResponse(FilesResponse, req)
            
            if resp.fail_err == ErrorCode.Success:
                updated += 1
            elif resp.fail_err == ErrorCode.CreateFile:
                self.unpackAfterFini = True
            else:
                g_AUShared.fail(resp.fail_err, resp.fail_code)
                break
        
        return updated
    
    def getFiles(self):
        if not g_AUShared.check(): return
        
        g_AUShared.respType = ResponseType.GetFiles
        
        updated = 0
        updated += self.process_mods(True)
        updated += self.process_mods(False)
        
        self.onModsUpdated(updated)
    
    def onModsUpdated(self, updated):
        if self.deleteAfterFini:
            key = 'delete'
            hookFini()
        elif self.unpackAfterFini:
            key = 'create'
            hookFini()
        elif updated:
            key = 'update'
        else:
            return
        
        g_AUShared.createDialogs(key)

g_Autoupdater = Autoupdater()
class SimpleErr(Enum):
    Translations     = 1
    CheckID          = 2
    FilesNotFound    = 3
    LicInvalid       = 4
    Connect          = 5
    RespTooSmall     = 6
    RespInvalid      = 7
    ReadMods         = 9
    ReadDeps         = 11
    InvalidPathLen   = 13
    InvalidFileSize  = 14
    CreateFile       = 15
    CreateManualFile = 16
    GetModFields     = 17
    DecodeModFields  = 18
    DeleteFile       = 19

class FormatErr(Enum):
    GetMods  = 8
    GetDeps  = 10
    GetFiles = 12

class GUIPaths:
    LOADER_DIR = Directory['MOD_DIR'] + 'Loader/'
    
    TRANSLATION_PATH = LOADER_DIR + '%s.json'

import json

from os.path import exists


def htmlMsg(msg, color=None, size=None, nl=0):
    fmted =  u'<font%s>%s</font>'
    attrs = ''
    if color is not None:
        attrs += ' color="#%s"'%(color)
    if size is not None:
        attrs += ' size="%s"'%(size)
    
    if not attrs:
        fmted = msg
    else:
        fmted = fmted%(attrs, msg)
    
    return fmted + '<br>'*nl

class GUIShared:
    def __init__(self):
        self.translation = {
            "info" : [
                "Pavel3333 Mods Autoupdater",
                "Author: Pavel3333 from RAINN VOD team",
                "Authors YouTube channel \"RAINN VOD\"",
                "Authors VK Group \"RAINN VOD\"",
            ],
            "msg" : {
                "updated"      : "Autoupdater was updated",
                "deleted"      : "Autoupdater was deleted",
                "unexpected"   : "Unexpected error %s (%s)",
                
                "warn"         : "Warning!",
                
                "subscribe"    : "Subscribe",
                "renew"        : "Renew subscription",
                
                "updated_desc" : "The changes will take effect after the client restarts",
                "restart"      : "Restart",
                
                "close"        : "Close"
            },
            "msg_err" : {
                str(ErrorCode.Translations)     : "An error occured while loading autoupdater translations.\nPlease redownload the autoupdater",
                str(ErrorCode.CheckID)          : "An error occured while checking player ID",
                str(ErrorCode.LicNotFound)      : "License key was not found.\nPlease redownload the autoupdater",
                str(ErrorCode.LicInvalid)       : "License key is invalid",
                str(ErrorCode.Connect)          : "Unable to connect to the server",
                str(ErrorCode.RespTooSmall)     : "An error occured: got empty response",
                str(ErrorCode.RespInvalid)      : "An error occured: got invalid response",
                str(ErrorCode.GetMods)          : "An error occured while getting mod list. Error code %s",
                str(ErrorCode.ReadMods)         : "An error occured while reading mod list",
                str(ErrorCode.GetDeps)          : "An error occured while getting dependencies list. Error code %s",
                str(ErrorCode.ReadDeps)         : "An error occured while reading dependencies list",
                str(ErrorCode.GetFiles)         : "An error occured while getting files. Error code %s",
                str(ErrorCode.InvalidPathLen)   : "Got invalid path length",
                str(ErrorCode.InvalidFileSize)  : "Got invalid file size",
                str(ErrorCode.CreateFile)       : "Unable to update some files.\nThey will be updated after game restart",
                str(ErrorCode.CreateManualFile) : "Unable to update some files and copy it to manual directory.\nPlease contact us",
                str(ErrorCode.GetModFields)     : "Could not get mod data",
                str(ErrorCode.DecodeModFields)  : "Got incorrect mod data",
                str(ErrorCode.DeleteFile)       : "Unable to delete some files.\nThey will be deleted after game restart"
            },
            "msg_warn" : {
                str(WarningCode.CheckID)      : "ID was not found",
                str(WarningCode.GetUserData)  : "You are not subscribed to Autoupdater.<br>You can subscribe it on \"https://pavel3333.ru/trajectorymod/lk\"",
                str(WarningCode.Expired)      : "Autoupdater subscription has expired.<br >You can renew the subscription on \"https://pavel3333.ru/trajectorymod/lk\"",
                str(WarningCode.GetModDesc)   : "Mod was not found"
            }
        }
        
        translation = getJSON(GUIPaths.TRANSLATION_PATH%(str(AUTH_REALM).lower()), self.translation)
        
        if translation is None:
            g_AUShared.fail(ErrorCode.Translations)
            return
        elif isinstance(translation, int):
            g_AUShared.fail(ErrorCode.Translations, translation)
            return
        else:
            self.translation = translation
    
    def getMsg(self, key):
        return self.translation['msg'][key]
    
    def getErrMsg(self, err):
        if isinstance(err, int):
            err = ErrorCode.__getattr__(err)
        return self.translation['msg_err'][str(err)]
    
    def getWarnMsg(self, code):
        if isinstance(code, int):
            code = WarningCode.__getattr__(code)
        return self.translation['msg_warn'][str(code)]
    
    def createDialog(self, *args, **kw):
        simpleDialog = SimpleDialog()
        simpleDialog._submit(*args, **kw)
    
    def createDialogs(self, key):
        func_proceed = lambda: BigWorld.wg_quitAndStartLauncher()
        handler      = lambda: g_AUShared.callHandler('showGUI')
        
        messages_titles = {
            'delete' : (self.getMsg('warn'),    self.getErrMsg(ErrorCode.DeleteFile)),
            'create' : (self.getMsg('warn'),    self.getErrMsg(ErrorCode.CreateFile)),
            'update' : (self.getMsg('updated'), self.getMsg('updated_desc'))
        }
        
        if key is not None:
            title, message = messages_titles[key]
            
            g_AUShared.delayed('showGUI')
            self.createDialog(title=title, message=message, submit=self.getMsg('restart'), close=self.getMsg('close'), func_proceed=func_proceed, handler=handler)
    
    def handleErr(self, err, code=0):
        if err == ErrorCode.Success:
            return
        
        func_proceed = lambda: BigWorld.wg_quitAndStartLauncher()
        handler      = lambda: g_AUShared.callHandler('showGUI')
        
        msg = self.handleServerErr(err, code)
        
        if g_AUShared.respType == ResponseType.GetModsList:
            code_key = {
                int(WarningCode.GetUserData) : 'subscribe',
                int(WarningCode.Expired)     : 'renew'
            }
            
            if code in code_key:
                key = code_key[code]
                
                g_AUShared.delayed('showGUI')
                self.createDialog(
                    title=self.getMsg('warn'),
                    message=msg,
                    submit=self.getMsg(key),
                    close=self.getMsg('close'),
                    url='https://pavel3333.ru/trajectorymod/lk',
                    handler=handler
                )
                return
        
        g_AUShared.delayed('showGUI')
        self.createDialog(
            title=self.getMsg('warn'),
            message=msg,
            close=self.getMsg('close'),
            handler=handler
        )
    
    def handleServerErr(self, err, code):
        if WarningCode.__hasattr__(code):
            return self.getWarnMsg(code)
        elif SimpleErr.__hasattr__(err):
            return self.getErrMsg(err)
        elif FormatErr.__hasattr__(err):
            return self.getErrMsg(err)%(code)
        return self.getMsg('unexpected')%(err, code)

g_AUGUIShared = GUIShared()
