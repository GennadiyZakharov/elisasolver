'''
Created on 05.11.2013

@author: gena
'''
from __future__ import print_function

from PyQt4 import QtCore
from escore.plate import Plate
from escore.approximations import indexByName

class PlateRecord(object):
    def __init__(self, plate, name,path):
        self.plate=plate
        self.name=name
        self.path=path

class PlateManager(QtCore.QObject):
    '''
    PlateManager holds all plates, and handles related actions,
    such as plate open,save,close,select, etc
    '''
    signalPlateListUpdated=QtCore.pyqtSignal(QtCore.QStringList)
    signalCurrentPlateSet=QtCore.pyqtSignal(object)
    signalCurrentIndexChanged=QtCore.pyqtSignal(int)
    signalApproximationSelected = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(PlateManager, self).__init__(parent)
        self.plates=[]
        self.currentPlateIndex = -1
        self.defaultApproximationIndex=0
    
    def getFileInfo(self,fileName):
        fileInfo=QtCore.QFileInfo(fileName)
        return fileInfo.baseName(), fileInfo.dir()
    
    def openPlate(self, fileName):
        plates = Plate.loadFromFile(fileName)
        for number,plate in enumerate(plates):
            plate.setParent(self)
            if plate.approximation is None:
                print("set default approximation for plate",self.defaultApproximationIndex)
                plate.setApproximation(self.defaultApproximationIndex)   
            name,path = self.getFileInfo(fileName)
            if len(plates)>1:
                name+='_'+str(number+1)
            plateRecord=PlateRecord(plate,name,path)
            self.plates.append(plateRecord)
            plate.signalApplyReference.connect(self.applyReference)
        self.signalPlateListUpdated.emit(self.names())
        if not self.isEmpty():
            self.setCurrentPlate(0)          
            
    def setApproximation(self, index):
        if self.defaultApproximationIndex==index:
            return
        self.defaultApproximationIndex=index
        if self.currentPlateIndex >= 0 :
            self.plates[self.currentPlateIndex].plate.setApproximation(index)
        self.signalApproximationSelected.emit(index)
            
    def openPlates(self, fileNameList):
        for fileName in fileNameList :
            self.openPlate(fileName)
            
    def savePlateAs(self,fileName):
        if self.currentPlateIndex < 0 :
            return
        plateRecord=self.plates[self.currentPlateIndex]
        plateRecord.plate.saveToFile(fileName)
        plateRecord.name,plateRecord.path = self.getFileInfo(fileName)
        self.signalPlateListUpdated.emit(self.names())
        
    def savePlateWithDefaultName(self, index):
        plateRecord=self.plates[index]
        fileInfo=QtCore.QFileInfo(plateRecord.path,plateRecord.name+'.csv')
        plateRecord.plate.saveToFile(fileInfo.filePath())
    
    def savePlate(self):
        if self.currentPlateIndex < 0 :
            return
        self.savePlateWithDefaultName(self.currentPlateIndex)
        
    def saveAllPlates(self):
        for index in range(len(self.plates)):
            self.savePlateWithDefaultName(index)
            
    def removePlate(self):
        if self.currentPlateIndex < 0 :
            return
        self.signalCurrentPlateSet.emit(None)
        self.plates[self.currentPlateIndex].plate.signalApplyReference.disconnect()
        del self.plates[self.currentPlateIndex]
        self.signalPlateListUpdated.emit(self.names())
        if not self.isEmpty():
            self.setCurrentPlate(0)
    
    def isDirty(self):
        return self.plates[self.currentPlateIndex].plate.dirty
    
    def isEmpty(self):
        return self.plates == []
     
    def names(self):
        return QtCore.QStringList([QtCore.QString(record.name) for record in self.plates])
              
    def setCurrentPlate(self, index):
        if self.currentPlateIndex == index :
            return
        self.currentPlateIndex = index
        if index >= 0:
            plate = self.plates[index].plate
            appindex= indexByName(plate.approximation.name)
            self.defaultApproximationIndex = appindex
            self.signalApproximationSelected.emit(appindex)  
        else :
            plate = None
        self.signalCurrentIndexChanged.emit(self.currentPlateIndex)
        self.signalCurrentPlateSet.emit(plate)
        
    def applyReference(self, reference):
        print('Applying reference to all plates')
        sender = self.sender()
        for plateRecord in self.plates:
            plate = plateRecord.plate
            if not plate is sender:
                plate.setReference(reference)
    