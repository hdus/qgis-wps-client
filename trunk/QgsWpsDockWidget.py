# -*- coding: utf-8 -*-
"""
 /***************************************************************************
   QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

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
from PyQt4 import QtXml
from PyQt4.QtNetwork import *
from qgis.core import *
from wps import version
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgswpstools import QgsWpsTools
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from wpslib.wpsserver import WpsServer
from wpslib.processdescription import ProcessDescription
from wpslib.processdescription import getFileExtension,isMimeTypeVector,isMimeTypeRaster,isMimeTypeText,isMimeTypeFile,isMimeTypePlaylist
from wpslib.processdescription import getFileExtension,isMimeTypeVector,isMimeTypeRaster,isMimeTypeText,isMimeTypeFile
from wps.wpslib.processdescription import StringInput, TextInput, SelectionInput, VectorInput, MultipleVectorInput, RasterInput, MultipleRasterInput, FileInput, MultipleFileInput, ExtentInput, CrsInput, VectorOutput, RasterOutput, StringOutput
from wpslib.executionrequest import ExecutionRequest
from wpslib.executionrequest import createTmpGML
from wpslib.executionresult import ExecutionResult
from urlparse import urlparse

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
        self.dlg = QgsWpsGui(self.iface.mainWindow(), flags)
        QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.getDescription)    
        QObject.connect(self.dlg, SIGNAL("newServer()"), self.newServer)    
        QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.editServer)    
        QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.deleteServer)        
        QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.cleanGui)    
        QObject.connect(self.dlg, SIGNAL("pushDefaultServer()"), self.pushDefaultServer) 
        QObject.connect(self.dlg, SIGNAL("requestDescribeProcess(QString, QString)"), self.requestDescribeProcess)
        QObject.connect(self.dlg, SIGNAL("bookmarksChanged()"), self, SIGNAL("bookmarksChanged()"))    

        self.killed.connect(self.stopStreaming)
        
    def getDescription(self, name, item):
        self.requestDescribeProcess(name, item.text(0))

    def requestDescribeProcess(self, serverName, processIdentifier):
        server = WpsServer.getServer(serverName)
        self.process = ProcessDescription(server, processIdentifier)
        QObject.connect(self.process, SIGNAL("describeProcessFinished"), self.createProcessGUI)
        self.process.requestDescribeProcess()
        
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
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(100)
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
         

    def createProcessGUI(self):
        """Create the GUI for a selected WPS process based on the DescribeProcess
           response document. Mandatory inputs are marked as red, default is black"""
           
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
        self.outputDataTypeList = {}

        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags

        self.processUrl = self.process.processUrl
        self.processIdentifier = self.process.processIdentifier
        self.processName = self.process.processName

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
        self.identifier = self.process.identifier
        title = self.process.title
        abstract = self.process.abstract
        self.addIntroduction(self.identifier, title)
        
        # If no Input Data  are requested
        if len(self.process.inputs)==0:
          self.defineProcess()
          return 0
      
        # Generate the input GUI buttons and widgets
        
        res = self.generateProcessInputsGUI()
        if res == 0:
           return 0

        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.generateProcessOutputsGUI()
        
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
        
    def generateProcessInputsGUI(self):
        """Generate the GUI for all Inputs defined in the process description XML file"""
        for input in self.process.inputs:
            inputType = type(input)
            inputIdentifier = input.identifier
            title = input.title
            minOccurs = input.minOccurs
            if inputType == VectorInput or inputType == MultipleVectorInput:
                complexDataFormat = input.dataFormat
                self.inputDataTypeList[inputIdentifier] = complexDataFormat
                layerNamesList = self.tools.getLayerNameList(0)
                if inputType == VectorInput:
                    self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
                else:
                    self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))              
            elif inputType == StringInput:
                dValue =  input.defaultValue
                self.literalInputLineEditList.append(self.tools.addLiteralLineEdit(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, dValue))
            elif inputType == TextInput:
                complexDataFormat = input.dataFormat
                if isMimeTypePlaylist(complexDataFormat["MimeType"]) != None:
                    self.inputDataTypeList[inputIdentifier] = complexDataFormat
                    # Playlist (text) inputs
                    self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, str(complexDataFormat))) 
                else:
                    self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif inputType == RasterInput or inputType == MultipleRasterInput:
                complexDataFormat = input.dataFormat
                self.inputDataTypeList[inputIdentifier] = complexDataFormat
                layerNamesList = self.tools.getLayerNameList(1)
                if inputType == RasterInput:
                    self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
                else:
                    self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif inputType == SelectionInput:
                valList = input.valList
                self.literalInputComboBoxList.append(self.tools.addLiteralComboBox(title, inputIdentifier, valList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif inputType == ExtentInput:
                myExtent = self.iface.mapCanvas().extent().toString().replace(':',',')                
                self.bboxInputLineEditList.append(self.tools.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, myExtent))
            elif inputType == CrsInput:
                crsListe = input.crsList
#                self.literalInputComboBoxList.append(self.tools.addLiteralComboBox("Supported CRS", inputIdentifier, crsListe, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
    
        self.tools.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"),  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout)
        
  ##############################################################################

    def generateProcessOutputsGUI(self):
        """Generate the GUI for all complex ouputs defined in the process description XML file"""
    
        if len(self.process.outputs) < 1:
            return
    
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        groupbox.setTitle("Complex output(s)")
        layout = QVBoxLayout()
    
        for output in self.process.outputs:
            outputType = type(output)
            outputIdentifier = output.identifier
            title = output.title
            if outputType == VectorOutput or outputType == RasterOutput:
                complexOutputFormat = output.dataFormat
                # Store the input formats
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
        self.doc.setContent(self.process.processXML)
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
            
        checkBoxes = self.dlgProcess.findChildren(QCheckBox)
        if len(checkBoxes) > 0:
          useSelected = checkBoxes[0].isChecked()

        request = ExecutionRequest(self.process)
        request.addExecuteRequestHeader()

        request.addDataInputsStart()
        if len(self.process.inputs) > 0:
            # text/plain inputs ########################################################
            for textBox in self.complexInputTextBoxList:
              # Do not add undefined inputs
              if textBox == None or str(textBox.document().toPlainText()) == "":
                continue
        
              # TODO: Check for more types (e.g. KML, Shapefile, JSON)
              self.mimeType = self.inputDataTypeList[textBox.objectName()]["MimeType"]
              
              if isMimeTypePlaylist(self.mimeType) != None:
                schema = self.inputDataTypeList[textBox.objectName()]["Schema"]
                encoding = self.inputDataTypeList[textBox.objectName()]["Encoding"]
  
                # Handle 'as reference' playlist
                request.addReferenceInput(textBox.objectName(), self.mimeType, schema, encoding, textBox.document().toPlainText())
  
              else: # It's not a playlist
                request.addPlainTextInput(textBox.objectName(), textBox.document().toPlainText())
        
        
            # Single raster and vector inputs ##########################################
            for comboBox in self.complexInputComboBoxList:
              # Do not add undefined inputs
              if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
                continue
                   
              # TODO: Check for more types (e.g. KML, Shapefile, JSON)
              self.mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
              schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
              encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]
              self.myLayer = self.tools.getVLayer(comboBox.currentText())
                 
#              try:
              if isMimeTypeVector(self.mimeType) != None and encoding != "base64":
                  gmldata = createTmpGML(self.tools.getVLayer(comboBox.currentText()), 
                                                    useSelected, self.process.getSupportedGMLVersion(comboBox.objectName()))
                  request.addGeometryInput(comboBox.objectName(), self.mimeType, schema, encoding, gmldata, useSelected)
              elif isMimeTypeVector(self.mimeType) != None or isMimeTypeRaster(self.mimeType) != None:
                  request.addGeometryBase64Input(comboBox.objectName(), self.mimeType, self.tools.getVLayer(comboBox.currentText()))
#              except:
#                  QApplication.restoreOverrideCursor()
#                  QMessageBox.warning(self.iface.mainWindow(), 
#                      QApplication.translate("QgsWps","Error"),  
#                      QApplication.translate("QgsWps","Please load or select a vector layer!"))
#                  return
        
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

                # TODO: Check for more types
                if isMimeTypeVector(self.mimeType) != None and self.mimeType == "text/xml":
                  gmldata = createTmpGML(self.tools.getVLayer(listWidget.text()), 
                    useSelected, self.process.getSupportedGMLVersion(listWidgets.objectName()))
                  request.addMultipleGeometryInput(listWidgets.objectName(), self.mimeType, schema, encoding, gmldata, useSelected)
                elif isMimeTypeVector(self.mimeType) != None or isMimeTypeRaster(self.mimeType) != None:
                  addMultipleGeometryBase64Input(listWidgets.objectName(), self.mimeType, self.tools.getVLayer(listWidget.text()))


            # Literal data as combo box choice #########################################
            for comboBox in self.literalInputComboBoxList:
              if comboBox == None or comboBox.currentText() == "":
                  continue

              request.addLiteralDataInput(comboBox.objectName(), comboBox.currentText())

           # Literal data as combo box choice #########################################
            for lineEdit in self.literalInputLineEditList:
              if lineEdit == None or lineEdit.text() == "":
                  continue

              request.addLiteralDataInput(lineEdit.objectName(), lineEdit.text())

           # BBOX data as lineEdit #########################################
            for bbox in self.bboxInputLineEditList:
              if bbox == None or bbox.text() == "":
                  continue
        
              bboxArray = bbox.text().split(',')
              
              request.addBoundingBoxInput(bbox.objectName(), bboxArray)


        request.addDataInputsEnd()


        # Attach only defined outputs
        dataOutputs = self.doc.elementsByTagName("Output")
        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
          request.addResponseFormStart()
    
          # Attach ALL literal outputs #############################################
          for i in range(dataOutputs.size()):
            f_element = dataOutputs.at(i).toElement()
            outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
            literalOutputType = f_element.elementsByTagName("LiteralOutput")
    
            # Complex data is always requested as reference
            if literalOutputType.size() != 0:
              request.addLiteralDataOutput(outputIdentifier)
    
          # Attach selected complex outputs ########################################
          for comboBox in self.complexOutputComboBoxList:
            # Do not add undefined outputs
            if comboBox == None or str(comboBox.currentText()) == "<None>":
              continue
            outputIdentifier = comboBox.objectName()
            
            self.mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
            schema = self.outputDataTypeList[outputIdentifier]["Schema"]
            encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]
            
            request.addReferenceOutput(outputIdentifier, self.mimeType, schema, encoding)

          request.addResponseFormEnd()

        request.addExecuteRequestEnd()
        postString = request.request

        # This is for debug purpose only
        if DEBUG == True:
#            self.tools.popUpMessageBox("Execute request", postString)
            # Write the request into a file
            outFile = open('/tmp/qwps_execute_request.xml', 'w')
            outFile.write(postString)
            outFile.close()
            
        QApplication.restoreOverrideCursor()
        self.setProcessStarted()
        self.wps = ExecutionResult(self.getLiteralResult, self.getResultFile, self.errorResult, self.streamingHandler)
        self.wps.executeProcess(self.process.processUrl, postString)
        if len(self.process.inputs) > 0:
          QObject.connect(self.wps.thePostReply, SIGNAL("uploadProgress(qint64,qint64)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status))
        QObject.connect(self.wps, SIGNAL("fetchingResult(int)"), self.fetchingResult)

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
        server = WpsServer.getServer(self.dlgProcess.currentServiceName())
        process = ProcessDescription(server, self.processUrl.queryItemValue('identifier'))
        process.saveBookmark()
        self.emit(SIGNAL("bookmarksChanged()"))
        QMessageBox.information(self.iface.mainWindow(), 
            QCoreApplication.translate("QgsWps","Bookmark"), 
            QCoreApplication.translate("QgsWps","The creation bookmark was successful."))
        
    def fetchingResult(self, noFilesToFetch):
        QApplication.restoreOverrideCursor()
        self.setStatusLabel('finished')

 ##############################################################################

    def streamingHandler(self, encoding, playlistUrl):
        """ Handle response form streaming based processes """
        mimeTypePlaylist, self.mimeType = self.mimeType.split("+")
        print playlistUrl
        
        # Get number of chunks (Only for Output streaming based WPSs)
        chunks=0
        if isMimeTypeVector(self.mimeType) != None:
            for lineEdit in self.literalInputLineEditList:
                if lineEdit.objectName() == "NumberOfChunks":
                    chunks = int(lineEdit.text())
        elif isMimeTypeRaster(self.mimeType) != None:
            chunks=1
            for lineEdit in self.literalInputLineEditList:
                if lineEdit.objectName() == "chunksByRow" or lineEdit.objectName() == "chunksByColumn":
                    chunks = chunks*int(lineEdit.text())
        
        print "No. of chunks:",chunks
        
        # Streaming handler
        self.dataStream = Streaming(self, self.iface, chunks, playlistUrl, self.mimeType, encoding)
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
        if isMimeTypeVector(self.mimeType) != None:
            vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
            try:
              vlayer.setCrs(self.myLayer.dataProvider().crs())
            except:
              pass
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            
       # Raster data
        elif isMimeTypeRaster(self.mimeType) != None:
            # We can directly attach the new layer
            rLayer = QgsRasterLayer(resultFile, layerName)
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(rLayer)
            
        # Text data
        elif isMimeTypeText(self.mimeType) != None:
            #TODO: this should be handled in a separate diaqgswps.pylog to save the text output as file'
            QApplication.restoreOverrideCursor()
            text = open(resultFile, 'r').read()
            # TODO: This should be a text dialog with safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Process result (text/plain)'),text)
            
        # Everything else
        elif isMimeTypeFile(self.mimeType) != None:
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
                QApplication.translate("QgsWps","It seems QGIS cannot load the result of the process. The result has a '%1' type and can be accessed at '%2'. \n\nYou could ask the service provider to consider changing the default data type of the result.").arg(self.mimeType ).arg(resultFile))

    def getLiteralResult(self, identifier, literalText):
        self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
        self.setStatusLabel('finished')
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

    def getResultFile(self, identifier, mimeType, encoding, schema, reply):
        # Get a unique temporary file name
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        ext = getFileExtension(self.mimeType)
        tmpFile = unicode(myQTempFile.fileName() + ext,'latin1')
        myQTempFile.close()
        
        # Write the data to the temporary file 
        outFile = QFile(tmpFile)
        outFile.open(QIODevice.WriteOnly)
        outFile.write(reply.readAll())
        outFile.close()
        
        resultFile = self.wps.handleEncoded(tmpFile, mimeType, encoding,  schema)
            
        # Finally, load the data
        self.loadData(resultFile)
        self.setStatusLabel('finished')


##############################################################################


    def errorResult(self, exceptionHtml):
        self.setStatusLabel('error')
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        QMessageBox.critical(self.iface.mainWindow(), "Exception report", exceptionHtml)


  ##############################################################################

    def deleteServer(self,  name):
        settings = QSettings()
        settings.beginGroup("WPS")
        settings.remove(name)
        settings.endGroup()
        self.dlg.initQgsWpsGui() 


  ##############################################################################

    def editServer(self, name):
        server = WpsServer.getServer(name)
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        dlgEdit = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
        dlgEdit.txtName.setText(name)
        dlgEdit.txtUrl.setText(server.baseUrl)
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
            settings.setValue(mySettings+"/url",QVariant(v))
            self.dlg.initQgsWpsGui()
    
    
    @pyqtSignature("")
    def on_btnKill_clicked(self):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.wps.thePostReply.abort()
        self.setStatusLabel('error')
        self.killed.emit()
        
