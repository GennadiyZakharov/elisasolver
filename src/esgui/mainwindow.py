'''
Created on 01.11.2013

@author: gena
'''
from PyQt4 import QtCore, QtGui


from esgui.platewidget import PlateWidget
from esgui.platemanagerwidget import PlateManagerWidget
from escore.actions import addActions,createAction
from escore.approximations import approximations
from escore.consts import applicationName,applicationVersion
import imagercc

class MainWindow(QtGui.QMainWindow):
    '''
    Main window for elisaSolver
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(MainWindow, self).__init__(parent)
        self.setObjectName("esMainWindow") 
        self.setWindowTitle(applicationName+' '+str(applicationVersion))
        self.plateWidget=PlateWidget()
        #
        mainWindow=QtGui.QWidget()
        layout = QtGui.QGridLayout()
        typeLabel = QtGui.QLabel('Approximation type:')
        layout.addWidget(typeLabel,0,0)
        self.typeComboBox = QtGui.QComboBox()
        self.typeComboBox.addItems([approximation.name for approximation in approximations])
        
        layout.addWidget(self.typeComboBox,0,1)
        layout.addWidget(self.plateWidget,1,0,1,2)
        mainWindow.setLayout(layout)
        
        
        self.setCentralWidget(mainWindow)
        #
        self.plateManagerWidget = PlateManagerWidget(self)
        plateManagerPanel = QtGui.QDockWidget('Plates', self)
        plateManagerPanel.setObjectName('plateManagerPanel')
        plateManagerPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        plateManagerPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, plateManagerPanel) 
        plateManagerPanel.setWidget(self.plateManagerWidget)
        self.plateManagerWidget.plateManager.signalCurrentPlateSet.connect(self.plateWidget.setPlate)
        self.typeComboBox.currentIndexChanged.connect(self.plateManagerWidget.plateManager.setApproximation)
        self.plateManagerWidget.plateManager.signalApproximationSelected.connect(self.typeComboBox.setCurrentIndex)
        # Menu
        
        projectMenu = self.menuBar().addMenu("&File")
        addActions(projectMenu, self.plateManagerWidget.actions)
        quitAction = createAction(self,'Exit...', QtGui.QKeySequence.Quit, 
                                          'application-exit', 'Exit program')
        projectMenu.addAction(quitAction)
        quitAction.triggered.connect(self.close) 
        
        plateMenu = self.menuBar().addMenu('&Plate')
        addActions(plateMenu, self.plateWidget.actions)
        referenceMenu = self.menuBar().addMenu('&Reference')
        addActions(referenceMenu, self.plateWidget.referenceActions)
        # Restore window settings
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value('esMainWindow/Geometry').toByteArray())
        self.restoreState(settings.value('esMainWindow/State').toByteArray())
        self.plateManagerWidget.lastDirectory = settings.value('lastDirectory').toString()
        self.plateWidget.lastDirectory = settings.value('referenceLastDirectory').toString()
        index, isOK = settings.value('defaultApproximationIndex').toInt()
        if isOK :
            self.typeComboBox.setCurrentIndex(index)
    
    def closeEvent(self, event):
        # Asking user to confirm
        reply = self.plateManagerWidget.closeAllPlates()
        if reply == QtGui.QMessageBox.Cancel :
            event.ignore()
            return
        # Save settings and exit 
        settings = QtCore.QSettings()
        settings.setValue("esMainWindow/Geometry", 
                              QtCore.QVariant(self.saveGeometry()))
        settings.setValue("esMainWindow/State", 
                              QtCore.QVariant(self.saveState()))
        settings.setValue('lastDirectory',QtCore.QVariant(self.plateManagerWidget.lastDirectory))
        settings.setValue('referenceLastDirectory',QtCore.QVariant(self.plateWidget.lastDirectory))
        settings.setValue('defaultApproximationIndex',QtCore.QVariant(self.typeComboBox.currentIndex()))
        event.accept()