# -*- coding: utf-8 -*-
"""
 /***************************************************************************
Module implementing QgsWpsDockWidget.
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

 Authors              : Dr. Horst Duester, Soeren Gebbert

  ***************************************************************************
  *                                                                         *
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                         *
  ***************************************************************************/
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from PyQt4 import QtWebKit
from PyQt4 import QtNetwork
from qgis.core import *
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from qgswpstools import QgsWpsTools
from qgswpsgui import QgsWpsGui

import resources_rc

DEBUG = False

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
        self.doc = QtXml.QDomDocument()
        self.tmpPath = QDir.tempPath()        
        self.uploadFinished = False
        self.status = ''
        self.btnKill.setEnabled(False)
        self.btnConnect.setEnabled(True)

        self.theUploadHttp = QHttp( self )
        QObject.connect(self.theUploadHttp, SIGNAL("done(bool)"), self.processFinished)    
        QObject.connect(self.theUploadHttp, SIGNAL("dataSendProgress(int,int)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status)) 
        
        self.theHttp = QHttp()     
        QObject.connect(self.theHttp, SIGNAL("requestFinished(int, bool)"),  self.loadData)                
        QObject.connect(self.theHttp, SIGNAL("done(bool)"), lambda myBool,  status='finished': self.setStatusLabel(status,  myBool)) 
        QObject.connect(self.theHttp, SIGNAL("dataReadProgress(int,int)"), lambda done,  all,  status="download": self.showProgressBar(done,  all,  status)) 

        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.dlg = QgsWpsGui(self.iface.mainWindow(),  self.tools,  flags)            
        
        QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.createProcessGUI)    
        QObject.connect(self.dlg, SIGNAL("newServer()"), self.newServer)    
        QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.editServer)    
        QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.deleteServer)        
        QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.cleanGui)            
        QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.dlg.createCapabilitiesGUI)    
                
#        proxySettings = self.tools.getProxy()
#        
#        if proxySettings['proxyEnabled'] == 'true':
#            myPort = proxySettings['proxyPort'].toInt()
#            proxy = QNetworkProxy()
#            proxy.setType(QNetworkProxy.HttpProxy)
#            proxy.setHostName(proxySettings['proxyHost'])
#            proxy.setPort(myPort[1])
#            proxy.setUser(proxySettings['proxyUser'])
#            proxy.setPassword(proxySettings['proxyPassword'])
#
#            self.theHttp.setProxy(proxy)
#            self.theUploadHttp.setProxy(proxy)
            
    
    def setUpload(self,  bool):
        self.status = 'Upload'
        QMessageBox.information(None, '', self.status)
        
    def setDownload(self,  bool):
        self.status = 'Download'
        QMessageBox.information(None, '', self.status)

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
            print 'finished'
      
      
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
            text = QApplication.translate("QgsWps", " finished successful")
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
        
    def processFinished(self,  error=None):
        if error:
          QMessageBox.information(None, 'Error',  self.theUploadHttp.errorString())
          self.setStatusLabel('error')
        else:
          self.resultHandler(self.theUploadHttp.readAll().data())        
        return



    def closeDialog(self):
      self.close()
         
         

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
        self.identifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(self.doc)
        self.addIntroduction(self.identifier, title)
        
        # If no Input Data  are requested
        if DataInputs.size()==0:
          self.defineProcess()
          return 0
      
        # Generate the input GUI buttons and widgets
        self.generateProcessInputsGUI(DataInputs)
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
            complexDataFormat = self.tools.getDefaultMimeType(complexDataTypeElement)
            supportedComplexDataFormat = self.tools.getSupportedMimeTypes(complexDataTypeElement)
    
            # Store the input formats
            self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
            self.inputDataTypeList[inputIdentifier] = complexDataFormat
    
            # Attach the selected vector or raster maps
            if self.tools.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
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
              # Raster inputs
              layerNamesList = self.tools.getLayerNameList(1)
              if maxOccurs == 1:
                self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
              else:
                self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
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
            self.tools.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout)
    
            supportedCrsElements = bBoxElement.elementsByTagName("Supported")
    
            for i in range(supportedCrsElements.size()):
              crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))
    
            self.literalInputComboBoxList.append(self.tools.addLiteralComboBox("Supported CRS", inputIdentifier, crsListe, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
    
    
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
          if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
            continue
               
          postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())
    
          # TODO: Check for more types
          self.mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
          schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
          encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]
          self.myLayer = self.tools.getVLayer(comboBox.currentText())
#          QMessageBox.information(None, '', self.myLayer.dataProvider().crs().toWkt())
          
          try:
              if self.tools.isMimeTypeVector(self.mimeType) != None and self.mimeType == "text/xml":
                postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
                postString += self.tools.createTmpGML(comboBox.currentText(), useSelected).replace("> <","><")
                postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", "xsi:schemaLocation=\"http://schemas.opengis.net/gml/3.1.1/base/ gml.xsd\"")
              elif self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
                postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
                postString += self.tools.createTmpBase64(comboBox.currentText())
          except:
              QApplication.restoreOverrideCursor()
              QMessageBox.warning(None, QApplication.translate("QgsWps","Error"),  QApplication.translate("QgsWps","Please load or select a vector layer!"))
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
              postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
    #          postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <","><").replace("http://ogr.maptools.org/ qt_temp.xsd","http://ogr.maptools.org/qt_temp.xsd")
              postString += self.tools.createTmpGML(listWidget.text(), useSelected).replace("> <","><")
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
    
        postString += "</wps:DataInputs>\n"
        
        # Attach only defined outputs
        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
          postString += "<wps:ResponseForm>\n"
          # The server should store the result. No lineage should be returned or status
          postString += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"true\" status=\"false\">\n"
    
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
            
            postString += "<wps:Output asReference=\"true\" mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\">"
            postString += "<ows:Identifier>" + outputIdentifier + "</ows:Identifier>\n"
            postString += "</wps:Output>\n"
    
          postString += "</wps:ResponseDocument>\n"
          postString  += "</wps:ResponseForm>\n"
          
        postString += "</wps:Execute>\n"
    
        # This is for debug purpose only
        if DEBUG == True:
    #        self.popUpMessageBox("Execute request", postString)
            # Write the request into a file
            outFile = open('/tmp/qwps_execute_request.xml', 'w')
            outFile.write(postString)
            outFile.close()
    
        QApplication.restoreOverrideCursor()
        #QApplication .setOverrideCursor(Qt.ArrowCursor)
        
        self.postBuffer = QBuffer()
        self.postBuffer.open(QBuffer.ReadWrite)
        self.postBuffer.write(QByteArray.fromRawData(postString))
        self.postBuffer.close()
        self.setProcessStarted()        
  
        url = QUrl()
        url.setPath(path)
        self.httpRequestResult = QBuffer()
        self.theUploadHttp.setHost(server)
        result = self.theUploadHttp.post(url.toString(), self.postBuffer)
          

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
    
        layout.addStretch(10)
        layout.addWidget(btnCancel)
        layout.addWidget(btnOk)
        
        groupBox.setLayout(layout)
        dlgProcessTabFrameLayout.addWidget(groupBox)
        
        QObject.connect(btnOk,SIGNAL("clicked()"), self.defineProcess)
        QObject.connect(btnCancel,SIGNAL("clicked()"), self.dlgProcess.close)            

        
    def resultHandler(self, resultXML,  resultType="store"):
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
    
                # Get the reference
                fileLink = reference.attribute("href", "0")
    
                # Try with namespace if not successful
                if fileLink == '0':
                  fileLink = reference.attributeNS("http://www.w3.org/1999/xlink", "href", "0")
                if fileLink == '0':
                  QMessageBox.warning(None, '', str(QApplication.translate("QgsWps", "WPS Error: Unable to download the result of reference: ")) + str(fileLink))
                  return False
    
                # Get the mime type of the result
                self.mimeType = str(reference.attribute("mimeType", "0").toLower())
    
                if fileLink != '0':                            
                  # Set a valid layerName
                  self.fetchResult(fileLink)
                  
              elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
                QApplication.restoreOverrideCursor()
                literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
                self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
                self.setStatusLabel('finished')
                self.progressBar.setMinimum(0)
                self.progressBar.setMaximum(100)
              else:
                QMessageBox.warning(None, '', str(QApplication.translate("QgsWps", "WPS Error: Missing reference or literal data in response")))
        else:
            self.setStatusLabel('error')
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(100)            
            return self.errorHandler(resultXML)
        return True
        
 ##############################################################################

                  

    def loadData(self,  processId,  error):
        
        self.outFile.close()
        resultFile = self.outFile.fileName()
        
        layerName = self.tools.uniqueLayerName(self.processIdentifier + "_" + self.identifier)
        # The layername is normally defined in the comboBox
        for comboBox in self.complexOutputComboBoxList:
            if comboBox.objectName() == self.identifier:
                layerName = comboBox.currentText()
                
        # Vector data 
        # TODO: Check for schema GML and KML
        if self.tools.isMimeTypeVector(self.mimeType) != None:
            vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
#            QMessageBox.information(None, '', self.myLayer.dataProvider().crs().toWkt())
            try:
              vlayer.setCrs(self.myLayer.dataProvider().crs())
            except:
              pass
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
       # Raster data
        elif self.tools.isMimeTypeRaster(self.mimeType) != None:
       # We can directly attach the new layer
            imageFile = self.tools.decodeBase64(resultFile)
            rLayer = QgsRasterLayer(imageFile, layerName)
            QgsMapLayerRegistry.instance().addMapLayer(rLayer)
            # Text data
        elif self.tools.isMimeTypeText(self.mimeType) != None:
            #TODO: this should be handled in a separate diaqgswps.pylog to save the text output as file'
            QApplication.restoreOverrideCursor()
            text = open(resultFile, 'r').read()
            # TODO: This should be a text dialog with safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Process result (text/plain)'),text)
           # Everything else
        else:
            # For unsupported mime types we assume text
            QApplication.restoreOverrideCursor()
            content = open(resultFile, 'r').read()
            # TODO: This should have a safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps", 'Process result (unsupported mime type)'), content)

    def fetchResult(self,  fileLink):
        url = QUrl(fileLink)
        fileInfo = QFileInfo(url.path())
    #Not working under Win7
    #self.outFile = QFile(fileInfo.fileName()+".gml")
   
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        tmpFile = unicode(myQTempFile.fileName()+fileInfo.fileName()+".gml",'latin1')
        myQTempFile.close()

     #may be easier, but there is no guarantee that the Web service returns a unique value of filename (sample: "http://my_geoserver/get_result?id=12221" filename==get_result):
     #tmpFile = unicode(QDir.tempPath()+"/"+fileInfo.fileName()+".gml",'latin1')
        
        self.outFile = QFile(tmpFile)
        self.outFile.open(QIODevice.WriteOnly)
        resultFile = self.outFile.fileName()
        
        if url.scheme().toLower() == 'https':
            mode = self.theHttp.ConnectionModeHttps
        else:
            mode = self.theHttp.ConnectionModeHttp

        port = url.port()

        if port == -1:
            port = 0

        self.theHttp.setHost(url.host(), mode, port)
        self.httpRequestAborted = False

        path = QUrl.toPercentEncoding(url.path(), "!$&'()*+,;=:@/")
        if path:
            try:
                # Python v3.
                path = str(path, encoding='utf-8')
            except TypeError:
                # Python v2.
                path = str(path)
        else:
            path = '/'
            
        self.httpGetId = self.theHttp.get(url.path(),  self.outFile)
        


##############################################################################


    def errorHandler(self, resultXML):
         errorDoc = QtXml.QDomDocument()
         errorDoc = self.doc
         
         myResult = errorDoc.setContent(resultXML.strip(), True)
         resultExceptionNodeList = errorDoc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","ExceptionReport")
         exceptionText = ''
         if not resultExceptionNodeList.isEmpty():
           for i in range(resultExceptionNodeList.size()):
             resultElement = resultExceptionNodeList.at(i).toElement()
             exceptionText += resultElement.text()
    
         resultExceptionNodeList = errorDoc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","ExceptionText")
         if not resultExceptionNodeList.isEmpty():
           for i in range(resultExceptionNodeList.size()):
             resultElement = resultExceptionNodeList.at(i).toElement()
             exceptionText += resultElement.text()
      
         resultExceptionNodeList = errorDoc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","ExceptionText")
         if not resultExceptionNodeList.isEmpty():
           for i in range(resultExceptionNodeList.size()):
             resultElement = resultExceptionNodeList.at(i).toElement()
             exceptionText += resultElement.text()
    
         resultExceptionNodeList = errorDoc.elementsByTagName("Exception")
         if not resultExceptionNodeList.isEmpty():
           resultElement = resultExceptionNodeList.at(0).toElement()
           exceptionText += resultElement.attribute("exceptionCode")
    
         if len(exceptionText) > 0:
             print resultXML
             QMessageBox.about(None, '', resultXML)
    #         self.popUpMessageBox("WPS Error", resultXML)
         return False
    


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
        
        
    def getProcessResult(self,  fileLink):        
        url = QUrl(fileLink)       
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        tmpFile = QFile(myQTempFile.fileName()+".gml")
        tmpFile.open(QIODevice.WriteOnly)
               
        self.theHttp.setHost(url.host())    
        self.theHttp.get(url.path(),  tmpFile)
        resultFile = tmpFile.fileName()
        tmpFile.close()
        return resultFile
    
    @pyqtSignature("")
    def on_btnKill_clicked(self):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.theUploadHttp.abort()
        self.theHttp.abort()
