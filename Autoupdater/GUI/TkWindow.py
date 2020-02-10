from Tkinter import Tk, HORIZONTAL
from ttk import Progressbar, Label

class SimpleTkWindow(object):
    def __init__(self, title, status):
        self.root = Tk()
        self.root.title(title)
        self.root.iconbitmap(Paths.ICON_PATH)
        #self.root.geometry('320x240')
        
        self.status = Label(
            self.root,
            text=status
        )
        self.status.pack(pady = 10)
        
        self.progressText = Label(
            self.root,
            text=''
        )
        self.progressText.pack(pady = 10)
        
        self.progress = Progressbar(
            self.root,
            orient = HORIZONTAL, 
            length = 250,
            mode = 'determinate'
        )
        self.progress.pack(pady = 10)

        self.setProgress(0, 0, '')
    
    def __del__(self):
        self.root.update()
        self.root.destroy()

    def getProgress(self, processed, total):
        if not total: return 0
        return int(100.0 * (float(processed) / float(total)))

    def setProgress(self, processed, total, unit, isTotalProgress=False):
        progressValue = self.getProgress(processed, total)
        progressText  = '%s/%s %s'%(processed, total, DataUnits[unit] if unit in xrange(len(DataUnits)) else '')

        progressAttr     = 'progress' if not isTotalProgress else 'totalProgress'
        progressTextAttr = progressAttr + 'Text'
        
        if hasattr(self, progressAttr):
            getattr(self, progressAttr)['value'] = progressValue

        if hasattr(self, progressTextAttr):
            getattr(self, progressTextAttr)['text'] = progressText
        
        self.root.update()

    def setStatus(self, text):
        self.status['text'] = text
        self.root.update()

    def setTitle(self, title):
        self.root.title(title)

class ExtraProgressWindow(SimpleTkWindow):
    def __init__(self, title, status):
        super(ExtraProgressWindow, self).__init__(title, status)

        self.progressDesc = Label(
            self.root,
            text=''
        )
        self.progressDesc.pack(pady = 10)
        
        self.totalProgressText = Label(
            self.root,
            text=''
        )
        self.totalProgressText.pack(pady = 10)
        
        self.totalProgress = Progressbar(
            self.root,
            orient = HORIZONTAL, 
            length = 250,
            mode = 'determinate'
        )
        self.totalProgress.pack(pady = 10)

        self.setProgress(0, 0, '', True)

    def setText(self, text):
        self.progressDesc['text'] = text
        self.root.update()
