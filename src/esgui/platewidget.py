'''
Created on 01.11.2013

@author: gena
'''
from PyQt4 import QtCore, QtGui
from string import ascii_uppercase
from numpy import isnan
from escore.well import Well
from esgui.wellwidget import WellWidget
from escore.plate import Plate
from escore.actions import createAction
from escore.reference import Reference
import imagercc


class PlateWidget(QtGui.QTableWidget):
    '''
    Widget to show plate data and execute plate-related dialogs
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(PlateWidget, self).__init__(Plate.plateSizeRows, Plate.plateSizeColumns, parent)
        self.plate=None
        self.lastDirectory = '.'
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers);
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        header = self.verticalHeader()
        header.setClickable(True)
        #header.sectionClicked.connect(self.chamberSelectionChanged)
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.setVerticalHeaderLabels(ascii_uppercase[:self.columnCount()])
        self.itemDoubleClicked.connect(self.editWell)
        self.fitCoefficientsAction = createAction(self,"Fit Coefficients", '', 
                                          "accessories-calculator", "")
        self.fitCoefficientsAction.triggered.connect(self.fitCoefficients)
        self.calculateConcentrationsAction = createAction(self,"Calculate Concentrations", '', 
                                          "run-build-install", "")
        self.calculateConcentrationsAction.triggered.connect(self.calculateConcentrations)
        setWellTypeAction = createAction(self,"Set well(s) type...", '', 
                                          "story-editor", "")
        setWellTypeAction.triggered.connect(self.editMultipleWels)
        
        #
        openReferenceAction = createAction(self, 'Open reference...', '',
                                          'document-open', '')
        openReferenceAction.triggered.connect(self.openReference)
        saveReferenceAction = createAction(self, 'Save reference...', '',
                                          'document-save', '')
        saveReferenceAction.triggered.connect(self.saveReference)
        applyToAllAction = createAction(self, 'Apply to all', '',
                                          'edit-copy', '')
        applyToAllAction.triggered.connect(self.applyToAll)
        #
        self.actions=(self.fitCoefficientsAction,self.calculateConcentrationsAction, 
                      setWellTypeAction)
        self.referenceActions=(openReferenceAction,saveReferenceAction,applyToAllAction)
        self.addAction(setWellTypeAction)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.setPlate(None)
        
    def setWell(self, row,column):
        well = self.plate[row,column]
        caption = 'a:{:6.3f}\n'.format(well.absorbanse)
        if not isnan(well.concentration) :
            caption += 'c:{:6.3f}'.format(well.concentration)
            if well.wellType == Well.wellTypeReference :
                color = QtGui.QColor(220,255,220)
            else :
                color = QtGui.QColor(220,220,255)
        else :
            color = QtGui.QColor(255,255,220)
        item = QtGui.QTableWidgetItem(caption)
        item.setBackgroundColor(color)
        self.setItem(row,column,item)
        
    def saveToFile(self,fileName):
        self.plate.saveToFile(fileName)
    
    def setPlate(self, plate):
        if self.plate is not None:
            self.plate.signalPlateUpdated.disconnect()
            self.plate.signalWellUpdated.disconnect()
            self.plate.signalApproximationFitted.disconnect()
        self.clearContents()
        self.plate = plate 
        self.setEnabled(self.plate is not None)
        for action in self.actions:
            action.setEnabled(self.plate is not None)
        for action in self.referenceActions :
            action.setEnabled(self.plate is not None)
        if self.plate is not None :
            self.plate.signalPlateUpdated.connect(self.updateTable)
            self.plate.signalWellUpdated.connect(self.setWell)
            self.plate.signalApproximationFitted.connect(self.calculateConcentrationsAction.setEnabled)
            self.calculateConcentrationsAction.setEnabled(self.plate.approximation.isFitted())
            self.updateTable()
         
    def updateTable(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                self.setWell(row, column)
    
    def editWell(self, item):
        index = self.indexFromItem(item)
        row,column = index.row(),index.column()
        wellWidget = WellWidget(self.plate[row,column],self)
        if wellWidget.exec_():
            self.plate[row,column]=wellWidget.getWell()    
    
    def editMultipleWels(self):
        indexes = self.selectedIndexes()
        if indexes == []:
            return
        index = indexes[0]
        row,column = index.row(),index.column()
        wellWidget = WellWidget(self.plate[row,column],self)
        if wellWidget.exec_():
            for index in indexes :
                row,column = index.row(),index.column()
                self.plate[row,column]=wellWidget.getWell()
         
    def fitCoefficients(self):
        plot = self.plate.fitCoefficients()
        plot.show()
        #plot.figure.canvas.manager.window.activateWindow()
         
    def calculateConcentrations(self):
        self.plate.calculateConcentrations()   
        
    def openReference(self):
        # Creating formats list
        formats = ["*.{}".format(Reference.fileFormat)]
        
        fname = QtGui.QFileDialog.getOpenFileName(self,
                        "Open reference file",
                        self.lastDirectory, 'ELISA reference ({})'.format(" ".join(formats)))
        if not fname.isEmpty() :
            #FIX: lastDirectory is QDir
            self.lastDirectory = QtCore.QFileInfo(fname).absolutePath()
            self.plate.openReference(fname)
    
    def saveReference(self):
        formats = ["*.{}".format(Reference.fileFormat)]
        # Executing standard open dialog
        fname = QtGui.QFileDialog.getSaveFileName(self,
                        "Save reference...",
                        self.lastDirectory, "ELISA reference ({})".format(" ".join(formats)))
        if not fname.isEmpty() :
            self.plate.saveReference(fname)
    
    def applyToAll(self):
        self.plate.applyToAll()
            