#!/usr/bin/env python

import sys
from PyQt4.QtGui import QApplication, QIcon
from os.path import join, abspath, pardir

# Add src and resources to python path
sys.path.append(abspath(join(pardir, 'src')))
sys.path.append(abspath(join(pardir, 'resources')))

# Import modules
from escore.consts import applicationName, applicationVersion, \
    organizationName, organizationDomain
from esgui.mainwindow import MainWindow
import imagercc

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(organizationName)
    app.setOrganizationDomain(organizationDomain)
    app.setApplicationName(applicationName + ' ' + applicationVersion)
    app.setWindowIcon(QIcon(":/kspread.png"))
    mainWindow = MainWindow()
    mainWindow.show()
    return app.exec_()

if __name__ == '__main__':
    main()

