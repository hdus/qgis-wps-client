# -*- coding: utf-8 -*-
"""
 /***************************************************************************
Module implementing QgsWpsDockWidget.
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

 Authors              : Dr. Horst Duester; Luca Delucchi (Fondazione Edmund Mach)

  ***************************************************************************
  *                                                                                                             *
  *   This program is free software; you can redistribute it and/or modify     *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or          *
  *   (at your option) any later version.                                                        *
  *                                                                                                              *
  ***************************************************************************/
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtXml
from PyQt4.QtXmlPatterns import QXmlQuery
from PyQt4.QtNetwork import *
from qgis.core import *
from wps import version
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from qgswpstools import QgsWpsTools
from qgswpsgui import QgsWpsGui
from urlparse import urlparse
from functools import partial

from streaming import Streaming

import resources_rc,  string

DEBUG = False

from Ui_QgsWpsDockWidget import Ui_QgsWpsDockWidget

class QgsWpsDockWidget(QDockWidget, Ui_QgsWpsDockWidget):
    """
    Class documentation goes here. 
    """
    
    killed = pyqtSignal()
    
    def __init__(self, iface):
        """
        Constructor
        """
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.tools = QgsWpsTools(self.iface)
        self.doc = QtXml.QDomDocument()
        self.tmpPath = QDir.tempPath()        
        self.uploadFinished = False
        self.status = ''
        self.btnKill.setEnabled(False)
        self.btnConnect.setEnabled(True)
        self.dataStream = None # Used for streaming
        self.setWindowTitle('QGIS WPS-Client '+version())
        
        self.defaultServers = {'Kappasys WPS':'http://www.kappasys.ch/pywps/pywps.cgi', 
            'geodati.fmach.it':'http://geodati.fmach.it/zoo/',
            'zoo project':'http://zoo-project.org/wps-foss4g2011/zoo_loader.cgi',
            'zoo project grass':'http://zoo-project.org/cgi-grass/zoo_loader.cgi',
            '52 North':'http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService'
            }

        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.dlg = QgsWpsGui(self.iface.mainWindow(),  self.tools,  flags)            
        QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.getDescription)    
        QObject.connect(self.tools, SIGNAL("serviceRequestIsFinished(QNetworkReply)"), self.createProcessGUI)            
        QObject.connect(self.dlg, SIGNAL("newServer()"), self.newServer)    
        QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.editServer)    
        QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.deleteServer)        
        QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.cleanGui)    
        QObject.connect(self.dlg, SIGNAL("pushDefaultServer()"), self.pushDefaultServer) 
        
        self.killed.connect(self.stopStreaming)
        
    def getDescription(self,  name, item):
        self.tools.getServiceXML(name,"DescribeProcess",item.text(0)) 
        
    def getBookmarkDescription(self,  item):
        QMessageBox.information(self.iface.mainWindow(), '', item.text(0))
        self.tools.getBookmarkXML(item.text(0))            
        
    def setUpload(self,  bool):
        self.status = 'Upload'
        QMessageBox.information(self.iface.mainWindow(), '', self.status)
        
    def setDownload(self,  bool):
        self.status = 'Download'
        QMessageBox.information(self.iface.mainWindow(), '', self.status)

    def showProgressBar(self,  done,  all,  status):
      self.progressBar.setRange(0, all)
      self.progressBar.setValue(done)
      if done < all:
          self.setStatusLabel(status)
      else:
         if status=='upload':
            self.setStatusLabel('processing')
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(0)
         else:
            self.setStatusLabel('finished') 
            #print 'finished'
      
      
      return
      
    def setStatusLabel(self,  status,  myBool=None):
        groupBox = QGroupBox(self.groupBox)
        layout = QHBoxLayout()
        if status == 'upload':
            self.btnConnect.setEnabled(False)      
            self.btnKill.setEnabled(False)
            text = QApplication.translate("QgsWps", " upload data ...")
        elif status == 'processing':
            self.btnConnect.setEnabled(False)      
            self.btnKill.setEnabled(True)
            text = QApplication.translate("QgsWps", " is running ...")
        elif status == 'download':
            self.btnConnect.setEnabled(False)      
            self.btnKill.setEnabled(False)
            text = QApplication.translate("QgsWps", " download data ...")
        elif status == 'finished':
            self.btnConnect.setEnabled(True)
            self.btnKill.setEnabled(False)
            text = QApplication.translate("QgsWps", " finished successfully")
        elif status == 'error':
            self.btnConnect.setEnabled(True)      
            self.btnKill.setEnabled(False)
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)
            text = QApplication.translate("QgsWps", " terminated with errors!")
            
        try:
          self.lblProcess.setText(QString(self.processIdentifier+text))          
        except:
          self.lblProcess = QLabel(groupBox)        
          self.lblProcess.setText(QString(self.processIdentifier+text))
          layout.addWidget(self.lblProcess)        
          self.groupBox.setLayout(layout)

        return
    
    
    def cleanGui(self,  text=''):
      try:
        self.lblProcess.setText('')
      except:
        return
    
    
    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        self.dlg.initQgsWpsGui()
        self.cleanGui()
        self.dlg.show()
        
        
    
    def setProcessStarted(self):
        self.showProgressBar(1, 0, 'processing')
        pass

    def closeDialog(self):
      self.close()
         

    def createProcessGUI(self,reply):
        """Create the GUI for a selected WPS process based on the DescribeProcess
           response document. Mandatory inputs are marked as red, default is black"""
           
        self.processUrl = reply.url()
    
        # Lists which store the inputs and meta information (format, occurs, ...)
        # This list is initialized every time the GUI is created
        self.complexInputComboBoxList = [] # complex input for single raster and vector maps
        self.complexInputListWidgetList = [] # complex input for multiple raster and vector maps
        self.complexInputTextBoxList = [] # complex inpt of type text/plain
        self.literalInputComboBoxList = [] # literal value list with selectable answers
        self.literalInputLineEditList = [] # literal value list with single text line input
        self.bboxInputLineEditList = [] # bbox value list with single text line input
        self.complexOutputComboBoxList = [] # list combo box
        self.inputDataTypeList = {}
        self.inputsMetaInfo = {} # dictionary for input metainfo, key is the input identifier
        self.outputsMetaInfo = {} # dictionary for output metainfo, key is the output identifier
        self.outputDataTypeList = {}

        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        # Receive the XML process description
        self.processXML = reply.readAll().data()
        self.doc.setContent(self.processXML,  True)
        ProcessDescription = self.doc.elementsByTagName("ProcessDescription")
        self.processIdentifier = ProcessDescription.at(0).toElement().elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
        self.processName = ProcessDescription.at(0).toElement().elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()  

# Create the complex inputs at first

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
        self.identifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(self.doc)
        self.addIntroduction(self.identifier, title)
        
        # If no Input Data  are requested
        if DataInputs.size()==0:
          self.defineProcess()
          return 0
      
        # Generate the input GUI buttons and widgets
        
        res = self.generateProcessInputsGUI(DataInputs)
        if res == 0:
           return 0

        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.generateProcessOutputsGUI(DataOutputs)
        
        self.dlgProcessScrollAreaWidgetLayout.setSpacing(10)
        self.dlgProcessScrollAreaWidget.setLayout(self.dlgProcessScrollAreaWidgetLayout)
        self.dlgProcessScrollArea.setWidget(self.dlgProcessScrollAreaWidget)
        self.dlgProcessScrollArea.setWidgetResizable(True)
    
        self.dlgProcessTabFrameLayout.addWidget(self.dlgProcessScrollArea)
    
        self.addOkCancelButtons(self.dlgProcess,  self.dlgProcessTabFrameLayout)
        
        self.dlgProcessTabFrame.setLayout(self.dlgProcessTabFrameLayout)
        self.dlgProcessTab.addTab(self.dlgProcessTabFrame, "Process")
    
        self.tools.addDocumentationTab(self.dlgProcessTab,  abstract)
    
        self.dlgProcessLayout.addWidget(self.dlgProcessTab)
        self.dlgProcess.setLayout(self.dlgProcessLayout)
        self.dlgProcess.setGeometry(QRect(190,100,800,600))
        self.dlgProcess.show()
        
    def generateProcessInputsGUI(self, DataInputs):
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
            supportedComplexDataFormat = self.tools.getSupportedMimeTypes(complexDataTypeElement)
            complexDataFormat = self.tools.getDefaultMimeType(complexDataTypeElement)
    
            # Store the input formats
            self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
      
            # Attach the selected vector or raster maps
            if self.tools.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
            
              # Since it is a vector, choose an appropriate GML version
              complexDataFormat = self.getSupportedGMLDataFormat(inputIdentifier) 
              
              if complexDataFormat == None :
                QMessageBox.warning(self.iface.mainWindow(), QApplication.translate("QgsWps","Error"),  
                  QApplication.translate("QgsWps","The process '" + self.processIdentifier + \
                  "' does not seem to support GML for the parameter '" + inputIdentifier + \
                  "', which is required by the QGIS WPS client."))
                return 0 
              
              # Store the input format for this parameter (after checking GML version supported)
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Vector inputs
              layerNamesList = self.tools.getLayerNameList(0)
              if maxOccurs == 1:
                self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
              else:
                self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif self.tools.isMimeTypeText(complexDataFormat["MimeType"]) != None:
              # Text inputs
              self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif self.tools.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:

              # Store the input format for this parameter
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Raster inputs
              layerNamesList = self.tools.getLayerNameList(1)
              if maxOccurs == 1:
                self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
              else:
                self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            
            elif self.tools.isMimeTypePlaylist(complexDataFormat["MimeType"]) != None:
              # Store the input format for this parameter
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Playlist (text) inputs
              self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, str(complexDataFormat))) 
            
            else:
              # We assume text inputs in case of an unknown mime type
              self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))            
    
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
            dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
    #        print "Checking allowed values " + str(aValues.size())
            if aValues.size() > 0:
              valList = self.tools.allowedValues(aValues)
              if len(valList) > 0:
                if len(valList[0]) > 0:
                  self.literalInputComboBoxList.append(self.tools.addLiteralComboBox(title, inputIdentifier, valList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
                else:
                  self.literalInputLineEditList.append(self.tools.addLiteralLineEdit(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, str(valList)))
            else:
              self.literalInputLineEditList.append(self.tools.addLiteralLineEdit(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, dValue))
    
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
            myExtent = self.iface.mapCanvas().extent().toString().replace(':',',')
            
            self.bboxInputLineEditList.append(self.tools.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, myExtent))
    
            supportedCrsElements = bBoxElement.elementsByTagName("Supported")
    
            for i in range(supportedCrsElements.size()):
              crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))
    
#            self.literalInputComboBoxList.append(self.tools.addLiteralComboBox("Supported CRS", inputIdentifier, crsListe, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
    
    
        self.tools.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"),  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout)
        
  ##############################################################################

    def generateProcessOutputsGUI(self, DataOutputs):
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
            
            widget, comboBox = self.tools.addComplexOutputComboBox(groupbox, outputIdentifier, title, str(complexOutputFormat),  self.processIdentifier)
            self.complexOutputComboBoxList.append(comboBox)
            layout.addWidget(widget)
        
        # Set the layout
        groupbox.setLayout(layout)
        # Add the outputs
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
        

  ##############################################################################  
    def defineProcess(self):
        """Create the execute request"""
        self.dlgProcess.close()
        self.dlg.close()
        self.doc.setContent(self.processXML)
        dataInputs = self.doc.elementsByTagName("Input")
        dataOutputs = self.doc.elementsByTagName("Output")
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        scheme = self.processUrl.scheme()
        path = self.processUrl.path()
        server = self.processUrl.host()
        port = self.processUrl.port()
            
        checkBoxes = self.dlgProcess.findChildren(QCheckBox)
        if len(checkBoxes) > 0:
          useSelected = checkBoxes[0].isChecked()

        postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        postString += "<wps:Execute service=\"WPS\" version=\""+ self.tools.getServiceVersion(self.doc) + "\"" + \
                       " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                       " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                       " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                       " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                       " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                       " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"
                       
        postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
        postString += "<wps:DataInputs>"
        if dataInputs.size() > 0:
            # text/plain inputs ########################################################
            for textBox in self.complexInputTextBoxList:
              # Do not add undefined inputs
              if textBox == None or str(textBox.document().toPlainText()) == "":
                continue
        
              # TODO: Check for more types (e.g. KML, Shapefile, JSON)
              self.mimeType = self.inputDataTypeList[textBox.objectName()]["MimeType"]
              
              if self.tools.isMimeTypePlaylist(self.mimeType) != None:
                schema = self.inputDataTypeList[textBox.objectName()]["Schema"]
                encoding = self.inputDataTypeList[textBox.objectName()]["Encoding"]
  
                # Handle 'as reference' playlist
                postString += self.tools.xmlExecuteRequestInputStart(textBox.objectName(), False)
                postString += "<wps:Reference mimeType=\"" + self.mimeType + "\" " + (("schema=\"" + schema + "\"") if schema != "" else "") + (("encoding=\"" + encoding + "\"") if encoding != "" else "") + " xlink:href=\"" + textBox.document().toPlainText() + "\" />"
                postString += self.tools.xmlExecuteRequestInputEnd(False)
  
              else: # It's not a playlist
                postString += self.tools.xmlExecuteRequestInputStart(textBox.objectName())
                postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
                postString += self.tools.xmlExecuteRequestInputEnd()
        
        
            # Single raster and vector inputs ##########################################
            for comboBox in self.complexInputComboBoxList:
              # Do not add undefined inputs
              if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
                continue
                   
              postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())
        
              # TODO: Check for more types (e.g. KML, Shapefile, JSON)
              self.mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
              schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
              encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]
              self.myLayer = self.tools.getVLayer(comboBox.currentText())
                 
              try:
                  if self.tools.isMimeTypeVector(self.mimeType) != None and encoding != "base64":
                      postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + (("\" encoding=\"" + encoding + "\"") if encoding != "" else "\"") + ">"
                      postString += self.tools.createTmpGML(comboBox.currentText(), 
                        useSelected, self.getSupportedGMLVersion(comboBox.objectName())).replace("> <","><")
                        
                      postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", 
                          "xsi:schemaLocation=\"" + schema.rsplit('/',1)[0] + "/ " + schema + "\"")
                  elif self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
                      postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
                      postString += self.tools.createTmpBase64(comboBox.currentText())
              except:
                  QApplication.restoreOverrideCursor()
                  QMessageBox.warning(self.iface.mainWindow(), 
                      QApplication.translate("QgsWps","Error"),  
                      QApplication.translate("QgsWps","Please load or select a vector layer!"))
                  return
                 
              postString += "</wps:ComplexData>\n"
              postString += self.tools.xmlExecuteRequestInputEnd()  
        
            # Multiple raster and vector inputs ########################################
            for listWidgets in self.complexInputListWidgetList:
              # Do not add undefined inputs
              if listWidgets == None:
                continue
                
              self.mimeType = self.inputDataTypeList[listWidgets.objectName()]["MimeType"]
              schema = self.inputDataTypeList[listWidgets.objectName()]["Schema"]
              encoding = self.inputDataTypeList[listWidgets.objectName()]["Encoding"]
              
              # Iterate over each seletced item
              for i in range(listWidgets.count()):
                listWidget = listWidgets.item(i)
                if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
                  continue
                  
                postString += self.tools.xmlExecuteRequestInputStart(listWidgets.objectName())
        
                # TODO: Check for more types
                if self.tools.isMimeTypeVector(self.mimeType) != None and self.mimeType == "text/xml":
                  postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + (("\" encoding=\"" + encoding + "\"") if encoding != "" else "\"") + ">"
                  postString += self.tools.createTmpGML(listWidget.text(), 
                    useSelected, self.getSupportedGMLVersion(listWidgets.objectName())).replace("> <","><")
                elif self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
                  postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
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
            
           # BBOX data as lineEdit #########################################
            for bbox in self.bboxInputLineEditList:
              if bbox == None or bbox.text() == "":
                  continue
        
              bboxArray = bbox.text().split(',')
              
              postString += self.tools.xmlExecuteRequestInputStart(bbox.objectName())
              postString += '<wps:BoundingBoxData ows:dimensions="2">'
              postString += '<ows:LowerCorner>'+bboxArray[0]+' '+bboxArray[1]+'</ows:LowerCorner>'
              postString += '<ows:UpperCorner>'+bboxArray[2]+' '+bboxArray[3]+'</ows:UpperCorner>'          
              postString += "</wps:BoundingBoxData>\n"
              postString += self.tools.xmlExecuteRequestInputEnd()
            
            
        postString += "</wps:DataInputs>\n"
        
        
        # Attach only defined outputs
        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
          postString += "<wps:ResponseForm>\n"
          # The server should store the result. No lineage should be returned or status
          postString += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"false\" status=\"false\">\n"
    
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
            outputIdentifier = comboBox.objectName()
            
            self.mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
            schema = self.outputDataTypeList[outputIdentifier]["Schema"]
            encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]
            
            postString += "<wps:Output asReference=\"true" + \
              "\" mimeType=\"" + self.mimeType + "\"" + \
              ((" schema=\"" + schema + "\"") if schema != "" else "") + \
              ((" encoding=\"" + encoding + "\"") if encoding != "" else "") + ">"
            
            # Playlists can be sent as reference or as complex data 
            #   For the latter, comment out next lines
            #postString += "<wps:Output asReference=\"" + \
            #  ("false" if "playlist" in self.mimeType.lower() else "true") + \
            #  "\" mimeType=\"" + self.mimeType + \
            #  (("\" schema=\"" + schema) if schema != "" else "") + "\">"
            postString += "<ows:Identifier>" + outputIdentifier + "</ows:Identifier>\n"
            postString += "</wps:Output>\n"
    
          postString += "</wps:ResponseDocument>\n"
          postString  += "</wps:ResponseForm>\n"
          
        postString += "</wps:Execute>"


        # This is for debug purpose only
        if DEBUG == True:
#            self.tools.popUpMessageBox("Execute request", postString)
            # Write the request into a file
            outFile = open('/tmp/qwps_execute_request.xml', 'w')
            outFile.write(postString)
            outFile.close()
            
        QApplication.restoreOverrideCursor()
        self.setProcessStarted()        
        self.postData = QByteArray()
        self.postData.append(postString) 
        
        wpsConnection = scheme+'://'+server+path
            
        self.thePostHttp = QgsNetworkAccessManager.instance() 
        url = QUrl(wpsConnection)
        url.setPort(port)
        try:
            self.thePostHttp.finished.disconnect()    
        except:
            pass
            
            
        self.thePostHttp.finished.connect(self.resultHandler)                  
        self.request = QNetworkRequest(url)
        self.request.setHeader( QNetworkRequest.ContentTypeHeader, "text/xml" )        
        self.thePostReply = self.thePostHttp.post(self.request, self.postData)      
        
        if dataInputs.size() > 0:
          QObject.connect(self.thePostReply, SIGNAL("uploadProgress(qint64,qint64)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status)) 



  ##############################################################################

    def addOkCancelButtons(self,  dlgProcess,  dlgProcessTabFrameLayout):

        groupBox = QFrame()
        layout = QHBoxLayout()
    
        btnOk = QPushButton(groupBox)
        btnOk.setText(QString(QApplication.translate("QgsWps", "Run")))
        btnOk.setMinimumWidth(100)
        btnOk.setMaximumWidth(100)
    
        btnCancel = QPushButton(groupBox)
        btnCancel.setText(QApplication.translate("QgsWps", "Back"))
        btnCancel.setMinimumWidth(100)
        btnCancel.setMaximumWidth(100)
        
        btnBookmark = QPushButton(groupBox)
        btnBookmark.setText(QApplication.translate("QgsWps", "Add Bookmark"))
        btnBookmark.setMinimumWidth(200)
        btnBookmark.setMaximumWidth(200)        
    
        layout.addWidget(btnBookmark)
        layout.addStretch(10)
        layout.addWidget(btnCancel)
        layout.addWidget(btnOk)
        
        groupBox.setLayout(layout)
        dlgProcessTabFrameLayout.addWidget(groupBox)
        
        QObject.connect(btnOk,SIGNAL("clicked()"), self.defineProcess)
        QObject.connect(btnCancel,SIGNAL("clicked()"), self.dlgProcess.close)
        QObject.connect(btnBookmark,SIGNAL("clicked()"), self.saveBookmark)
        
    def saveBookmark(self):
        settings = QSettings()
        mySettings = "/WPS-Bookmarks/"+self.dlgProcess.currentServiceName()+"@@"+self.processUrl.queryItemValue('identifier')
        settings.setValue(mySettings+"/scheme", self.processUrl.scheme())
        settings.setValue(mySettings+"/server", self.processUrl.host())
        settings.setValue(mySettings+"/path",  self.processUrl.path())
        settings.setValue(mySettings+"/port",  self.processUrl.port())
        settings.setValue(mySettings+"/version", self.processUrl.queryItemValue('version'))
        settings.setValue(mySettings+"/identifier",  self.processUrl.queryItemValue('identifier'))
        QMessageBox.information(self.iface.mainWindow(), 
            QCoreApplication.translate("QgsWps","Bookmark"), 
            QCoreApplication.translate("QgsWps","The creation bookmark was successful."))
        
    def resultHandler(self, reply):
        """Handle the result of the WPS Execute request and add the outputs as new
           map layers to the registry or open an information window to show literal
           outputs."""
        resultXML = reply.readAll().data()
# This is for debug purpose only
        if DEBUG == True:
#            self.tools.popUpMessageBox("Result XML", resultXML)
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
    
                # Get the reference
                fileLink = reference.attribute("href", "0")
    
                # Try with namespace if not successful
                if fileLink == '0':
                  fileLink = reference.attributeNS("http://www.w3.org/1999/xlink", "href", "0")
                if fileLink == '0':
                  QMessageBox.warning(self.iface.mainWindow(), '', 
                      str(QApplication.translate("QgsWps", "WPS Error: Unable to download the result of reference: ")) + str(fileLink))
                  return False
    
                # Get the mime type of the result
                self.mimeType = str(reference.attribute("mimeType", "0").toLower())
    
                # Get the encoding of the result, it can be used decoding base64
                encoding = str(reference.attribute("encoding", "").toLower())
                
                if fileLink != '0':                            
                  if "playlist" in self.mimeType: # Streaming based process?
                    self.streamingHandler(encoding, fileLink)
                  else: # Conventional processes
                    self.fetchResult(encoding, fileLink)
                    QApplication.restoreOverrideCursor()
                    self.setStatusLabel('finished')
                  
              elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "ComplexData").size() > 0:
                complexData = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","ComplexData").at(0).toElement()
    
                # Get the mime type of the result
                self.mimeType = str(complexData.attribute("mimeType", "0").toLower())
                
                # Get the encoding of the result, it can be used decoding base64
                encoding = str(complexData.attribute("encoding", "").toLower())

                if "playlist" in self.mimeType:
                  playlistUrl = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "ComplexData").at(0).toElement().text()
                  self.streamingHandler(encoding, playlistUrl)

                else: # Other ComplexData are not supported by this WPS client
                  QMessageBox.warning(self.iface.mainWindow(), '', 
                    str(QApplication.translate("QgsWps", "WPS Error: The mimeType '" + mimeType + "' is not supported by this client")))
                
              elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
                QApplication.restoreOverrideCursor()
                literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
                self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
                self.setStatusLabel('finished')
                self.progressBar.setMinimum(0)
                self.progressBar.setMaximum(100)
              else:
                QMessageBox.warning(self.iface.mainWindow(), '', 
                  str(QApplication.translate("QgsWps", "WPS Error: Missing reference or literal data in response")))
        else:
            status = self.doc.elementsByTagName("Status")
            if status.size() == 0:
              self.setStatusLabel('error')
              self.progressBar.setMinimum(0)
              self.progressBar.setMaximum(100)        
#              QMessageBox.information(None, 'Result Handler', resultXML)    
              return self.errorHandler(resultXML)
        return True
        
 ##############################################################################

    def streamingHandler(self, encoding, playlistUrl):
        """ Handle response form streaming based processes """
        mimeTypePlaylist, self.mimeType = self.mimeType.split("+")
        print playlistUrl
        
        # Get number of chunks (Only for Output streaming based WPSs)
        chunks=0
        if self.tools.isMimeTypeVector(self.mimeType) != None:
            for lineEdit in self.literalInputLineEditList:
                if lineEdit.objectName() == "NumberOfChunks":
                    chunks = int(lineEdit.text())
        elif self.tools.isMimeTypeRaster(self.mimeType) != None:
            chunks=1
            for lineEdit in self.literalInputLineEditList:
                if lineEdit.objectName() == "chunksByRow" or lineEdit.objectName() == "chunksByColumn":
                    chunks = chunks*int(lineEdit.text())
        
        print "No. of chunks:",chunks
        
        # Streaming handler
        self.dataStream = Streaming(self, self.iface, chunks, playlistUrl, self.mimeType, encoding, self.tools)
        self.dataStream.start()              

    def stopStreaming(self):
        """ SLOT Stop the timer """   
        if self.dataStream: 
            self.dataStream.stop()

 ##############################################################################
 

    def loadData(self,  resultFile):
        bLoaded = True # For information purposes
        
        layerName = self.tools.uniqueLayerName(self.processIdentifier + "_" + self.identifier)
        # The layername is normally defined in the comboBox
        for comboBox in self.complexOutputComboBoxList:
            if comboBox.objectName() == self.identifier:
                layerName = comboBox.currentText()
                
        # Vector data 
        # TODO: Check for schema GML and KML
        if self.tools.isMimeTypeVector(self.mimeType) != None:
            vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
            try:
              vlayer.setCrs(self.myLayer.dataProvider().crs())
            except:
              pass
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            
       # Raster data
        elif self.tools.isMimeTypeRaster(self.mimeType) != None:
            # We can directly attach the new layer
            rLayer = QgsRasterLayer(resultFile, layerName)
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(rLayer)
            
        # Text data
        elif self.tools.isMimeTypeText(self.mimeType) != None:
            #TODO: this should be handled in a separate diaqgswps.pylog to save the text output as file'
            QApplication.restoreOverrideCursor()
            text = open(resultFile, 'r').read()
            # TODO: This should be a text dialog with safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Process result (text/plain)'),text)
            
        # Everything else
        elif self.tools.isMimeTypeFile(self.mimeType) != None:
            #TODO: this should be handled in a separate diaqgswps.pylog to save the text output as file'
            QApplication.restoreOverrideCursor()
            text = open(resultFile, 'r').read()
            # TODO: This should be a text dialog with safe option
            fileName = QFileDialog().getSaveFileName()
            
        # Everything else
        else:
            # For unsupported mime types we assume text
            QApplication.restoreOverrideCursor()
            content = open(resultFile, 'r').read()
            # TODO: This should have a safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps", 'Process result (unsupported mime type)'), content)

        if not bLoaded:
            QMessageBox.information(self.iface.mainWindow(), 
                QApplication.translate("QgsWps","Result not loaded to the map"), 
                QApplication.translate("QgsWps","It seems QGIS cannot load the result of the process. The result has a '") + self.mimeType + QApplication.translate("QgsWps","' type and can be accessed at '") + resultFile + QApplication.translate("QgsWps","'. \n\nYou could ask the service provider to consider changing the default data type of the result."))

    def fetchResult(self, encoding, fileLink):
        url = QUrl(fileLink)
        self.theHttp = QgsNetworkAccessManager.instance()
        self.theReply = self.theHttp.get(QNetworkRequest(url))
        try:
            self.theHttp.finished.disconnect()
        except:
            pass
            
        # Append encoding to 'finished' signal parameters
        self.theHttp.finished.connect(partial(self.getResultFile, encoding))  
        
        QObject.connect(self.theReply, SIGNAL("downloadProgress(qint64, qint64)"), lambda done,  all,  status="download": self.showProgressBar(done,  all,  status)) 

        
    def getResultFile(self, encoding, reply):
        # Check if there is redirection 
        reDir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        if not reDir.isEmpty():
            self.fetchResult(encoding, reDir)
            return

        # Get a unique temporary file name
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        ext = self.tools.getFileExtension(self.mimeType)
        tmpFile = unicode(myQTempFile.fileName() + ext,'latin1')
        myQTempFile.close()
        
        # Write the data to the temporary file 
        outFile = QFile(tmpFile)
        outFile.open(QIODevice.WriteOnly)
        outFile.write(reply.readAll())
        outFile.close()
        
        # Decode?
        if encoding == "base64":
            resultFile = self.tools.decodeBase64(tmpFile, self.mimeType)  
        else:   
            resultFile = tmpFile
            
        # Finally, load the data
        self.loadData(resultFile)
        self.setStatusLabel('finished')


##############################################################################


    def errorHandler(self, resultXML):    
         if resultXML:
           #print resultXML
           query = QXmlQuery(QXmlQuery.XSLT20)
           xslFile = QFile(":/plugins/wps/exception.xsl")
           xslFile.open(QIODevice.ReadOnly)
           bRead = query.setFocus(resultXML)
           query.setQuery(xslFile)
           exceptionHtml = query.evaluateToString()
           QMessageBox.critical(self.iface.mainWindow(), "Exception report", exceptionHtml)
           xslFile.close()
         return False
         

##############################################################################

    def isDataTypeSupportedByServer(self, baseMimeType, name):
      # Return if the given data type is supported by the WPS server
      for dataType in self.inputsMetaInfo[name]:
        if baseMimeType in dataType['MimeType']:
          return True
      return False

    def getDataTypeInfo(self, mimeType, name):
      # Return a dict with mimeType, schema and encoding for the given mimeType
      for dataType in self.inputsMetaInfo[name]:
        if mimeType in dataType['MimeType']:
          return dataType
      return None  
        
    def getSupportedGMLVersion(self, dataIdentifier):
      # Return GML version, e.g., GML, GML2, GML3 
      if self.tools.isGML3SupportedByOGR() and self.isDataTypeSupportedByServer(self.tools.getBaseMimeType("GML3"), dataIdentifier):
        return "GML3"
      elif self.isDataTypeSupportedByServer(self.tools.getBaseMimeType("GML2"), dataIdentifier): 
        return "GML2"
      elif self.isDataTypeSupportedByServer(self.tools.getBaseMimeType("GML"), dataIdentifier): 
        return "GML"
      else:
        return ""

    def getSupportedGMLDataFormat(self, dataIdentifier):
      # Return mimeType, schema and encoding for the supported GML version 
      supportedGML = self.getSupportedGMLVersion(dataIdentifier)
      
      if supportedGML != "":
        return self.getDataTypeInfo(self.tools.getBaseMimeType(supportedGML), dataIdentifier) 
      else:
        return None
##############################################################################

    def deleteServer(self,  name):
        settings = QSettings()
        settings.beginGroup("WPS")
        settings.remove(name)
        settings.endGroup()
        self.dlg.initQgsWpsGui() 

  ##############################################################################   
 

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

    def newServer(self):
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        dlgNew = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
        dlgNew.show()
        self.dlg.initQgsWpsGui()

    def pushDefaultServer(self):
        settings = QSettings()
        for k,v in self.defaultServers.iteritems():
            myURL = urlparse(str(v))
            mySettings = "/WPS/" + k
#    settings.setValue("WPS/connections/selected", QVariant(name) )
            settings.setValue(mySettings+"/scheme",  QVariant(myURL.scheme))
            settings.setValue(mySettings+"/server",  QVariant(myURL.netloc))
            settings.setValue(mySettings+"/path", QVariant(myURL.path))
            settings.setValue(mySettings+"/method",QVariant("GET"))
            settings.setValue(mySettings+"/version",QVariant("1.0.0"))
            self.dlg.initQgsWpsGui()
    
    
    @pyqtSignature("")
    def on_btnKill_clicked(self):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.thePostReply.abort()
        self.setStatusLabel('error')
        self.killed.emit()
        
