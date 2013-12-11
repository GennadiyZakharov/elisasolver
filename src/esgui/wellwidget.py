'''
Created on 01.11.2013

@author: gena
'''
from PyQt4 import QtGui
from escore.well import Well

class WellWidget(QtGui.QDialog):
    '''
    Widget to edit well type (reference or experiment) and reference concentration
    '''
    def __init__(self, well, parent=None):
        '''
        Constructor
        '''
        super(WellWidget, self).__init__(parent)
        self.well=well
        layout = QtGui.QGridLayout()
        typeLabel = QtGui.QLabel('Well type:')
        layout.addWidget(typeLabel,0,0)
        self.typeComboBox = QtGui.QComboBox()
        self.typeComboBox.addItems(Well.wellTypeCaptions)
        self.typeComboBox.setCurrentIndex(well.wellType)
        self.typeComboBox.currentIndexChanged.connect(self.setWellType)
        layout.addWidget(self.typeComboBox,0,1)
        #
        concentrationLabel = QtGui.QLabel('Concentration:')
        layout.addWidget(concentrationLabel)
        self.concentrationSpinBox = QtGui.QDoubleSpinBox()
        self.concentrationSpinBox.setDecimals(3)
        self.concentrationSpinBox.setMaximum(1000)
        self.concentrationSpinBox.setSuffix(' ng/ml')
        self.concentrationSpinBox.setEnabled(well.wellType == Well.wellTypeReference)
        self.concentrationSpinBox.valueChanged.connect(self.setWellConcentration)
        if well.wellType == Well.wellTypeReference :
            self.concentrationSpinBox.setValue(well.concentration)
        else :
            self.concentrationSpinBox.setValue(0)
        layout.addWidget(self.concentrationSpinBox)
        # Ok/Close buttonbox
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close | QtGui.QDialogButtonBox.Ok,
                                           accepted=self.accept,
                                           rejected=self.reject)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout) 
        
    def setWellType(self, index):
        self.well.setWellType(index)
        self.concentrationSpinBox.setEnabled(self.typeComboBox.currentIndex()==Well.wellTypeReference)
        if index == Well.wellTypeReference :
            self.well.setConcentration(self.concentrationSpinBox.value())
    
    def setWellConcentration(self, value):
        self.well.setConcentration(value)
        '''
        if value  <= 0.5 :
            self.concentrationSpinBox.setSingleStep(0.01)
        elif value <= 1.0 :
            self.concentrationSpinBox.setSingleStep(0.1)
        elif value <= 10 :
            self.concentrationSpinBox.setSingleStep(1.0)
        elif value <= 50 :
            self.concentrationSpinBox.setSingleStep(5.0)
        else :
            self.concentrationSpinBox.setSingleStep(10.0)
        '''

    def getWell(self):
        return self.well
        