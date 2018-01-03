from logging import *
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import os.path as op
import os
from shutil import copy
from distutils.dir_util import copy_tree
import sys
import glob
import zipfile

def logging_getLogger():
    logger = getLogger("DEADBEEF")
    logger._fmt = Formatter('%(relativeCreated)09d | %(levelname)s | %(message)s',"%Y-%m-%d %H:%M:%S")
    logHandler = StreamHandler()
    logHandler.setFormatter(logger._fmt)
    logger.addHandler(logHandler)
    return logger

def logging_log2statusbar(statusbar, logger, formatter):
    QtHandler = _QtLog2StatusBarHandler()
    QtHandler.setFormatter(formatter)
    QtHandler.sig.connect(lambda x: statusbar.showMessage(x, 0))
    logger.addHandler(QtHandler)
    logger.debug("started logging into statusbar")

def logging_log2Textfile(filename, logger, formatter):
    if filename is not None:
        fileHandler = FileHandler(filename)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.debug("started logging into %s", op.abspath(filename))

def logging_log2TextEdit(widget, logger, formatter):
    QtHandler = _QtLog2TextEditHandler()
    QtHandler.setFormatter(formatter)
    QtHandler.sig.connect(widget.append)
    logger.addHandler(QtHandler)
    logger.debug("started logging into text widget")

def logging_LogContextMenu(widget, pos):
    menu = QtWidgets.QMenu()
    clearAction = QtWidgets.QAction("clear",widget)
    clearAction.triggered.connect(widget.clear)
    saveAction = QtWidgets.QAction("save to file",widget)
    saveAction.triggered.connect(lambda: logging_savelog(widget))
    menu.addAction(clearAction)
    menu.addAction(saveAction)
    menu.exec(widget.viewport().mapToGlobal(pos))

def logging_savelog(widget):
    filename = QtWidgets.QFileDialog.getSaveFileName(None, "Save log to ...", "","*.*")
    if filename[0] != "": open(filename[0],"w").write(widget.toPlainText())

class _QtLog2StatusBarHandler(QtCore.QObject,StreamHandler):
    sig = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def emit(self, logRecord):
        msg = self.format(logRecord)
        self.sig.emit(msg)

class _QtLog2TextEditHandler(QtCore.QObject,StreamHandler):
    sig = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def emit(self, logRecord):
        msg = self.format(logRecord)
        self.sig.emit(msg)

class DataManager():
    def __init__(self):
        dataprefix = "data"
        basepath = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        fullpath = op.join(basepath,dataprefix).replace("\\","/")
        
        names = []
        if op.isfile(basepath):
            with zipfile.ZipFile(basepath) as archive:
                for name in archive.namelist():
                    #in this case, the relevant stuff is located under /data/...
                    name = name.replace("\\","/")
                    if name.startswith(dataprefix+"/"): names.append(name)
        else:
            for name in glob.glob(fullpath+"/**/*.*",recursive = True): 
                names.append(name.replace("\\","/"))
        names = [x for x in names if op.isfile(x)]
        names = [x.replace(fullpath+"/", "").replace(dataprefix+"/", "") for x in names]
        dirnames = sorted(list(set([op.dirname(x) for x in names])))
        while True:
            L0 = len(dirnames)
            newDirnames = sorted(list(set([op.dirname(x) for x in dirnames]+dirnames)))
            L1 = len(newDirnames)
            if L0 == L1: break
            dirnames = newDirnames
        self._fileList = names
        self._dirList = dirnames
        self.path = fullpath
        self._basepath = basepath
        self._dataprefix = dataprefix
    
    def getDataPath(self): return self.path
    def getFileList(self, returnHandles = False): return self._fileList
    def getFileContent(self, filepath):
        filepath = filepath.replace("\\", "/")
        if filepath not in self._fileList: return None
        if op.isfile(self._basepath):
            # in this case, we need to access a zip-archive
            with zipfile.ZipFile(self._basepath) as archive:
                return archive.open(self._dataprefix+"/"+filepath)
        else:
            #this is easier: just return the stuff
            return open(op.join(self.path, filepath), "r")
    def storeData(self, srcPath, dstPath, createFolder = False):
        TYPE_FILE = 1
        TYPE_DIR = 2
        type = 0
        nrOfFilesCopied = 0

        if srcPath.replace("\\","/") in self._fileList: type = TYPE_FILE
        elif srcPath.replace("\\","/") in self._dirList: type = TYPE_DIR
        else: return -1

        if type == TYPE_FILE:
            if op.isfile(self._basepath):
                # in this case, we need to access a zip-archive
                pass
            else:
                #this is easier: just return the stuff
                dstDir = op.dirname(dstPath)
                if not op.exists(dstDir): os.makedirs(dstDir, exist_ok=True)
                copy(op.join(self.path, srcPath), dstPath)
                nrOfFilesCopied = 1
        elif type == TYPE_DIR:
            if op.isfile(self._basepath):
                # in this case, we need to access a zip-archive
                pass
            else:
                #this is easier: just return the stuff
                dstDir = op.dirname(dstPath)
                srcDir = op.join(self.path, srcPath)
                if not op.exists(dstDir): os.makedirs(dstDir, exist_ok=True)
                res = copy_tree(srcDir, dstPath, update=1)
                for root, dirs, files in os.walk(srcDir):
                    nrOfFilesCopied += 1

        return nrOfFilesCopied

class PermanentSettings(QtCore.QSettings):
    def __init__(self, creator, applicationName):
        super().__init__(creator, applicationName)
    def getValue(self, name, type = str, defaultValue = None):
        return self.value(name, defaultValue,type = type)
    def setValue(self, name, value):
        super().setValue(name, value)