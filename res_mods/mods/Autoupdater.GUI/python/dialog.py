# Author: Ekspoint

import BigWorld
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta

__all__ = ('SimpleDialog',)

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
    def openUrlUp(self, url=None):
        if url is not None:
            return BigWorld.wg_openWebBrowser(url)
    
    def _close(self, title=None, message=None, close=None):
        return showDialog(SimpleDialogMeta(title=title, message=message, buttons=DialogButtons(close=close)), None)
    
    def _submit(self, title=None, message=None, submit=None, close=None, url=None, func=None):
        if func is None:
            func = lambda proceed: self.openUrlUp(url) if proceed else None
        
        return showDialog(SimpleDialogMeta(title=title, message=message, buttons=DialogButtons(submit=submit, close=close)), func)
