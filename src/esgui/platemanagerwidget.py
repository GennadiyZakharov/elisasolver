'''
Created on 06.11.2013

@author: gena
'''


from PyQt4 import QtGui
from escore.actions import createAction
from escore.plate import Plate
from escore.platemanager import PlateManager
import imagercc

class PlateManagerWidget(QtGui.QWidget):
    '''
    Widget represets plate manager -- list of plates
    Also handles actions -- plate opening, closing, saving, etc
    '''
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(PlateManagerWidget, self).__init__(parent)
        self.plateManager = PlateManager(self)
        self.plateManager.signalPlateListUpdated.connect(self.updatePlateList)
        layout = QtGui.QVBoxLayout()
        self.plateListWidget = QtGui.QListWidget()
        self.plateListWidget.setEnabled(False)
        self.plateListWidget.currentRowChanged.connect(self.plateManager.setCurrentPlate)
        self.plateListWidget.currentRowChanged.connect(self.plateSelectionChange)
        self.plateManager.signalCurrentIndexChanged.connect(self.plateListWidget.setCurrentRow)
        layout.addWidget(self.plateListWidget)
        self.setLayout(layout)
        # Actions
        openPlateAction = createAction(self, 'Open plate(s)...', QtGui.QKeySequence.Open,
                                          'document-open', '')
        openPlateAction.triggered.connect(self.openPlate)
        savePlateAction = createAction(self, 'Save plate', QtGui.QKeySequence.Save,
                                          'document-save', '')
        savePlateAction.triggered.connect(self.plateManager.savePlate)
        savePlateAsAction = createAction(self, 'Save plate As...', QtGui.QKeySequence.SaveAs,
                                          'document-save-as', '')
        savePlateAsAction.triggered.connect(self.savePlateAs)
        saveAllPlatesAction = createAction(self, 'Save All plates', '',
                                          'document-save-all', '')
        saveAllPlatesAction.triggered.connect(self.plateManager.saveAllPlates)
        closePlateAction = createAction(self, 'Close plate', QtGui.QKeySequence.Close,
                                          'dialog-close', '')
        closePlateAction.triggered.connect(self.closePlate)
        self.actions = (openPlateAction, None, savePlateAction, savePlateAsAction,
                        saveAllPlatesAction, None, closePlateAction, None)
        self.saveActions = (savePlateAction, savePlateAsAction,
                        saveAllPlatesAction, closePlateAction)
        self.lastDirectory = '.'
        self.plateSelectionChange(-1)
        
        
    def updatePlateList(self, names):
        self.plateListWidget.clear()
        empty = self.plateManager.isEmpty()
        self.plateListWidget.setEnabled(not empty)
        if not empty :
            self.plateListWidget.addItems(names)
            
    def openPlate(self):
        '''
        Open plate file
        '''
        # Creating formats list
        formats = ["*.{}".format(unicode(fmt)) for fmt in Plate.formats]
        dialog = QtGui.QFileDialog(self, 'Open input Files',
                                   self.lastDirectory)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles);
        dialog.setNameFilter('ELISA data files ({})'.format(" ".join(formats)))
        if dialog.exec_() :
            # Display selected list
            filesList = dialog.selectedFiles()
            self.plateManager.openPlates(filesList)
            self.lastDirectory = dialog.directory().absolutePath()
    
    def savePlateAs(self):
        formats = ["*.{}".format(unicode(fmt)) \
                   for fmt in Plate.formats]
        # Executing standard open dialog
        fname = QtGui.QFileDialog.getSaveFileName(self,
                        "Choose file to save ElisaFit data",
                        self.lastDirectory, "Data files ({})".format(" ".join(formats)))
        if not fname.isEmpty() :
            self.plateManager.savePlateAs(fname)

    def closePlate(self):
        reply = QtGui.QMessageBox.Yes
        if self.plateManager.isDirty():
            reply = QtGui.QMessageBox.question(self,
                                         " Unsaved Changes",
                                         "Save unsaved changes for plate?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | 
                                         QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return reply
            elif reply == QtGui.QMessageBox.Yes:
                self.plateManager.savePlate()
        self.plateManager.removePlate()
        return reply
    
    def closeAllPlates(self):
        reply = QtGui.QMessageBox.Yes
        while not self.plateManager.isEmpty():
            reply = self.closePlate()
            if reply == QtGui.QMessageBox.Cancel:
                break
        return reply
    
    def plateSelectionChange(self, index):
        for action in self.saveActions:
            action.setEnabled(index >= 0)
    
    def isDirty(self):
        return self.plateManager.isDirty()
