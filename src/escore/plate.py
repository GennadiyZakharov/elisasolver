'''
Created on 01.11.2013

@author: gena
'''
from __future__ import division,print_function
from PyQt4 import QtCore
import numpy as np
from StringIO import StringIO
from escore.well import Well
from escore.approximations import approximations,indexByName
from escore.reference import Reference

class Plate(QtCore.QObject):
    '''
    Holds and handles all data for single plate -- 
    absorbtions, reference, approximation, concentration
    '''
    plateSizeRows = 8
    plateSizeColumns = 12
    plateSize=(plateSizeRows,plateSizeColumns)
    inputTitle = 'Plate'
    outputTitle = 'ElisaSolver plate output'
    formats = ['txt','csv']
    signalPlateUpdated = QtCore.pyqtSignal() # Updated all plate
    signalWellUpdated  = QtCore.pyqtSignal(int,int) # Updated all plate
    signalApproximationFitted = QtCore.pyqtSignal(bool)
    signalApplyReference = QtCore.pyqtSignal(object)
    
    def __init__(self, absorbanses, parent=None):
        super(Plate, self).__init__(parent)
        self.absorbanses = absorbanses
        self.concentrations = np.empty(self.plateSize)
        self.concentrations[:]=np.NAN
        self.approximation = None
        self.reference = Reference()
        self.notes = None
        self.dirty = False
    
    def __getitem__(self, index):
        '''
        return esWell from plate
        '''
        well = Well(self.absorbanses[index], self.concentrations[index])
        if index in self.reference.keys() :
            well.setWellType(Well.wellTypeReference)
            well.setConcentration(self.reference[index])
        return well
           
    def __setitem__(self, index, well):
        '''
        Store esWell in plate
        '''
        if self.isWellEmpty(*index):
            return
        if well.wellType == Well.wellTypeReference :
            self.reference[index]=well.concentration
        else:
            self.reference.remove(index)
        self.signalWellUpdated.emit(*index)
    
    def isWellEmpty(self, row,column):
        return np.isnan(self.absorbanses[row,column])
    
    def resetApproximation(self):
        '''
        Clear approximation coefficients and calculated concentrations
        '''
        self.approximation.p = None
        self.concentrations[:]=np.NAN
        self.dirty=True
        self.signalPlateUpdated.emit()
        self.signalApproximationFitted.emit(False)
    
    @classmethod
    def readTable(cls, plateFile):
        '''
        read One plate record from IOStream
        '''
        lines = []
        plateFile.readline()
        for i in range(cls.plateSizeRows):
            lines.append(plateFile.readline())
        c = StringIO('\n'.join(lines))
        return np.loadtxt(c,delimiter=';')
    
    @classmethod
    @QtCore.pyqtSlot(QtCore.QString)
    def loadFromFile(cls, fileName):
        '''
        Read plate file and return list of plate records, or empty list if reading was unsucsessfull
        '''
        def wellFromLine(line):
            column = int(line[1:])-1
            row = ord(line[0])-ord('A')
            return row,column
        
        plateFile = open(unicode(fileName))
        caption = plateFile.readline().strip()
        if caption.startswith(cls.inputTitle) :
            print('Loading plate from txt')
            plateNumber = 1
            absorbanses = np.empty(cls.plateSize)
            absorbanses[:]=np.NAN
            plates = []
            print('parsing plate',plateNumber)
            while True:
                line = plateFile.readline().split()
                isEndFile=not line[0].isdigit()
                if isEndFile or (int(line[0])>plateNumber) : # writing plate record
                    plate = cls(absorbanses)
                    plates.append(plate)
                    print('Loaded plate absorbances')
                    print(absorbanses)
                    if isEndFile:
                        break
                    plateNumber+=1
                    absorbanses = np.zeros(cls.plateSize)
                    print('parsing plate',plateNumber)
                wellline=line[2]
                row,column = wellFromLine(wellline)
                absorbanses[row, column] = float(line[-1])
            
            line = ''
            while not line.strip() == 'Protocol description':
                line = plateFile.readline()
            notes = plateFile.readlines() 
            for plate in plates :
                plate.notes=notes
            return plates
        elif caption == cls.outputTitle :
            print('Loading plate from ElisaSolver csv')
            plateFile.readline()
            plateFile.readline()
            absorbanses=cls.readTable(plateFile)
            plate = cls(absorbanses)
            plateFile.readline()
            appName = plateFile.readline().split(':')[1].strip()
            index= indexByName(appName)
            plate.setApproximation(index)
            plateFile.readline()
            strP = plateFile.readline().strip()
            if strP != '' :
                p = np.array([float(item) for item in strP.split(';')])
            else:
                p=None
            plate.reference=Reference.loadFromFile(plateFile)
            print('Reference cells: ',plate.reference)
            plateFile.readline()
            plateFile.readline()
            plate.concentrations= cls.readTable(plateFile)
            plate.notes = plateFile.readlines()
            print('Approximation: ',plate.approximation.name)
            plate.approximation.p = p
            print('Coefficients: ',p)
            plate.dirty = False
            return [plate]
        else :
            return []
    
    @QtCore.pyqtSlot(QtCore.QString)
    def saveToFile(self, fileName):
        '''
        Save plate to ElisaSolver csv
        '''
        print('Saving plate to file: ',fileName)
        plateFile = open(unicode(fileName), 'w')
        plateFile.write(self.outputTitle+'\n\n')
        plateFile.write('Raw absorbanses data:\n')
        numbers = ';'.join(['{:8}'.format(i+1) for i in range(12)])+'\n'
        plateFile.write(numbers)
        np.savetxt(plateFile, self.absorbanses, fmt='%8.3f',delimiter=';')
        plateFile.write('\nApproximation type: {}\n'.format(self.approximation.name))
        plateFile.write('Coefficients:\n')
        if self.approximation.p is not None:
            strP='; '.join([str(coef) for coef in self.approximation.p])
        else:
            strP=''     
        plateFile.write(strP+'\n')
        self.reference.saveToFile(plateFile)
        plateFile.write('\nCalculated concentrations:\n')
        plateFile.write(numbers)
        np.savetxt(plateFile, self.concentrations, fmt='%8.3f',delimiter=';')
        if self.notes is not None :
            plateFile.writelines(self.notes)
        self.dirty = False
    
    def setApproximation(self, index):
        '''
        Set approximation by index
        '''
        self.approximation=approximations[index]()
        self.resetApproximation()
    
    def prepareCalibration(self):
        '''
        Form the list of x and y data from calibration
        '''
        if self.reference.isEmpty() :
            print('No reference cells selected')
            return [],[]
        print('Preparing calibration...')
        print('Reference cells: ',self.reference)
        wellsByConc = {}
        for index,concentration in self.reference.iteritems() :
            absorbance = self.absorbanses[index]
            rConc=round(concentration,2)
            if rConc not in wellsByConc.keys() :
                wellsByConc[rConc]=[absorbance]
            else :
                wellsByConc[rConc].append(absorbance)
        x = [conc for conc in wellsByConc.keys()]
        x.sort()
        print('Reference data:')
        print(x)
        y = []
        for conc in x :
            yList=wellsByConc[conc]
            y.append(sum(yList)/len(yList))
        print(y)
        return x,y

    def fitCoefficients(self):
        '''
        Fit approximation coefficients according to current calibration
        '''
        x,y = self.prepareCalibration()
        if len(x)<self.approximation.referenceCount :
            print('Reference list is too short ',len(x))
            print('Need at least ',self.approximation.referenceCount)
            return None
        x = np.array(x)
        y = np.array(y)
        self.approximation.fitPvals(x,y)
        self.dirty=True  
        self.signalApproximationFitted.emit(True)
        return self.approximation.fitPlot          
            
    def calculateConcentrations(self):
        '''
        Calculate concentrations according to current calibration
        '''
        if not self.approximation.isFitted():
            return
        print('Calculating concentrations:')
        for row in range(self.plateSizeRows):
            for column in range(self.plateSizeColumns):
                if not self.isWellEmpty(row, column) :
                    self.concentrations[row,column]=self.approximation.invEval(self.absorbanses[row,column])
        
        self.dirty = True
        self.signalPlateUpdated.emit()
    
    @QtCore.pyqtSlot(QtCore.QString)
    def openReference(self, fileName):
        referenceFile = open(unicode(fileName))
        reference = Reference.loadFromFile(referenceFile)
        if reference is not None :
            self.setReference(reference)
        referenceFile.close()
    
    @QtCore.pyqtSlot(QtCore.QString)
    def saveReference(self, fileName):
        referenceFile = open(unicode(fileName),'w')
        self.reference.saveToFile(referenceFile)
        referenceFile.close()
    
    def setReference(self, reference):
        self.reference = reference
        self.resetApproximation()
        
    def applyToAll(self):
        '''
        Send curent reference with signal signalApplyReference
        '''
        if not self.reference.isEmpty():
            self.signalApplyReference.emit(self.reference)