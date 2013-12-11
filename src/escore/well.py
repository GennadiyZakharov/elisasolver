'''
Created on 02.11.2013

@author: gena
'''
from numpy import NAN
class Well(object):
    '''
    Object represents a single well of plate
    '''
    wellTypeExperiment = 0
    wellTypeReference   = 1
    wellTypeCaptions = ['Experiment','Reference']

    def __init__(self, absorbanse, concentration=NAN):
        self.absorbanse=absorbanse
        self.concentration = concentration
        self.wellType = self.wellTypeExperiment
    
    def setWellType(self, wellType):
        self.wellType=wellType
        
    def setConcentration(self, concentration):
        self.concentration=concentration
    