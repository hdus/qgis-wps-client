# -*- coding: utf-8 -*-

"""
Module implementing QgsWpsDockWidget.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgswpsgui import QgsWpsGui
from QgsWpsServerThread import QgsWpsServerThread
import resources_rc


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
        self.dlg = parent
        self.theThread = QgsWpsServerThread()
        QObject.connect(self.theThread, SIGNAL("started()"), self.setProcessStarted)          
        QObject.connect(self.theThread, SIGNAL("finished()"), self.setProcessFinished)          
        QObject.connect(self.theThread, SIGNAL("terminated()"), self.setProcessTerminated)        
        QObject.connect(self.theThread, SIGNAL("serviceFinished(QString)"), self.resultHandler)             
        
            
        self.doc = QtXml.QDomDocument()
        self.tmpPath = QDir.tempPath()
    
        self.tools = QgsWpsTools(self.iface)
        
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        self.dlg.show()
