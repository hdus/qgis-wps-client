from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.SextanteLog import SextanteLog
from sextante.outputs.OutputFactory import OutputFactory
from sextante.parameters.ParameterFactory import ParameterFactory
from sextante.core.Sextante import Sextante
import time,  inspect

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgswpstools import *
from QgsWpsDockWidget import QgsWpsDockWidget


class WpsAlgorithm(GeoAlgorithm):
    '''This is an example algorithm that takes a vector layer and creates
    a new one just with just those features of the input layer that are
    selected.
    It is meant to be used as an example of how to create your own SEXTANTE
    algorithms and explain methods and variables used to do it.
    An algorithm like this will be available in all SEXTANTE elements, and
    there is not need for additional work.

    All SEXTANTE algorithms should extend the GeoAlgorithm class'''

    #constants used to refer to parameters and outputs.
    #They will be used when calling the algorithm from another algorithm,
    #or when calling SEXTANTE from the QGIS console.
    OUTPUT_LAYER = "OUTPUT_LAYER"
    INPUT_LAYER = "INPUT_LAYER"

    def __init__(self, descriptionfile):
        GeoAlgorithm.__init__(self)
#        QMessageBox.information(None, 'in alg',  descriptionfile)
        self.descriptionFile = descriptionfile
        self.defineCharacteristicsFromFile()
        self.numExportedLayers = 0
        
    def defineCharacteristicsFromFile(self):
        lines = open(self.descriptionFile)
        line = lines.readline().strip("\n").strip()
        self.name = line
        line = lines.readline().strip("\n").strip()
        self.group = line
        while line != "":
            try:
                    line = line.strip("\n").strip()
                    if line.startswith("Parameter"):
                        self.addParameter(ParameterFactory.getFromString(line))
                    else:
                        self.addOutput(OutputFactory.getFromString(line))
                    line = lines.readline().strip("\n").strip()
            except Exception,e:
                SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open WPS algorithm: " + self.descriptionFile + "\n" + line)
                raise e
        lines.close()

    def processAlgorithm(self, progress):
        '''Here is where the processing itself takes place'''
        processName = self.parameters.name.split('@@')
        self.processIdentifier = processName[1]
        self.defineProcess(self.parameters)
        
        
    def defineProcess(self,  sextanteParams):
        """Create the execute request"""
        
        serviceUrl = self.tools.getBookmarkXmlUrl(sextanteParams.name)
        QMessageBox.information(None, '', serviceUrl)
#
#        postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
#        postString += "<wps:Execute service=\"WPS\" version=\"1.0.0\"" + \
#                       " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
#                       " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
#                       " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
#                       " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
#                       " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
#                       " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"
#
#        postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
#        postString += "<wps:DataInputs>"
#        if dataInputs.size() > 0:
#            # text/plain inputs ########################################################
#            for textBox in self.complexInputTextBoxList:
#              # Do not add undefined inputs
#              if textBox == None or str(textBox.document().toPlainText()) == "":
#                continue
#
#              postString += self.tools.xmlExecuteRequestInputStart(textBox.objectName())
#              postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
#              postString += self.tools.xmlExecuteRequestInputEnd()
#
#
#            # Single raster and vector inputs ##########################################
#            for comboBox in self.complexInputComboBoxList:
#              # Do not add undefined inputs
#              if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
#                continue
#
#              postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())
#
#              # TODO: Check for more types
#              self.mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
#              schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
#              encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]
#              self.myLayer = self.tools.getVLayer(comboBox.currentText())
#
#              try:
#                  if self.tools.isMimeTypeVector(self.mimeType) != None and self.mimeType == "text/xml":
#                    postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
#                    postString += self.tools.createTmpGML(comboBox.currentText(), useSelected).replace("> <","><")
#                    postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", "xsi:schemaLocation=\"http://schemas.opengis.net/gml/3.1.1/base/ http://schemas.opengis.net/gml/3.1.1/base/gml.xsd\"")
#                  elif self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
#                    postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
#                    postString += self.tools.createTmpBase64(comboBox.currentText())
#              except:
#                  QApplication.restoreOverrideCursor()
#                  QMessageBox.warning(None, QApplication.translate("QgsWps","Error"),  QApplication.translate("QgsWps","Please load or select a vector layer!"))
#                  return
#
#              postString += "</wps:ComplexData>\n"
#              postString += self.tools.xmlExecuteRequestInputEnd()
#
#            # Multiple raster and vector inputs ########################################
#            for listWidgets in self.complexInputListWidgetList:
#              # Do not add undefined inputs
#              if listWidgets == None:
#                continue
#
#              self.mimeType = self.inputDataTypeList[listWidgets.objectName()]["MimeType"]
#              schema = self.inputDataTypeList[listWidgets.objectName()]["Schema"]
#              encoding = self.inputDataTypeList[listWidgets.objectName()]["Encoding"]
#
#              # Iterate over each seletced item
#              for i in range(listWidgets.count()):
#                listWidget = listWidgets.item(i)
#                if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
#                  continue
#
#                postString += self.tools.xmlExecuteRequestInputStart(listWidgets.objectName())
#
#                # TODO: Check for more types
#                if self.tools.isMimeTypeVector(self.mimeType) != None and self.mimeType == "text/xml":
#                  postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
#        #          postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <","><").replace("http://ogr.maptools.org/ qt_temp.xsd","http://ogr.maptools.org/qt_temp.xsd")
#                  postString += self.tools.createTmpGML(listWidget.text(), useSelected).replace("> <","><")
#                elif self.tools.isMimeTypeVector(self.mimeType) != None or self.tools.isMimeTypeRaster(self.mimeType) != None:
#                  postString += "<wps:ComplexData mimeType=\"" + self.mimeType + "\" encoding=\"base64\">\n"
#                  postString += self.tools.createTmpBase64(listWidget.text())
#
#                postString += "</wps:ComplexData>\n"
#                postString += self.tools.xmlExecuteRequestInputEnd()
#
#            # Literal data as combo box choice #########################################
#            for comboBox in self.literalInputComboBoxList:
#              if comboBox == None or comboBox.currentText() == "":
#                  continue
#
#              postString += self.tools.xmlExecuteRequestInputStart(comboBox.objectName())
#              postString += "<wps:LiteralData>"+comboBox.currentText()+"</wps:LiteralData>\n"
#              postString += self.tools.xmlExecuteRequestInputEnd()
#
#           # Literal data as combo box choice #########################################
#            for lineEdit in self.literalInputLineEditList:
#              if lineEdit == None or lineEdit.text() == "":
#                  continue
#
#              postString += self.tools.xmlExecuteRequestInputStart(lineEdit.objectName())
#              postString += "<wps:LiteralData>"+lineEdit.text()+"</wps:LiteralData>\n"
#              postString += self.tools.xmlExecuteRequestInputEnd()
#
#           # BBOX data as lineEdit #########################################
#            for bbox in self.bboxInputLineEditList:
#              if bbox == None or bbox.text() == "":
#                  continue
#
#              bboxArray = bbox.text().split(',')
#
#              postString += self.tools.xmlExecuteRequestInputStart(bbox.objectName())
#              postString += '<wps:BoundingBoxData ows:dimensions="2">'
#              postString += '<ows:LowerCorner>'+bboxArray[0]+' '+bboxArray[1]+'</ows:LowerCorner>'
#              postString += '<ows:UpperCorner>'+bboxArray[2]+' '+bboxArray[3]+'</ows:UpperCorner>'          
#              postString += "</wps:BoundingBoxData>\n"
#              postString += self.tools.xmlExecuteRequestInputEnd()
#
#
#        postString += "</wps:DataInputs>\n"
#
#
#        # Attach only defined outputs
#        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
#          postString += "<wps:ResponseForm>\n"
#          # The server should store the result. No lineage should be returned or status
#          postString += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"false\" status=\"false\">\n"
#
#          # Attach ALL literal outputs #############################################
#          for i in range(dataOutputs.size()):
#            f_element = dataOutputs.at(i).toElement()
#            outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
#            literalOutputType = f_element.elementsByTagName("LiteralOutput")
#
#            # Complex data is always requested as reference
#            if literalOutputType.size() != 0:
#              postString += "<wps:Output>\n"
#              postString += "<ows:Identifier>"+outputIdentifier+"</ows:Identifier>\n"
#              postString += "</wps:Output>\n"
#
#          # Attach selected complex outputs ########################################
#          for comboBox in self.complexOutputComboBoxList:
#            # Do not add undefined outputs
#            if comboBox == None or str(comboBox.currentText()) == "<None>":
#              continue
#            outputIdentifier = comboBox.objectName()
#
#            self.mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
#            schema = self.outputDataTypeList[outputIdentifier]["Schema"]
#            encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]
#
#            postString += "<wps:Output asReference=\"true\" mimeType=\"" + self.mimeType + "\" schema=\"" + schema + "\">"
#            postString += "<ows:Identifier>" + outputIdentifier + "</ows:Identifier>\n"
#            postString += "</wps:Output>\n"
#
#          postString += "</wps:ResponseDocument>\n"
#          postString  += "</wps:ResponseForm>\n"
#
#        postString += "</wps:Execute>"
#
#
#        # This is for debug purpose only
#        if DEBUG == True:
##            self.tools.popUpMessageBox("Execute request", postString)
#            # Write the request into a file
#            outFile = open('/tmp/qwps_execute_request.xml', 'w')
#            outFile.write(postString)
#            outFile.close()
#
#        QApplication.restoreOverrideCursor()
#        self.setProcessStarted()        
#        self.postData = QByteArray()
#        self.postData.append(postString) 
#
#        wpsConnection = scheme+'://'+server+path
#
#        self.thePostHttp = QgsNetworkAccessManager.instance() 
#        url = QUrl(wpsConnection)
#        url.setPort(port)
#        try:
#            self.thePostHttp.finished.disconnect()    
#        except:
#            pass
#
#
#        self.thePostHttp.finished.connect(self.resultHandler)                  
#        self.request = QNetworkRequest(url)
#        self.request.setHeader( QNetworkRequest.ContentTypeHeader, "text/xml" );        
#        self.thePostReply = self.thePostHttp.post(self.request, self.postData)      
#
#        if dataInputs.size() > 0:
#          QObject.connect(self.thePostReply, SIGNAL("uploadProgress(qint64,qint64)"), lambda done,  all,  status="upload": self.showProgressBar(done,  all,  status)) 
#        
#        for param in self.parameters:
#            QMessageBox.information(None, '', self.name+'  '+str(param.name)+': '+str(param.value))
        #the first thing to do is retrieve the values of the parameters
        #entered by the user
#        inputFilename = self.getParameterValue(self.INPUT_LAYER)
#        output = self.getOutputValue(self.OUTPUT_LAYER)

        #input layers values are always a string with its location.name     
        #That string can be converted into a QGIS object (a QgsVectorLayer in this case))
        #using the Sextante.getObject() method
#        vectorLayer = Sextante.getObject(inputFilename)

        #And now we can process

        #First we create the output layer.
        #The output value entered by the user is a string containing a filename,
        #so we can use it directly
#        settings = QSettings()
#        systemEncoding = settings.value( "/UI/encoding", "System" ).toString()
#        provider = vectorLayer.dataProvider()
#        writer = QgsVectorFileWriter( output, systemEncoding,provider.fields(), provider.geometryType(), provider.crs() )

        #Now we take the selected features and add them to the output layer
#        selection = vectorLayer.selectedFeatures()
#        for feat in selection:
#            writer.addFeature(feat)
#        del writer

        #There is nothing more to do here. We do not have to open the layer that we have created.
        #SEXTANTE will take care of that, or will handle it if this algorithm is executed within
        #a complex model
