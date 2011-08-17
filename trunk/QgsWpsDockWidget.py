# -*- coding: utf-8 -*-

"""
Module implementing QgsWpsDockWidget.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from PyQt4 import QtWebKit
from qgswpsgui import QgsWpsGui
from QgsWpsServerThread import QgsWpsServerThread
from qgswpstools import QgsWpsTools
from qgswpsgui import QgsWpsGui

import resources_rc


from Ui_QgsWpsDockWidget import Ui_QgsWpsDockWidget

class QgsWpsDockWidget(QDockWidget, Ui_QgsWpsDockWidget):
    """
    Class documentation goes here.
    """
    def __init__(self, iface):
        """
        Constructor
        """
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        
        self.tools = QgsWpsTools(self.iface)
        
        self.theThread = QgsWpsServerThread()
        QObject.connect(self.theThread, SIGNAL("started()"), self.setProcessStarted)          
        QObject.connect(self.theThread, SIGNAL("finished()"), self.setProcessFinished)          
        QObject.connect(self.theThread, SIGNAL("terminated()"), self.setProcessTerminated)        
        QObject.connect(self.theThread, SIGNAL("serviceFinished(QString)"), self.tools.resultHandler) 
        
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.dlg = QgsWpsGui(self.iface.mainWindow(),  flags)    
        QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.tools.createProcessGUI)    
        QObject.connect(self.dlg, SIGNAL("newServer()"), self.tools.newServer)    
        QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.tools.editServer)    
        QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.tools.deleteServer)        
        QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.dlg.createCapabilitiesGUI)    
        
            
        self.doc = QtXml.QDomDocument()
        self.tmpPath = QDir.tempPath()
    

        
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        self.dlg.initQgsWpsGui()
        self.dlg.show()
        
        
    
    def setProcessStarted(self):
#      self.dlgProcess.lneStatus.setText("Process started and running ... ")
        groupBox = QGroupBox(self.myDockWidget.groupBox)
        layout = QHBoxLayout()
        self.lblProcess = QLabel(groupBox)
        self.lblProcess.setText(QString("Process "+self.processIdentifier+" running ..."))

        self.btnProcessCancel = QToolButton(groupBox)
        self.btnProcessCancel.setIcon(QIcon(":/plugins/wps/images/button_cancel.png") )
        self.btnProcessCancel.setMinimumWidth(30)
        self.btnProcessCancel.setMaximumWidth(30)
        layout.addWidget(self.lblProcess)
        layout.addStretch(10)
        layout.addWidget(self.btnProcessCancel)

        self.myDockWidget.groupBox.setLayout(layout)
        self.myDockWidget.btnConnect.setEnabled(False)
        QObject.connect(self.btnProcessCancel,SIGNAL("clicked()"),self.terminateProcessing)
        pass


    def setProcessFinished(self):
        self.iface.mainWindow().statusBar().removeWidget(self.statusLabel)
        self.lblProcess.setText('Process finished')
        self.myDockWidget.btnConnect.setEnabled(True)
        QMessageBox.information(self.iface.mainWindow(),'Status', "Process "+self.processIdentifier+" finished")
      
    def setProcessTerminated(self):
        QMessageBox.information(None,'Status', "Process "+self.processIdentifier+" terminated")
        self.myDockWidget.btnConnect.setEnabled(True)

        
    def closeDialog(self):
      self.close()
      
    def removeProcessFromWidget(self):
      pass

    def terminateProcessing( self ):
       if self.theThread != None:
         self.theThread.terminate()
         self.theThread = None    
         self.lblProcess.setText('Process '+self.processIdentifier+' terminated')
         btnProcessRemove = self.btnProcessCancel
         btnProcessRemove.setText('remove')
         self.myDockWidget.btnConnect.setEnabled(True)
         QObject.connect(btnProcessRemove,SIGNAL("clicked()"),self.removeProcessFromWidget)         
   
    def stopProcessing( self ):
       if self.theThread != None:
         self.theThread.stop()
         self.theThread = None            
