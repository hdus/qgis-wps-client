from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.Sextante import Sextante
from sextante.core.QGisLayers import QGisLayers
from sextante.parameters.ParameterBoolean import ParameterBoolean
from sextante.parameters.ParameterCrs import ParameterCrs
from sextante.parameters.ParameterExtent import ParameterExtent
from sextante.parameters.ParameterFactory import ParameterFactory
from sextante.parameters.ParameterMultipleInput import ParameterMultipleInput
from sextante.parameters.ParameterNumber import ParameterNumber
from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterSelection import ParameterSelection
from sextante.parameters.ParameterString import ParameterString
from sextante.parameters.ParameterTable import ParameterTable
from sextante.parameters.ParameterVector import ParameterVector
from sextante.outputs.OutputRaster import OutputRaster
from sextante.outputs.OutputVector import OutputVector
from sextante.outputs.OutputFactory import OutputFactory
from wps.qgswpstools import QgsWpsTools
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtXml


class BookmarksAlgorithm(GeoAlgorithm):

    def __init__(self, config):
        self.config = config
        self.processName = str(self.config['service'])
        self.processIdentifier = str(self.config['identifier'])
        self.tools = QgsWpsTools()
        GeoAlgorithm.__init__(self) #calls defineCharacteristics

    def defineCharacteristics(self):
        self.name = self.processIdentifier
        self.group = "Bookmarks"
        #Lazy loading of process description
        self.processXML = None
        #Parameters are added after loading process description

    def checkBeforeOpeningParametersDialog(self):
        if self.processXML == None:
            self.getServiceXML()
            self.buildParametersDialog()
        return None

    def getServiceXML(self):
        QObject.connect(self.tools, SIGNAL("serviceRequestIsFinished(QNetworkReply)"), self.describeProcessFinished)
        #Start http request. Emits serviceRequestIsFinished(QNetworkReply)
        self.tools.getServiceXML(self.processName, "DescribeProcess", self.processIdentifier)
        #Wait for answer
        while self.processXML == None:
             qApp.processEvents()
        qDebug(self.processXML)

    @pyqtSlot()
    def describeProcessFinished(self,reply):
        QObject.disconnect(self.tools, SIGNAL("serviceRequestIsFinished(QNetworkReply)"), self.describeProcessFinished)
        self.processUrl = reply.url()
        self.processXML = reply.readAll().data()

    def buildParametersDialog(self):
        self.inputDataTypeList = {}
        self.inputsMetaInfo = {} # dictionary for input metainfo, key is the input identifier
        self.outputsMetaInfo = {} # dictionary for output metainfo, key is the output identifier
        self.outputDataTypeList = {}

        # Receive the XML process description
        self.doc = QtXml.QDomDocument()
        self.doc.setContent(self.processXML,  True)
        processDescription = self.doc.elementsByTagName("processDescription")
        #self.processIdentifier = processDescription.at(0).toElement().elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
        #self.processName = processDescription.at(0).toElement().elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()  

        # Create the complex inputs at first

        dataInputs = self.doc.elementsByTagName("Input")
        dataOutputs = self.doc.elementsByTagName("Output")
    
        # First part of the gui is a short overview about the process
        self.identifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(self.doc)
        #self.addIntroduction(self.identifier, title)
        
        # If no Input Data  are requested
        #if dataInputs.size()==0:
        #  self.defineProcess()
        #  return 0
      
        # Generate the input GUI buttons and widgets
        
        res = self.generateProcessInputsGUI(dataInputs)
        if res == 0:
           return 0

        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.generateProcessOutputsGUI(dataOutputs)
    
        #self.tools.addDocumentationTab(self.dlgProcessTab,  abstract)
        
    def generateProcessInputsGUI(self, dataInputs):
        """Generate the GUI for all Inputs defined in the process description XML file"""
    
        # Create the complex inputs at first
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()
    
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
                  QApplication.translate("QgsWps","The process '%1' does not seem to support GML for the parameter '%2', which is required by the QGIS WPS client.").arg(self.processIdentifier).arg(inputIdentifier))
                return 0 
              
              # Store the input format for this parameter (after checking GML version supported)
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Vector inputs
              if maxOccurs == 1:
                self.addParameter(ParameterVector(inputIdentifier, title, ParameterVector.VECTOR_TYPE_ANY, minOccurs == 0))
                #self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
              else:
                self.addParameter(ParameterMultipleInput(inputIdentifier, title, ParameterVector.VECTOR_TYPE_ANY, minOccurs == 0))
                #self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            elif self.tools.isMimeTypeText(complexDataFormat["MimeType"]) != None:
              # Text inputs
              self.addParameter(ParameterString(inputIdentifier, title))
            elif self.tools.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:

              # Store the input format for this parameter
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Raster inputs
              #layerNamesList = self.tools.getLayerNameList(1)
              if maxOccurs == 1:
                self.addParameter(ParameterRaster(inputIdentifier, title, minOccurs == 0))
                #self.complexInputComboBoxList.append(self.tools.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
              else:
                self.addParameter(ParameterMultipleInput(inputIdentifier, title, ParameterVector.TYPE_RASTER, minOccurs == 0))
                #self.complexInputListWidgetList.append(self.tools.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
            
            elif self.tools.isMimeTypePlaylist(complexDataFormat["MimeType"]) != None:
              # Store the input format for this parameter
              self.inputDataTypeList[inputIdentifier] = complexDataFormat
              
              # Playlist (text) inputs
              self.addParameter(ParameterString(inputIdentifier, title))
              #self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, str(complexDataFormat))) 
            
            else:
              # We assume text inputs in case of an unknown mime type
              self.addParameter(ParameterString(inputIdentifier, title))
              #self.complexInputTextBoxList.append(self.tools.addComplexInputTextBox(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))            
    
        # Create the literal inputs as second
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()
    
          inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
    
          literalData = f_element.elementsByTagName("LiteralData")
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))
    
          if literalData.size() > 0:
            allowedValuesElement = literalData.at(0).toElement()
            aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
            dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
            if aValues.size() > 0:
              valList = self.tools.allowedValues(aValues)
              if len(valList) > 0:
                if len(valList[0]) > 0:
                  self.addParameter(ParameterSelection(inputIdentifier, title, valList)) 
                  #self.literalInputComboBoxList.append(self.tools.addLiteralComboBox(title, inputIdentifier, valList, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
                else:
                  self.addParameter(ParameterString(inputIdentifier, title))
                  #self.literalInputLineEditList.append(self.tools.addLiteralLineEdit(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, str(valList)))
            else:
              self.addParameter(ParameterString(inputIdentifier, title))
              #self.literalInputLineEditList.append(self.tools.addLiteralLineEdit(title, inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, dValue))
    
        # At last, create the bounding box inputs
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()
    
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
            
            self.addParameter(ParameterExtent("EXTENT","EXTENT"))
            #self.bboxInputLineEditList.append(self.tools.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout, myExtent))
    
            supportedCrsElements = bBoxElement.elementsByTagName("Supported")
    
            for i in range(supportedCrsElements.size()):
              crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))

            self.addParameter(ParameterCrs("CRS", "CRS"))
#            self.literalInputComboBoxList.append(self.tools.addLiteralComboBox("Supported CRS", inputIdentifier, crsListe, minOccurs,  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout))
    
    
        #self.tools.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"),  self.dlgProcessScrollAreaWidget,  self.dlgProcessScrollAreaWidgetLayout)
        
  ##############################################################################

    def generateProcessOutputsGUI(self, dataOutputs):
        """Generate the GUI for all complex ouputs defined in the process description XML file"""
    
        if dataOutputs.size() < 1:
            return
    
        # Add all complex outputs
        for i in range(dataOutputs.size()):
          f_element = dataOutputs.at(i).toElement()
    
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
            
            self.addOutput(OutputVector(outputIdentifier, title))
            #widget, comboBox = self.tools.addComplexOutputComboBox(groupbox, outputIdentifier, title, str(complexOutputFormat),  self.processIdentifier)
            #self.complexOutputComboBoxList.append(comboBox)
        
##############################################################################
    #Copied from QgsWpsDockWidget

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

    def defineProcess(self):
        """Create the execute request"""
        #self.doc.setContent(self.processXML)
        dataInputs = self.doc.elementsByTagName("Input")
        dataOutputs = self.doc.elementsByTagName("Output")

        postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        postString += "<wps:Execute service=\"WPS\" version=\""+ self.tools.getServiceVersion(self.doc) + "\"" + \
                       " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                       " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                       " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                       " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                       " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                       " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"

        postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
        postString += self.defineProcessInputs(dataInputs)
        postString += self.defineProcessOutputs(dataOutputs)

        postString += "</wps:Execute>"
        return postString

    def defineProcessInputs(self, dataInputs):
        postString = "<wps:DataInputs>"

        useSelected = False
        #if len(checkBoxes) > 0:
        #  useSelected = checkBoxes[0].isChecked()

        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))

          inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)

          complexData = f_element.elementsByTagName("ComplexData")

          # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
          if complexData.size() > 0:
            # Das i-te ComplexData Objekt auswerten
            complexDataTypeElement = complexData.at(0).toElement()
            supportedComplexDataFormat = self.tools.getSupportedMimeTypes(complexDataTypeElement)
            complexDataFormat = self.tools.getDefaultMimeType(complexDataTypeElement)

            # Attach the selected vector or raster maps
            if self.tools.isMimeTypeVector(complexDataFormat["MimeType"]) != None:

              # Since it is a vector, choose an appropriate GML version
              complexDataFormat = self.getSupportedGMLDataFormat(inputIdentifier) 

              postString += self.tools.xmlExecuteRequestInputStart(inputIdentifier)

              mimeType = complexDataFormat["MimeType"]
              schema = complexDataFormat["Schema"]
              encoding = complexDataFormat["Encoding"]
              self.myLayer = QGisLayers.getObjectFromUri(self.getParameterFromName(inputIdentifier).value, False)

              # Vector inputs
              if maxOccurs == 1:
                #ParameterVector
                #if self.tools.isMimeTypeVector(self.mimeType) != None and encoding != "base64":
                val = self.getParameterValue(inputIdentifier)
                postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + (("\" encoding=\"" + encoding + "\"") if encoding != "" else "\"") + ">"
                postString += self.tools.createTmpGML(self.myLayer, 
                  useSelected, mimeType).replace("> <","><")

                postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", 
                  "xsi:schemaLocation=\"" + schema.rsplit('/',1)[0] + "/ " + schema + "\"")
                postString += "</wps:ComplexData>\n"
              else:
                self.addParameter(ParameterMultipleInput(inputIdentifier, title, ParameterVector.VECTOR_TYPE_ANY, minOccurs == 0))
              postString += self.tools.xmlExecuteRequestInputEnd()  

            elif self.tools.isMimeTypeText(complexDataFormat["MimeType"]) != None:
              # Text inputs
              self.addParameter(ParameterString(inputIdentifier, title))
            elif self.tools.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:

              # Raster inputs
              if maxOccurs == 1:
                  #if self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
                  postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
                  postString += self.tools.createTmpBase64(self.myLayer)
              else:
                self.addParameter(ParameterMultipleInput(inputIdentifier, title, ParameterVector.TYPE_RASTER, minOccurs == 0))

            elif self.tools.isMimeTypePlaylist(complexDataFormat["MimeType"]) != None:
              # Playlist (text) inputs
              self.addParameter(ParameterString(inputIdentifier, title))

            else:
              # We assume text inputs in case of an unknown mime type
              self.addParameter(ParameterString(inputIdentifier, title))

        # literal inputs
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()

          inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)

          literalData = f_element.elementsByTagName("LiteralData")
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))

          if literalData.size() > 0:
            #ParameterString or ParameterSelection
            val = self.getParameterValue(inputIdentifier)
            postString += self.tools.xmlExecuteRequestInputStart(inputIdentifier)
            postString += "<wps:ComplexData>" + str(val) + "</wps:ComplexData>\n"
            postString += self.tools.xmlExecuteRequestInputEnd()

        # bounding box inputs
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()

          inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
          bBoxData = f_element.elementsByTagName("BoundingBoxData")

          if bBoxData.size() > 0:
            crsListe = []
            bBoxElement = bBoxData.at(0).toElement()
            defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()

            #self.addParameter(ParameterExtent("EXTENT","EXTENT"))
            #bboxArray = bbox.text().split(',')
            #postString += self.tools.xmlExecuteRequestInputStart(bbox.objectName())
            #postString += '<wps:BoundingBoxData ows:dimensions="2">'
            #postString += '<ows:LowerCorner>'+bboxArray[0]+' '+bboxArray[1]+'</ows:LowerCorner>'
            #postString += '<ows:UpperCorner>'+bboxArray[2]+' '+bboxArray[3]+'</ows:UpperCorner>'          
            #postString += "</wps:BoundingBoxData>\n"
            #postString += self.tools.xmlExecuteRequestInputEnd()

            #self.addParameter(ParameterCrs("CRS", "CRS"))

        postString += "</wps:DataInputs>\n"
        return postString

    def defineProcessOutputs(self, dataOutputs):
        postString = ""
        if dataOutputs.size() < 1:
            return postString

        postString += "<wps:ResponseForm>\n"
        # The server should store the result. No lineage should be returned or status
        postString += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"false\" status=\"false\">\n"

        # complex outputs
        for i in range(dataOutputs.size()):
          f_element = dataOutputs.at(i).toElement()

          outputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
          complexOutput = f_element.elementsByTagName("ComplexOutput")

          if complexOutput.size() > 0:
            # Complex data is always requested as reference
            postString += "<wps:Output>\n"
            postString += "<ows:Identifier>"+outputIdentifier+"</ows:Identifier>\n"
            postString += "</wps:Output>\n"

            # Das i-te ComplexData Objekt auswerten
            complexOutputTypeElement = complexOutput.at(0).toElement()
            complexOutputFormat = self.tools.getDefaultMimeType(complexOutputTypeElement)
            supportedcomplexOutputFormat = self.tools.getSupportedMimeTypes(complexOutputTypeElement)

            #OutputVector
            mimeType = complexOutputFormat["MimeType"]
            schema = complexOutputFormat["Schema"]
            encoding = complexOutputFormat["Encoding"]
            postString += "<wps:Output asReference=\"true" + \
              "\" mimeType=\"" + mimeType + "\"" + \
              ((" schema=\"" + schema + "\"") if schema != "" else "") + \
              ((" encoding=\"" + encoding + "\"") if encoding != "" else "") + ">"

            # Playlists can be sent as reference or as complex data 
            #   For the latter, comment out next lines
            #postString += "<wps:Output asReference=\"" + \
            #  ("false" if "playlist" in mimeType.lower() else "true") + \
            #  "\" mimeType=\"" + mimeType + \
            #  (("\" schema=\"" + schema) if schema != "" else "") + "\">"
            postString += "<ows:Identifier>" + outputIdentifier + "</ows:Identifier>\n"
            postString += "</wps:Output>\n"

        postString += "</wps:ResponseDocument>\n"
        postString  += "</wps:ResponseForm>\n"
        return postString

    def resultHandler(self, reply):
        """Handle the result of the WPS Execute request and add the outputs as new
           map layers to the registry or open an information window to show literal
           outputs."""
        resultXML = reply.readAll().data()
        qDebug(resultXML)
        self.processExecuted = True
        return True

    def processAlgorithm(self, progress):
        postString = self.defineProcess()
        qDebug(postString)
        self.processExecuted = False
        self.tools.executeProcess(self.processUrl, postString, self.resultHandler)
        #if dataInputs.size() > 0:
        #  QObject.connect(self.thePostReply, SIGNAL("uploadProgress(qint64,qint64)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status)) 
        #Wait for answer
        while not self.processExecuted:
             qApp.processEvents()
