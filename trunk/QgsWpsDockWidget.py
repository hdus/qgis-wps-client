# -*- coding: utf-8 -*-

"""
Module implementing QgsWpsDockWidget.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgswpsgui import QgsWpsGui


from Ui_QgsWpsDockWidget import Ui_QgsWpsDockWidget

class QgsWpsDockWidget(QDockWidget, Ui_QgsWpsDockWidget):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDockWidget.__init__(self, parent)
        self.setupUi(self)
        self.iface = parent
        
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.dlg = QgsWpsGui(self.iface.mainWindow(),  flags)    

        self.dlg.initQgsWpsGui()
        self.dlg.show()
