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
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
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
        self.dlg = QgsWpsGui(self.iface.mainWindow(),  self.tools,  flags)    
        QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.createProcessGUI)    
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
         
         

    def createProcessGUI(self,name, item):
        """Create the GUI for a selected WPS process based on the DescribeProcess
           response document. Mandatory inputs are marked as red, default is black"""
        try:
          self.processIdentifier = item.text(0)
        except:
          QMessageBox.warning(None,'',QCoreApplication.translate("QgsWps",'Please select a Process'))
          return 0
    
        # Lists which store the inputs and meta information (format, occurs, ...)
        # This list is initialized every time the GUI is created
        self.complexInputComboBoxList = [] # complex input for single raster and vector maps
        self.complexInputListWidgetList = [] # complex input for multiple raster and vector maps
        self.complexInputTextBoxList = [] # complex inpt of type text/plain
        self.literalInputComboBoxList = [] # literal value list with selectable answers
        self.literalInputLineEditList = [] # literal value list with single text line input
        self.complexOutputComboBoxList = [] # list combo box
        self.inputDataTypeList = {}
        self.inputsMetaInfo = {} # dictionary for input metainfo, key is the input identifier
        self.outputsMetaInfo = {} # dictionary for output metainfo, key is the output identifier
        self.outputDataTypeList = {}
    
        self.processName = name
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        # Recive the XML process description
        self.doc.setContent(self.tools.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier), True)     
        DataInputs = self.doc.elementsByTagName("Input")
        DataOutputs = self.doc.elementsByTagName("Output")
    
        # Create the layouts and the scroll area
        self.dlgProcess = QgsWpsDescribeProcessGui(self.dlg, flags)
        self.dlgProcessLayout = QGridLayout()
        # Two tabs, one for the process inputs and one for the documentation
        # TODO: add a tab for literal outputs
        self.dlgProcessTab = QTabWidget()
        self.dlgProcessTabFrame = QFrame()
        self.dlgProcessTabFrameLayout = QGridLayout()
        # The process description can be very long, so we make it scrollable
        self.dlgProcessScrollArea = QScrollArea(self.dlgProcessTab)
    
        self.dlgProcessScrollAreaWidget = QFrame()
        self.dlgProcessScrollAreaWidgetLayout = QGridLayout()
    
        # First part of the gui is a short overview about the process
        identifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(self.doc)
        self.addIntroduction(identifier, title)
        
        # If no Input Data  are requested
        if DataInputs.size()==0:
          self.defineProcess()
          return 0
      
        # Generate the input GUI buttons and widgets
        self.tools.generateProcessInputsGUI(DataInputs)
        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.tools.generateProcessOutputsGUI(DataOutputs)
        
        self.tools.dlgProcessScrollAreaWidgetLayout.setSpacing(10)
        self.tools.dlgProcessScrollAreaWidget.setLayout(self.tools.dlgProcessScrollAreaWidgetLayout)
        self.tools.dlgProcessScrollArea.setWidget(self.tools.dlgProcessScrollAreaWidget)
        self.tools.dlgProcessScrollArea.setWidgetResizable(True)
    
        self.tools.dlgProcessTabFrameLayout.addWidget(self.tools.dlgProcessScrollArea)
    
        self.addOkCancelButtons()
    
        self.dlgProcessTabFrame.setLayout(self.dlgProcessTabFrameLayout)
        self.dlgProcessTab.addTab(self.dlgProcessTabFrame, "Process")
    
        self.addDocumentationTab(abstract)
    
        self.dlgProcessLayout.addWidget(self.dlgProcessTab)
        self.dlgProcess.setLayout(self.dlgProcessLayout)
        self.dlgProcess.setGeometry(QRect(190,100,800,600))
        self.dlgProcess.show()
        
  ##############################################################################

    def addIntroduction(self,  name, title):

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      groupbox.setTitle(name)
      layout = QVBoxLayout()

      myLabel = QLabel(groupbox)
      myLabel.setObjectName("qLabel"+name)
      myLabel.setText(QString(title))
      myLabel.setMinimumWidth(600)
      myLabel.setMinimumHeight(25)
      myLabel.setWordWrap(True)

      layout.addWidget(myLabel)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
      
  ##############################################################################
        
             
