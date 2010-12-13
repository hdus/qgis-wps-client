# -*- coding: latin1 -*-
# /***************************************************************************
#   qgswps.py QGIS Web Processing Service Plugin
#  -------------------------------------------------------------------
# Date                 : 09 November 2009
# Copyright            : (C) 2009 by Dr. Horst Duester
# email                : horst dot duester at kappasys dot ch
#  ***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/
# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from PyQt4 import QtWebKit
from qgis.core import *
from qgswpstools import QgsWpsTools
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from httplib import *
from urlparse import urlparse
import os, sys, string, tempfile, urllib2, urllib,  mimetypes

# initialize Qt resources from file resources.py
import resources

DEBUG = True

# Our main class for the plugin
class QgsWps:
  MSG_BOX_TITLE = "WPS Client"
  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface  
    self.minimumRevision = 12026
    
    #Initialise the translation environment    
    userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path()+"/python/plugins/wps"  
    systemPluginPath = QgsApplication.prefixPath()+"/share/qgis/python/plugins/wps"
    myLocaleName = QSettings().value("locale/userLocale").toString()
    myLocale = myLocaleName[0:2]
    if QFileInfo(userPluginPath).exists():
      self.pluginPath = userPluginPath
      self.localePath = userPluginPath+"/i18n/wps_"+myLocale+".qm"
    elif QFileInfo(systemPluginPath).exists():
      self.pluginPath = systemPluginPath
      self.localePath = systemPluginPath+"/i18n/wps_"+myLocale+".qm"

    if QFileInfo(self.localePath).exists():
      self.translator = QTranslator()
      self.translator.load(self.localePath)
      
      if qVersion() > '4.3.3':        
        QCoreApplication.installTranslator(self.translator)  
        

  ##############################################################################

  def initGui(self):
    
    qgsRevision = QGis.QGIS_SVN_VERSION[0:5]
    
    versionMessage = unicode(QCoreApplication.translate("QgsWps","Quantum GIS revision detected: ")+str(qgsRevision)+"\n"
                    +QCoreApplication.translate("QgsWps","WPS-Client plugin requires Revision at least ")+str(self.minimumRevision)+"!\n"
                    +QCoreApplication.translate("QgsWps","Plugin not loaded."),'latin1')       
                                                                    
#    if int(qgsRevision) < int(self.minimumRevision):
#        QMessageBox.warning(None, "Version", versionMessage)
#        return 1
                                                                     
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/wps/images/wps-add.png"), "WPS Client", self.iface.mainWindow())
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)
    
    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("WPS", self.action)
    
    self.doc = QtXml.QDomDocument()
    self.tmpPath = QDir.tempPath()
    
    self.tools = QgsWpsTools(self.iface)

  ##############################################################################

  def unload(self):
    self.iface.removePluginMenu("WPS", self.action)
    self.iface.removeToolBarIcon(self.action)

  ##############################################################################

  def run(self):  
       
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
 
    self.dlg = QgsWpsGui(self.iface.mainWindow(),  flags)    
    QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.createProcessGUI)    
    QObject.connect(self.dlg, SIGNAL("newServer()"), self.newServer)    
    QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.editServer)    
    QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.deleteServer)        
    QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.createCapabilitiesGUI)    

    self.dlg.initQgsWpsGui()
    self.dlg.show()

  ##############################################################################

  def newServer(self):
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgNew = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgNew.show()
    self.dlg.initQgsWpsGui()

  ##############################################################################

  def editServer(self, name):
    info = self.tools.getServer(name)
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgEdit = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgEdit.txtName.setText(name)
    dlgEdit.txtUrl.setText(info["scheme"]+"://"+info["server"]+info["path"])
    dlgEdit.show()
    self.dlg.initQgsWpsGui()    

  ##############################################################################

  def deleteServer(self,  name):
    settings = QSettings()
    settings.beginGroup("WPS")
    settings.remove(name)
    settings.endGroup()
    self.dlg.initQgsWpsGui() 

  ##############################################################################

  def createCapabilitiesGUI(self, connection):
    if not self.tools.webConnectionExists(connection):
        return 0
        
    itemListAll = self.tools.getCapabilities(connection)
    
#    QMessageBox.information(None, '', itemListAll)
    self.dlg.initTreeWPSServices(itemListAll)

  ##############################################################################

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
    # TODO: add selectable outputs and custom name definitions
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
      self.startProcess()
      return 0
  
    # Generate the input GUI buttons and widgets
    self.generateProcessInputs(DataInputs)

    self.generateProcessOutputs(DataOutputs)
    
    self.dlgProcessScrollAreaWidgetLayout.setSpacing(10)
    self.dlgProcessScrollAreaWidget.setLayout(self.dlgProcessScrollAreaWidgetLayout)
    self.dlgProcessScrollArea.setWidget(self.dlgProcessScrollAreaWidget)
    self.dlgProcessScrollArea.setWidgetResizable(True)

    self.dlgProcessTabFrameLayout.addWidget(self.dlgProcessScrollArea)

    self.addOkCancelButtons()

    self.dlgProcessTabFrame.setLayout(self.dlgProcessTabFrameLayout)
    self.dlgProcessTab.addTab(self.dlgProcessTabFrame, "Process")

    self.addDocumentationTab(abstract)

    self.dlgProcessLayout.addWidget(self.dlgProcessTab)
    self.dlgProcess.setLayout(self.dlgProcessLayout)
    self.dlgProcess.setGeometry(QRect(190,100,800,600))
    self.dlgProcess.show()

  ##############################################################################

  def generateProcessInputs(self, DataInputs):
    """Generate the GUI for all Inputs defined in the process description XML file"""

    # Create the complex inputs at first
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)

      complexData = f_element.elementsByTagName("ComplexData")
      minOccurs = int(f_element.attribute("minOccurs"))
      maxOccurs = int(f_element.attribute("maxOccurs"))

      # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
      if complexData.size() > 0:
        # Das i-te ComplexData Objekt auswerten
        complexDataTypeElement = complexData.at(0).toElement()
        complexDataFormat = self.tools.getDefaultMimeType(complexDataTypeElement)
        supportedComplexDataFormat = self.tools.getSupportedMimeTypes(complexDataTypeElement)

        # Store the input formats
        self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
        self.inputDataTypeList[inputIdentifier] = complexDataFormat

        # Attach the selected vector or raster maps
        if complexDataFormat.toLower() == "text/xml":
          # Vector inputs
          layerNamesList = self.tools.getLayerNameList(0)
          if maxOccurs == 1:
            self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, complexDataFormat, layerNamesList, minOccurs))
          else:
            self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, complexDataFormat, layerNamesList, minOccurs))
        elif complexDataFormat.toLower() == "text/plain":
          # Text inputs
          self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))
        else:
          # Raster inputs
          layerNamesList = self.tools.getLayerNameList(1)
          if maxOccurs == 1:
            self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, complexDataFormat, layerNamesList, minOccurs))
          else:
            self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, complexDataFormat, layerNamesList, minOccurs))
            

    # Create the literal inputs as second
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)

      literalData = f_element.elementsByTagName("LiteralData")
      minOccurs = int(f_element.attribute("minOccurs"))
      maxOccurs = int(f_element.attribute("maxOccurs"))

      if literalData.size() > 0:
        allowedValuesElement = literalData.at(0).toElement()
        aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
        if aValues.size() > 0:
          valList = self.tools.allowedValues(aValues)
          if len(valList) > 0:
            if len(valList[0]) > 0:
              self.literalInputComboBoxList.append(self.addLiteralComboBox(title, inputIdentifier, valList, minOccurs))
            else:
              self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier))
        else:
          self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs))

    # At last, create the bounding box inputs
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
      
      bBoxData = f_element.elementsByTagName("BoundingBoxData")
      minOccurs = int(f_element.attribute("minOccurs"))
      maxOccurs = int(f_element.attribute("maxOccurs"))

      if bBoxData.size() > 0:
        crsListe = []
        bBoxElement = bBoxData.at(0).toElement()
        defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
        defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href")
        crsListe.append(defaultCrs)
        self.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs)

        supportedCrsElements = bBoxElement.elementsByTagName("Supported")

        for i in range(supportedCrsElements.size()):
          crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))

        self.literalInputComboBoxList.append(self.addLiteralComboBox("Supported CRS", inputIdentifier,crsListe, minOccurs))


    self.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"))
    
  ##############################################################################

  def generateProcessOutputs(self, DataOutputs):
    """Generate the GUI for all complex ouputs defined in the process description XML file"""

    if DataOutputs.size() < 1:
        return

    groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
    groupbox.setTitle("Complex output(s)")
    layout = QVBoxLayout()

    # Add all complex outputs
    for i in range(DataOutputs.size()):
      f_element = DataOutputs.at(i).toElement()

      outputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
      complexOutput = f_element.elementsByTagName("ComplexOutput")

      # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
      if complexOutput.size() > 0:
        # Das i-te ComplexData Objekt auswerten
        complexOutputTypeElement = complexOutput.at(0).toElement()
        complexOutputFormat = self.tools.getDefaultMimeType(complexOutputTypeElement)
        supportedcomplexOutputFormat = self.tools.getSupportedMimeTypes(complexOutputTypeElement)

        # Store the input formats
        self.outputsMetaInfo[outputIdentifier] = supportedcomplexOutputFormat
        self.outputDataTypeList[outputIdentifier] = complexOutputFormat
        
        widget, comboBox = self.addComplexOutputComboBox(groupbox, outputIdentifier, title, complexOutputFormat)
        self.complexOutputComboBoxList.append(comboBox)
        layout.addWidget(widget)
    
    # Set the layout
    groupbox.setLayout(layout)
    # Add the outputs
    self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
      
  ##############################################################################

  def addComplexInputComboBox(self, title, name, mimeType, namesList, minOccurs):
      """Adds a combobox to select a raster or vector map as input to the process tab"""

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()
      
      # This input is optional
      if minOccurs == 0:
        namesList.append("<None>")

      comboBox = QComboBox(groupbox)
      comboBox.addItems(namesList)
      comboBox.setObjectName(name)
      comboBox.setMinimumWidth(179)
      comboBox.setMaximumWidth(179)
      comboBox.setMinimumHeight(25)
      
      myLabel = QLabel(self.dlgProcessScrollAreaWidget)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "(" + name + ") <br>" + title + " (" + mimeType + ")"
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "(" + name + ")\n" + title + " (" + mimeType + ")"
        myLabel.setText(string)

      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(comboBox)
      
      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return comboBox              

   
  ##############################################################################

  def addComplexOutputComboBox(self, widget, name, title, mimeType):
      """Adds a combobox to select a raster or vector map as input to the process tab"""

      groupbox = QGroupBox(widget)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()
      
      namesList = []
      # Generate a unique name for the layer
      namesList.append(self.tools.uniqueLayerName(self.processIdentifier + "_" + name + "_"))
      namesList.append("<None>")

      comboBox = QComboBox(groupbox)
      comboBox.setEditable(True)
      comboBox.addItems(namesList)
      comboBox.setObjectName(name)
      comboBox.setMinimumWidth(250)
      comboBox.setMaximumWidth(250)
      comboBox.setMinimumHeight(25)
      
      myLabel = QLabel(widget)
      myLabel.setObjectName("qLabel"+name)

      string = "(" + name + ") <br>" + title + " (" + mimeType + ")"
      myLabel.setText("<font color='Green'>" + string + "</font>")

      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(comboBox)
      
      groupbox.setLayout(layout)

      return groupbox, comboBox              

  ##############################################################################

  def addComplexInputListWidget(self, title, name, mimeType, namesList, minOccurs):
      """Adds a widget for multiple raster or vector selections as inputs  to the process tab"""
      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      # This input is optional
      if minOccurs == 0:
        namesList.append("<None>")

      listWidget = QListWidget(groupbox)
      listWidget.addItems(namesList)
      listWidget.setObjectName(name)
      listWidget.setMinimumWidth(179)
      listWidget.setMaximumWidth(179)
      listWidget.setMinimumHeight(120)
      listWidget.setMaximumHeight(120)
      listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

      myLabel = QLabel(self.dlgProcessScrollAreaWidget)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "(" + name + ") <br>" + title + " (" + mimeType + ")"
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "(" + name + ")\n" + title + " (" + mimeType + ")"
        myLabel.setText(string)

      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(listWidget)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return listWidget

  ##############################################################################

  def addComplexInputTextBox(self, title, name, minOccurs):
      """Adds a widget to insert text as complex inputs to the process tab"""
      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(50)
      layout = QHBoxLayout()

      textBox = QTextEdit(groupbox)
      textBox.setObjectName(name)
      textBox.setMinimumWidth(200)
      textBox.setMaximumWidth(200)
      textBox.setMinimumHeight(50)

      myLabel = QLabel(self.dlgProcessScrollAreaWidget)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "(" + name + ") <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "(" + name + ")\n" + title
        myLabel.setText(string)

      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(textBox)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return textBox

  ##############################################################################

  def addLiteralComboBox(self, title, name, namesList, minOccurs):

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      comboBox = QComboBox(self.dlgProcessScrollAreaWidget)
      comboBox.addItems(namesList)
      comboBox.setObjectName(name)
      comboBox.setMinimumWidth(179)
      comboBox.setMaximumWidth(179)
      comboBox.setMinimumHeight(25)

      myLabel = QLabel(self.dlgProcessScrollAreaWidget)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "(" + name + ") <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "(" + name + ")\n" + title
        myLabel.setText(string)
        
      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(comboBox)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return comboBox

  ##############################################################################

  def addLiteralLineEdit(self, title, name, minOccurs):

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      myLineEdit = QLineEdit(groupbox)
      myLineEdit.setObjectName(name)
      myLineEdit.setMinimumWidth(179)
      myLineEdit.setMaximumWidth(179)
      myLineEdit.setMinimumHeight(25)
      
      myLabel = QLabel(groupbox)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "(" + name + ") <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "(" + name + ")\n" + title
        myLabel.setText(string)
        
      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(myLineEdit)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return myLineEdit

  ##############################################################################

  def addCheckBox(self,  title,  name):

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      myCheckBox = QCheckBox(groupbox)
      myCheckBox.setObjectName("chkBox"+name)
      myCheckBox.setChecked(False)
      
      myLabel = QLabel(groupbox)
      myLabel.setObjectName("qLabel"+name)  
      myLabel.setText("(" + name + ")" + "\n" + title)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)
      myLabel.setWordWrap(True)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(myCheckBox)

      groupbox.setLayout(layout)

      self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

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

  def addDocumentationTab(self, abstract):
    # Check for URL
    if str(abstract).find("http://") == 0:
      textBox = QtWebKit.QWebView(self.dlgProcessTab)
      textBox.load(QUrl(abstract))
      textBox.show()
    else:
      textBox = QTextBrowser(self.dlgProcessTab)
      textBox.setText(QString(abstract))

    self.dlgProcessTab.addTab(textBox, "Documentation")

  ##############################################################################

  def addOkCancelButtons(self):

    groupbox = QFrame()
    layout = QHBoxLayout()

    btnOk = QPushButton(groupbox)
    btnOk.setText(QString("Run"))
    btnOk.setMinimumWidth(100)
    btnOk.setMaximumWidth(100)

    btnCancel = QPushButton(groupbox)
    btnCancel.setText("Back")
    btnCancel.setMinimumWidth(100)
    btnCancel.setMaximumWidth(100)

    layout.addWidget(btnOk)
    layout.addStretch(1)
    layout.addWidget(btnCancel)

    groupbox.setLayout(layout)
    self.dlgProcessTabFrameLayout.addWidget(groupbox)

    QObject.connect(btnOk,SIGNAL("clicked()"),self.startProcess)
    QObject.connect(btnCancel,SIGNAL("clicked()"),self.dlgProcess.close)

  ##############################################################################

  def startProcess(self):
    """Create the execute request"""
    self.doc.setContent(self.tools.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier))
    dataInputs = self.doc.elementsByTagName("Input")
    dataOutputs = self.doc.elementsByTagName("Output")

    QApplication.setOverrideCursor(Qt.WaitCursor)
    result = self.tools.getServer(self.processName)
    scheme = result["scheme"]
    path = result["path"]
    server = result["server"]

    checkBoxes = self.dlgProcess.findChildren(QCheckBox)

    if len(checkBoxes) > 0:
      useSelected = checkBoxes[0].isChecked()

    postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
    postString += "<wps:Execute service=\"WPS\" version=\""+ self.tools.getServiceVersion() + "\"" + \
                   " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                   " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                   " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                   " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                   " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                   " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"
                   
    postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
    postString += "<wps:DataInputs>"

    # text/plain inputs ########################################################
    for textBox in self.complexInputTextBoxList:
      # Do not add undefined inputs
      if textBox == None or str(textBox.document().toPlainText()) == "":
        continue

      postString += self.tools.xmlExecuteRequestInputStart(textBox.objectName())
      postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
      postString += self.tools.xmlExecuteRequestInputEnd()


    # Single raster and vector inputs ##########################################
    for comboBox in self.complexInputComboBoxList:
      # Do not add undefined inputs
      if comboBox == None or str(comboBox.currentText()) == "<None>":
        continue
           
      postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())

      # TODO: Check for more types
      if self.inputDataTypeList[comboBox.objectName()] == "text/xml":
        postString += "<wps:ComplexData>"
        postString += self.tools.createTmpGML(comboBox.currentText(), useSelected).replace("> <","><")
      else:
        postString += "<wps:ComplexData encoding=\"base64\">\n"
        postString += self.tools.createTmpBase64(comboBox.currentText())

      postString += "</wps:ComplexData>\n"
      postString += self.tools.xmlExecuteRequestInputEnd()

    # Multiple raster and vector inputs ########################################
    for listWidgets in self.complexInputListWidgetList:
      # Do not add undefined inputs
      if listWidgets == None:
        continue

      # Iterate over each seletced item
      for i in range(listWidgets.count()):
        listWidget = listWidgets.item(i)
        if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
          continue
          
        postString += self.tools.xmlExecuteRequestInputStart(listWidgets.objectName())

        # TODO: Check for more types
        if self.inputDataTypeList[listWidgets.objectName()] == "text/xml":
          postString += "<wps:ComplexData>"
          postString += self.tools.createTmpGML(listWidget.text(), useSelected).replace("> <","><").replace("http://ogr.maptools.org/ qt_temp.xsd","http://ogr.maptools.org/qt_temp.xsd")
        else:
          postString += "<wps:ComplexData encoding=\"base64\">\n"
          postString += self.tools.createTmpBase64(listWidget.text())

        postString += "</wps:ComplexData>\n"
        postString += self.tools.xmlExecuteRequestInputEnd()

    # Literal data as combo box choice #########################################
    for comboBox in self.literalInputComboBoxList:
      if comboBox == None or comboBox.currentText() == "":
          continue

      postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())
      postString += "<wps:LiteralData>"+comboBox.currentText()+"</wps:LiteralData>\n"
      postString += self.tools.xmlExecuteRequestInputEnd()

   # Literal data as combo box choice #########################################
    for lineEdit in self.literalInputLineEditList:
      if lineEdit == None or lineEdit.text() == "":
          continue

      postString += self.tools.xmlExecuteRequestInputStart(lineEdit.objectName())
      postString += "<wps:LiteralData>"+lineEdit.text()+"</wps:LiteralData>\n"
      postString += self.tools.xmlExecuteRequestInputEnd()

    postString += "</wps:DataInputs>\n"
    
    # Attach only defined outputs
    if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
      postString += "<wps:ResponseForm>\n"
      # The server should store the result. No lineage should be returned or status
      postString += "<wps:ResponseDocument lineage=\"true\" storeExecuteResponse=\"true\" status=\"false\">\n"

      # Attach ALL literal outputs #############################################
      for i in range(dataOutputs.size()):
        f_element = dataOutputs.at(i).toElement()
        outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
        literalOutputType = f_element.elementsByTagName("LiteralOutput")

        # Complex data is always requested as reference
        if literalOutputType.size() != 0:
          postString += "<wps:Output>\n"
          postString += "<ows:Identifier>"+outputIdentifier+"</ows:Identifier>\n"
          postString += "</wps:Output>\n"

      # Attach selected complex outputs ########################################
      for comboBox in self.complexOutputComboBoxList:
        # Do not add undefined outputs
        if comboBox == None or str(comboBox.currentText()) == "<None>":
          continue
        postString += "<wps:Output asReference=\"true\">\n"
        postString += "<ows:Identifier>"+comboBox.objectName()+"</ows:Identifier>\n"
        postString += "</wps:Output>\n"

      postString += "</wps:ResponseDocument>\n"
      postString  += "</wps:ResponseForm>\n"
      
    postString += "</wps:Execute>\n"

    # This is for debug purpose only
    if DEBUG == True:
        self.tools.popUpMessageBox("Execute request", postString)
        # Write the request into a file
        outFile = open('/tmp/qwps_execute_request.xml', 'w')
        outFile.write(postString)
        outFile.close()

    f = urllib.urlopen( str(scheme)+"://"+str(server)+""+str(path), unicode(postString, "latin1").replace('<wps:ComplexData>\n','<wps:ComplexData>'))

    # Read the results back.
    wpsRequestResult = f.read()
    QApplication.restoreOverrideCursor()
    QApplication .setOverrideCursor(Qt.ArrowCursor)
    self.resultHandler(wpsRequestResult)

  ##############################################################################

  def resultHandler(self, resultXML, resultType="store"):
    """Handle the result of the WPS Execute request and add the outputs as new
       map layers to the regestry or open an information window to show literal
       outputs."""

    # This is for debug purpose only
    if DEBUG == True:
        self.tools.popUpMessageBox("Result XML", resultXML)
        # Write the response into a file
        outFile = open('/tmp/qwps_execute_response.xml', 'w')
        outFile.write(resultXML)
        outFile.close()
        
    self.doc.setContent(resultXML,  True)
    resultNodeList = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Output")
    
    # TODO: Check if the process does not run correctly before
    if resultNodeList.size() > 0:
        for i in range(resultNodeList.size()):
          f_element = resultNodeList.at(i).toElement()

          # Fetch the referenced complex data
          if f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "Reference").size() > 0:
            identifier = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
            reference = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Reference").at(0).toElement()

            fileLink = reference.attributeNS("http://www.w3.org/1999/xlink", "href", "0")
            mimeType = reference.attribute("mimeType", "0").toLower()

            if fileLink <> '0':                            
              # Set a valid layerName
              layerName = self.tools.uniqueLayerName(self.processIdentifier + "_" + identifier)
              # The layername is normally defined in the comboBox
              for comboBox in self.complexOutputComboBoxList:
                if comboBox.objectName() == identifier:
                  layerName = comboBox.currentText()

              resultFileConnector = urllib.urlretrieve(unicode(fileLink,'latin1'))
              resultFile = resultFileConnector[0]
              if mimeType == 'text/xml': # We assume GML output
                vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
              elif mimeType == 'text/plain':
                #TODO: this should be handled in a separate dialog to save the text output as file'
                QApplication.restoreOverrideCursor()
                text = open(resultFile, 'r').read()
                # TODO: This should be a text dialog with safe option
                self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Process result'),text)
              else:
                # We can directly attach the new layer, it should be a raster tif
                rLayer = QgsRasterLayer(resultFile, layerName)
                QgsMapLayerRegistry.instance().addMapLayer(rLayer)
          elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
            QApplication.restoreOverrideCursor()
            literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
        QMessageBox.information(None, QCoreApplication.translate("QgsWps",'Process result'), QCoreApplication.translate("QgsWps",'The process finished successful'))
    else:
        self.tools.errorHandler(resultXML)
        
