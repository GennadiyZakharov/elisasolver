'''
Created on 05.11.2013

@author: gena
'''
from __future__ import division,print_function

class Reference(dict):
    '''
    Reference cell set to calibrate
    Consists in dictionaly with (row,column) in key, and concentration in stored value
    '''
    caption = 'Reference cells:'
    fileFormat = 'esr'

    def isEmpty(self):
        return (len(self)==0)
        
    def remove(self, index):
        if index in self.keys():
            del self[index]
            
    def saveToFile(self, fileStream):
        fileStream.write(self.caption+'\n')
        fileStream.write(repr(self)+'\n')
    
    @classmethod
    def loadFromFile(cls, fileStream):
        caption=fileStream.readline().strip()
        if caption != cls.caption :
            print('Illegal caption: '+caption)
            raise
        return cls(eval(fileStream.readline()))
