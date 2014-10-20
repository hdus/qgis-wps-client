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
from . import version
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgswpstools import QgsWpsTools
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from wpslib.wpsserver import WpsServer
from wpslib.processdescription import ProcessDescription
from wpslib.processdescription import getFileExtension,isMimeTypeVector,isMimeTypeRaster,isMimeTypeText,isMimeTypeFile,isMimeTypePlaylist
from wpslib.processdescription import getFileExtension,isMimeTypeVector,isMimeTypeRaster,isMimeTypeText,isMimeTypeFile
from wpslib.processdescription import StringInput, TextInput, SelectionInput, VectorInput, MultipleVectorInput, RasterInput, MultipleRasterInput, FileInput, MultipleFileInput, ExtentInput, CrsInput, VectorOutput, RasterOutput, StringOutput
from wpslib.executionrequest import ExecutionRequest
from wpslib.executionrequest import createTmpGML
from wpslib.executionresult import ExecutionResult
from urlparse import urlparse

from streaming import Streaming

import resources_rc,  string
import apicompat

DEBUG = False

from Ui_QgsWpsDockWidget import Ui_QgsWpsDockWidget

class QgsWpsDockWidget(QDockWidget, Ui_QgsWpsDockWidget):
    """
    Class documentation goes here.
    """

    killed = pyqtSignal()
    bookmarksChanged = pyqtSignal()


    def __init__(self, iface):
        """
        Constructor
        """
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.tools = QgsWpsTools(self.iface)
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
        self.dlg.getDescription.connect(self.getDescription)
        self.dlg.newServer.connect(self.newServer)
        self.dlg.editServer.connect(self.editServer)
        self.dlg.deleteServer.connect(self.deleteServer)
        self.dlg.pushDefaultServer.clicked.connect(self.pushDefaultServer)
        self.dlg.requestDescribeProcess.connect(self.requestDescribeProcess)
#        self.dlg.bookmarksChanged.connect()"), self, SIGNAL("bookmarksChanged()"))

        self.killed.connect(self.stopStreaming)

    def getDescription(self, name, item):
        self.requestDescribeProcess(name, item.text(0))

    def requestDescribeProcess(self, serverName, processIdentifier):
        server = WpsServer.getServer(serverName)
        self.process = ProcessDescription(server, processIdentifier)
        self.process.describeProcessFinished.connect(self.createProcessGUI)
        self.process.requestDescribeProcess()

    def setStatus(self, status, done=0, total=0):
        complete = status == "aborted" or status == "finished" or status == "error"

        self.progressBar.setRange(done, total)
        if status == "upload" and done == total:
            status = "processing"
            done = total = 0

        self.btnConnect.setEnabled(complete)
        self.btnKill.setEnabled(not complete)
        if complete:
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(100)
        else:
            self.progressBar.setRange(0, total)
            self.progressBar.setValue(done)

        if status == 'upload':
            text = QApplication.translate("QgsWps", " upload data ...")
        elif status == 'processing':
            text = QApplication.translate("QgsWps", " is running ...")
        elif status == 'download':
            text = QApplication.translate("QgsWps", " download data ...")
        elif status == 'finished':
            text = QApplication.translate("QgsWps", " finished successfully")
        elif status == 'error':
            text = QApplication.translate("QgsWps", " terminated with errors!")
        elif status == 'aborted':
            text = QApplication.translate("QgsWps", " was aborted!")

        self.statusLabel.setText(pystring(self.processIdentifier+text))

    @pyqtSignature("")
    def on_btnConnect_clicked(self):
        self.dlg.initQgsWpsGui()
        self.statusLabel.setText("")
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.dlg.show()

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
                myExtent = pystring(self.iface.mapCanvas().extent()).replace(':',',')
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
      myLabel.setText(pystring(title))
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
        doc = QtXml.QDomDocument()
        doc.setContent(self.process.processXML)

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

              if comboBox == None or comboBox.currentText() == "<None>":
                continue

              # TODO: Check for more types (e.g. KML, Shapefile, JSON)
#              QMessageBox.information(None, '',  str(self.inputDataTypeList[comboBox.objectName()]["MimeType"]))
#              QMessageBox.information(None, '',  pystring(comboBox.objectName()))


              self.mimeType = self.inputDataTypeList[pystring(comboBox.objectName())]["MimeType"]
              schema = self.inputDataTypeList[pystring(comboBox.objectName())]["Schema"]
              encoding = self.inputDataTypeList[pystring(comboBox.objectName())]["Encoding"]
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
        dataOutputs = doc.elementsByTagName("Output")
        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
          request.addResponseFormStart()

          # Attach ALL literal outputs #############################################
          for i in range(dataOutputs.size()):
            f_element = dataOutputs.at(i).toElement()
            outputIdentifier = pystring(f_element.elementsByTagName("ows:Identifier").at(0).toElement().text()).strip()
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

            self.mimeType = self.outputDataTypeList[pystring(outputIdentifier)]["MimeType"]
            schema = self.outputDataTypeList[pystring(outputIdentifier)]["Schema"]
            encoding = self.outputDataTypeList[pystring(outputIdentifier)]["Encoding"]

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
        self.setStatus("processing")
        self.wps = ExecutionResult(self.getLiteralResult, self.getResultFile, self.successResult, self.errorResult, self.streamingHandler,  self.progressBar)
        self.wps.executeProcess(self.process.processUrl, postString)
        if len(self.process.inputs) > 0:
          self.wps.thePostReply.uploadProgress.connect(lambda done, total: self.setStatus("upload", done, total))
        self.wps.fetchingResult.connect(self.fetchingResult)

  ##############################################################################


    def addOkCancelButtons(self,  dlgProcess,  dlgProcessTabFrameLayout):

        groupBox = QFrame()
        layout = QHBoxLayout()

        btnOk = QPushButton(groupBox)
        btnOk.setText(pystring(QApplication.translate("QgsWps", "Run")))
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

        btnOk.clicked.connect(self.defineProcess)
        btnCancel.clicked.connect(self.dlgProcess.close)
        btnBookmark.clicked.connect(self.saveBookmark)

    def saveBookmark(self):
        server = WpsServer.getServer(self.dlgProcess.currentServiceName())
        process = ProcessDescription(server, self.processUrl.queryItemValue('identifier'))
        process.saveBookmark()
        self.bookmarksChanged.emit()
        QMessageBox.information(self.iface.mainWindow(),
            QCoreApplication.translate("QgsWps","Bookmark"),
            QCoreApplication.translate("QgsWps","The creation bookmark was successful."))

    def fetchingResult(self, noFilesToFetch):
        QApplication.restoreOverrideCursor()
        self.setStatus('finished')

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
                QApplication.translate("QgsWps","It seems QGIS cannot load the result of the process. The result has a '{0}' type and can be accessed at '{1}'. \n\nYou could ask the service provider to consider changing the default data type of the result.").format(self.mimeType,  resultFile))

    def getLiteralResult(self, identifier, literalText):
        self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
        self.setStatus('finished')

    def getResultFile(self, identifier, mimeType, encoding, schema, reply):
        # Get a unique temporary file name
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        ext = getFileExtension(self.mimeType)
        tmpFile = myQTempFile.fileName() + ext
        myQTempFile.close()

        # Write the data to the temporary file
        outFile = QFile(tmpFile)
        outFile.open(QIODevice.WriteOnly)
        outFile.write(reply.readAll())
        reply.deleteLater()
        outFile.close()

        resultFile = self.wps.handleEncoded(tmpFile, mimeType, encoding,  schema)

        # Finally, load the data
        self.loadData(resultFile)
        self.setStatus('finished')


##############################################################################


    def errorResult(self, exceptionHtml):
        self.setStatus('error')
        QMessageBox.critical(self.iface.mainWindow(), "Exception report", exceptionHtml)

    def successResult(self):
        self.setStatus('finished')


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
            settings.setValue(mySettings+"/scheme",  pystring(myURL.scheme))
            settings.setValue(mySettings+"/server",  pystring(myURL.netloc))
            settings.setValue(mySettings+"/path", pystring(myURL.path))
            settings.setValue(mySettings+"/method",pystring("GET"))
            settings.setValue(mySettings+"/version",pystring("1.0.0"))
            settings.setValue(mySettings+"/url",pystring(v))
            self.dlg.initQgsWpsGui()


    @pyqtSignature("")
    def on_btnKill_clicked(self):
        self.wps.thePostReply.abort()
        self.wps.thePostReply.deleteLater()
        self.setStatus('aborted')
        self.killed.emit()

