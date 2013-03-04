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
from wps.wpslib.processdescription import ProcessDescription
from wps.wpslib.executerequest import ExecuteRequest
from wps.qgswpstools import QgsWpsTools
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtXml
#http communication:
from qgis.core import *
from PyQt4.QtNetwork import *
from functools import partial


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
        self.process = ProcessDescription()
        QObject.connect(self.process, SIGNAL("describeProcessFinished"), self.describeProcessFinished)

        result = self.tools.getServer(self.processName)
        path = result["path"]
        server = result["server"]
        method = result["method"]
        version = result["version"]
        scheme = result["scheme"]
        baseUrl = scheme+"://"+server+path

        self.process.requestDescribeProcess(baseUrl, self.processIdentifier, version)

        #Wait for answer
        while self.processXML == None:
             qApp.processEvents()
        qDebug(self.processXML)

    @pyqtSlot()
    def describeProcessFinished(self):
        self.processXML = self.process.processXML

    def buildParametersDialog(self):
        for input in self.process.inputs:
            inputType = type(input).__name__
            if inputType == 'VectorInput':
                self.addParameter(ParameterVector(input.identifier, input.title, ParameterVector.VECTOR_TYPE_ANY, input.minOccurs == 0))
            elif inputType == 'MultipleVectorInput':
                self.addParameter(ParameterMultipleInput(input.identifier, input.title, ParameterVector.VECTOR_TYPE_ANY, input.minOccurs == 0))
            elif inputType == 'StringInput':
                self.addParameter(ParameterString(input.identifier, input.title))
            elif inputType == 'RasterInput':
                self.addParameter(ParameterRaster(input.identifier, input.title, input.minOccurs == 0))
            elif inputType == 'MultipleRasterInput':
                self.addParameter(ParameterMultipleInput(input.identifier, input.title, ParameterVector.TYPE_RASTER, input.minOccurs == 0))
            elif inputType == 'SelectionInput':
                self.addParameter(ParameterSelection(input.identifier, input.title, input.valList)) 
            elif inputType == 'ExtentInput':
                #myExtent = self.iface.mapCanvas().extent().toString().replace(':',',')
                self.addParameter(ParameterExtent("EXTENT","EXTENT"))
            elif inputType == 'CrsInput':
                self.addParameter(ParameterCrs("CRS", "CRS"))

        for output in self.process.outputs:
            outputType = type(output).__name__
            if outputType == 'VectorOutput':
                self.addOutput(OutputVector(output.identifier, output.title))

    def defineProcess(self):
        """Create the execute request"""
        request = ExecuteRequest(self.process)
        request.addExecuteRequestHeader(self.processIdentifier, self.tools.getServiceVersion(self.process.doc))

        # inputs
        useSelected = False
        request.addDataInputsStart()
        for input in self.process.inputs:
            inputType = type(input).__name__
            value = self.getParameterValue(input.identifier)
            if inputType == 'VectorInput':
                layer = QGisLayers.getObjectFromUri(value, False)
                mimeType = input.dataFormat["MimeType"]
                data = self.tools.createTmpGML(layer, useSelected, mimeType)
                request.addGeometryInput(input.identifier, mimeType, input.dataFormat["Schema"], input.dataFormat["Encoding"], data, useSelected)
            elif inputType == 'MultipleVectorInput':
                #ParameterMultipleInput(input.identifier, input.title, ParameterVector.VECTOR_TYPE_ANY, input.minOccurs == 0))
                pass
            elif inputType == 'StringInput':
                request.addLiteralDataInput(input.identifier, str(value))
                pass
            elif inputType == 'RasterInput':
                #ParameterRaster(input.identifier, input.title, input.minOccurs == 0))
                pass
            elif inputType == 'MultipleRasterInput':
                #ParameterMultipleInput(input.identifier, input.title, ParameterVector.TYPE_RASTER, input.minOccurs == 0))
                pass
            elif inputType == 'SelectionInput':
                #ParameterSelection(input.identifier, input.title, input.valList)) 
                pass
            elif inputType == 'ExtentInput':
                #myExtent = self.iface.mapCanvas().extent().toString().replace(':',',')
                #ParameterExtent("EXTENT","EXTENT"))
                pass
            elif inputType == 'CrsInput':
                #ParameterCrs("CRS", "CRS"))
                pass
        request.addDataInputsEnd()

        # outputs
        request.addResponseFormStart()
        for output in self.process.outputs:
            outputType = type(output).__name__
            mimeType = output.dataFormat["MimeType"]
            schema = output.dataFormat["Schema"]
            encoding = output.dataFormat["Encoding"]
            if outputType == 'VectorOutput':
                request.addReferenceOutput(output.identifier, mimeType, schema, encoding)
        request.addResponseFormEnd()

        request.addExecuteRequestEnd()
        return request.request

    def resultHandler(self, reply):
        """Handle the result of the WPS Execute request and add the outputs as new
           map layers to the registry or open an information window to show literal
           outputs."""
        resultXML = reply.readAll().data()
        qDebug(resultXML)
        self.parseResult(resultXML)
        self.processExecuted = True
        return True

    def parseResult(self, resultXML):
        self.doc = QtXml.QDomDocument()
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
                    self.streamingHandler(encoding, fileLink) #FIXME: not supported yet
                  else: # Conventional processes
                    self.fetchResult(encoding, fileLink, identifier)
                    #self.setStatusLabel('finished')

              elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "ComplexData").size() > 0:
                complexData = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","ComplexData").at(0).toElement()

                # Get the mime type of the result
                self.mimeType = str(complexData.attribute("mimeType", "0").toLower())

                # Get the encoding of the result, it can be used decoding base64
                encoding = str(complexData.attribute("encoding", "").toLower())

                if "playlist" in self.mimeType:
                  playlistUrl = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "ComplexData").at(0).toElement().text()
                  self.streamingHandler(encoding, playlistUrl) #FIXME: not supported yet

                else: # Other ComplexData are not supported by this WPS client
                  QMessageBox.warning(self.iface.mainWindow(), '', 
                    str(QApplication.translate("QgsWps", "WPS Error: The mimeType '" + mimeType + "' is not supported by this client")))

              elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
                literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
                self.setOutputValue(identifier, literalText)
                #self.setStatusLabel('finished')
              else:
                QMessageBox.warning(self.iface.mainWindow(), '', 
                  str(QApplication.translate("QgsWps", "WPS Error: Missing reference or literal data in response")))
        else:
            status = self.doc.elementsByTagName("Status")
            if status.size() == 0:
              #self.setStatusLabel('error')
              return self.errorHandler(resultXML)


 ##############################################################################


    def loadData(self, resultFile, identifier):
        # Vector data 
        # TODO: Check for schema GML and KML
        if self.tools.isMimeTypeVector(self.mimeType) != None:
            self.setOutputValue(identifier, resultFile)
       # Raster data
        elif self.tools.isMimeTypeRaster(self.mimeType) != None:
            self.setOutputValue(identifier, resultFile)

        # Text data
        elif self.tools.isMimeTypeText(self.mimeType) != None:
            text = open(resultFile, 'r').read()
            self.setOutputValue(identifier, text)

        # Everything else
        elif self.tools.isMimeTypeFile(self.mimeType) != None:
            text = open(resultFile, 'r').read()
            self.setOutputValue(identifier, text)

        # Everything else
        else:
            # For unsupported mime types we assume text
            content = open(resultFile, 'r').read()
            # TODO: This should have a safe option
            self.tools.popUpMessageBox(QCoreApplication.translate("QgsWps", 'Process result (unsupported mime type)'), content)

    def fetchResult(self, encoding, fileLink, identifier):
        self.noFilesToFetch += 1
        url = QUrl(fileLink)
        self.myHttp = QgsNetworkAccessManager.instance()
        self.theReply = self.myHttp.get(QNetworkRequest(url))

        # Append encoding to 'finished' signal parameters
        self.encoding = encoding
        self.theReply.finished.connect(partial(self.getResultFile, identifier, encoding,  self.theReply))  

        #QObject.connect(self.theReply, SIGNAL("downloadProgress(qint64, qint64)"), lambda done,  all,  status="download": self.showProgressBar(done,  all,  status)) 


    def getResultFile(self, identifier, encoding, reply):
    # Check if there is redirection 

        reDir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        if not reDir.isEmpty():
            self.fetchResult(self.encoding, reDir, identifier)
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
        if self.encoding == "base64":
            resultFile = self.tools.decodeBase64(tmpFile, self.mimeType)
        else:
            resultFile = tmpFile

        # Finally, load the data
        self.loadData(resultFile, identifier)
        self.noFilesToFetch -= 1
        #self.setStatusLabel('finished')


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

    def processAlgorithm(self, progress):
        postString = self.defineProcess()
        qDebug(postString)
        self.processExecuted = False
        self.noFilesToFetch = 0
        self.tools.executeProcess(self.process.processUrl, postString, self.resultHandler)
        #if dataInputs.size() > 0:
        #  QObject.connect(self.thePostReply, SIGNAL("uploadProgress(qint64,qint64)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status)) 
        #Wait for answer
        while (not self.processExecuted) or (self.noFilesToFetch > 0):
             qApp.processEvents()
