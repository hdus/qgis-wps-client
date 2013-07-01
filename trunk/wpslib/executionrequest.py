# -*- coding: latin1 -*-  
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

from PyQt4.QtCore import *
from PyQt4 import QtXml
from PyQt4.QtGui import QApplication,QMessageBox
from PyQt4.QtSql import *
from qgis.core import QgsVectorFileWriter
import os, sys, string, tempfile, base64


# Execute example:
#
#<?xml version="1.0" encoding="utf-8" standalone="yes"?>
#<wps:Execute service="WPS" version="1.0.0"
#xmlns:wps="http://www.opengis.net/wps/1.0.0"
#xmlns:ows="http://www.opengis.net/ows/1.1"
#xmlns:xlink="http://www.w3.org/1999/xlink"
#xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
#
#  <ows:Identifier>returner</ows:Identifier>
#  <wps:DataInputs>
#    <wps:Input>
#      <ows:Identifier>data</ows:Identifier>
#      <ows:Title>data</ows:Title>
#      <wps:Data>
#        <wps:ComplexData mimeType="text/xml" schema="">
#          <ogr:FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#          xsi:schemaLocation="/"
#          xmlns:ogr="http://ogr.maptools.org/"
#          xmlns:gml="http://www.opengis.net/gml">
#            <gml:boundedBy>
#              <gml:Box>
#                <gml:coord>
#                  <gml:X>9.5</gml:X>
#                  <gml:Y>47.0666667</gml:Y>
#                </gml:coord>
#                <gml:coord>
#                  <gml:X>9.6083946</gml:X>
#                  <gml:Y>47.2397558</gml:Y>
#                </gml:coord>
#              </gml:Box>
#            </gml:boundedBy>
#            <gml:featureMember>
#              <ogr:qt_temp fid="qt_temp.0">
#                <ogr:geometryProperty>
#                  <gml:Point>
#                    <gml:coordinates>
#                    9.5450182,47.178495</gml:coordinates>
#                  </gml:Point>
#                </ogr:geometryProperty>
#                <ogr:osm_id>32011241</ogr:osm_id>
#                <ogr:name>Oberplanken</ogr:name>
#                <ogr:type>suburb</ogr:type>
#                <ogr:population>0</ogr:population>
#              </ogr:qt_temp>
#            </gml:featureMember>
#            <!-- ... -->
#          </ogr:FeatureCollection>
#        </wps:ComplexData>
#      </wps:Data>
#    </wps:Input>
#    <wps:Input>
#      <ows:Identifier>text</ows:Identifier>
#      <ows:Title>text</ows:Title>
#      <wps:Data>
#        <wps:LiteralData>25</wps:LiteralData>
#      </wps:Data>
#    </wps:Input>
#  </wps:DataInputs>
#  <wps:ResponseForm>
#    <wps:ResponseDocument lineage="false"
#    storeExecuteResponse="false" status="false">
#      <wps:Output>
#        <ows:Identifier>text</ows:Identifier>
#      </wps:Output>
#      <wps:Output asReference="true" mimeType="text/xml">
#        <ows:Identifier>output2</ows:Identifier>
#      </wps:Output>
#      <wps:Output asReference="true" mimeType="text/xml">
#        <ows:Identifier>output1</ows:Identifier>
#      </wps:Output>
#    </wps:ResponseDocument>
#  </wps:ResponseForm>
#</wps:Execute>


def createTmpBase64(rLayer):
  try:
#      tmpFile = tempfile.NamedTemporaryFile(prefix="base64", delete=False)
#      infile = open(unicode(rLayer.source()))
#      tmpFileName = tmpFile.name
#      outfile = open(tmpFileName, 'w')
#      base64.encode(infile,outfile)
#      outfile.close()
#      outfile =  open(tmpFileName, 'r')
#      base64String = outfile.read()
#      outfile.close()
#      os.remove(tmpFile.name)

        tmpFile = tempfile.NamedTemporaryFile(prefix="base64", delete=False)
        infile = open(rLayer.source())
        tmpFileName = tmpFile.name
        outfile = tmpFile #open(tmpFileName, 'w')
        base64.encode(infile,outfile)
        outfile.close()
        infile.close()
        outfile =  open(tmpFileName, 'r')
        base64String = outfile.read()
        outfile.close()
        os.remove(tmpFileName)

  except:
      QMessageBox.critical(None, QApplication.translate("QgsWps","Error"), QApplication.translate("QgsWps","Unable to create temporal file: ") + filename + QApplication.translate("QgsWps"," for base64 encoding") ) 
  return base64String

def createTmpGML(vLayer, processSelection="False", supportedGML="GML2"):
    if supportedGML == "": # Neither GML, GML2 or GML3 are supported!
      return 0

    myQTempFile = QTemporaryFile()
    myQTempFile.open()
    tmpFile = unicode(myQTempFile.fileName()+".gml",'latin1')
    myQTempFile.close()

    if vLayer.dataProvider().name() == "postgres":
      encoding = getDBEncoding(vLayer.dataProvider())
    else:
      encoding = vLayer.dataProvider().encoding()

    processSelected = False
    if processSelection and vLayer.selectedFeatureCount() > 0:
      processSelected = True

    # FORMAT=GML3 only works with OGR >= 1.8.0, otherwise GML2 is always returned
    if supportedGML == "GML3":
      dso = QStringList("FORMAT=GML3")
    else: # "GML" or "GML2"
      dso = QStringList()
    lco = QStringList()
    error = QgsVectorFileWriter.writeAsVectorFormat(vLayer, tmpFile, encoding, vLayer.dataProvider().crs(), "GML",  processSelected,  "",  dso,  lco)
    if error != QgsVectorFileWriter.NoError:
        QMessageBox.information(None, 'Error',  'Process stopped with errors')
    else:
        myFile = QFile(tmpFile)
        if (not myFile.open(QIODevice.ReadOnly | QIODevice.Text)):
          QMessageBox.information(None, '', QApplication.translate("QgsWps","File open problem"))
          pass

        myGML = QTextStream(myFile)
        myGML.setCodec(encoding)
        gmlString = ""
        # Overread the first Line of GML Result
        dummy = myGML.readLine()
        gmlString += myGML.readAll()
        myFile.close()
        myFilePath = QFileInfo(myFile).dir().path()
        myFileInfo = myFilePath+'/'+QFileInfo(myFile).completeBaseName()
        QFile(myFileInfo+'.xsd').remove()
        QFile(myFileInfo+'.gml').remove()
    return gmlString.simplified()

def getDBEncoding(layerProvider):
    dbConnection = QgsDataSourceURI(layerProvider.dataSourceUri())
    db = QSqlDatabase.addDatabase("QPSQL","WPSClient")
    db.setHostName(dbConnection.host())
    db.setDatabaseName(dbConnection.database())
    db.setUserName(dbConnection.username())
    db.setPassword(dbConnection.password())
    db.setPort(int(dbConnection.port()))
    db.open()

    query =  "select pg_encoding_to_char(encoding) as encoding "
    query += "from pg_catalog.pg_database "
    query += "where datname = '"+dbConnection.database()+"' "

    result = QSqlQuery(query,db)
    result.first()
    encoding = result.value(0).toString()
    db.close()

    return encoding



class ExecutionRequest(QObject):
    """
    Compose request XML for WPS execution
    """

    def __init__(self, process):
        QObject.__init__(self)
        self.process = process
        self.request = ""

    def addExecuteRequestHeader(self):
        identifier = self.process.processIdentifier
        version = self.process.getServiceVersion()
        self.request = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        self.request += "<wps:Execute service=\"WPS\" version=\""+ version + "\"" + \
                       " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                       " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                       " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                       " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                       " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                       " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"
        self.request += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"

    def addExecuteRequestEnd(self):
        self.request += "</wps:Execute>"

    def addDataInputsStart(self):
        self.request += "<wps:DataInputs>\n"

    def addDataInputsEnd(self):
        self.request += "</wps:DataInputs>\n"

    def addExecuteRequestInputStart(self, identifier, includeData=True):
        self.request += "<wps:Input>\n"
        self.request += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"
        self.request += "<ows:Title>"+identifier+"</ows:Title>\n"
        if includeData: self.request += "<wps:Data>\n"

    def addExecuteRequestInputEnd(self, includeData=True):
        if includeData: self.request += "</wps:Data>\n"
        self.request += "</wps:Input>\n"

    def addReferenceInput(self, identifier, mimeType, schema, encoding, ref):
        # text/plain inputs ########################################################
        # Handle 'as reference' playlist
        self.addExecuteRequestInputStart(identifier, False)
        self.request += "<wps:Reference mimeType=\"" + mimeType + "\" " + (("schema=\"" + schema + "\"") if schema != "" else "") + (("encoding=\"" + encoding + "\"") if encoding != "" else "") + " xlink:href=\"" + ref + "\" />"
        self.addExecuteRequestInputEnd(False)

    def addPlainTextInput(self, identifier, text):
        # text/plain inputs ########################################################
        # It's not a playlist
        self.addExecuteRequestInputStart(identifier)
        self.request += "<wps:ComplexData>" + text + "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()

    def addGeometryInput(self, identifier, mimeType, schema, encoding, gmldata, useSelected):
        # Single raster and vector inputs ##########################################
        #if self.tools.isMimeTypeVector(mimeType) != None and encoding != "base64":
        self.addExecuteRequestInputStart(identifier)
        
        self.request += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + (("\" encoding=\"" + encoding + "\"") if encoding != "" else "\"") + ">"
        self.request += gmldata.replace("> <","><")
          
        self.request = self.request.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", 
            "xsi:schemaLocation=\"" + schema.rsplit('/',1)[0] + "/ " + schema + "\"")
        
        self.request += "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()  

    def addGeometryBase64Input(self, identifier, mimeType, data):
        # Single raster and vector inputs ##########################################
        #elif self.tools.isMimeTypeVector(mimeType) != None or self.tools.isMimeTypeRaster(mimeType) != None:
        self.addExecuteRequestInputStart(identifier)

        self.request += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
        self.request += createTmpBase64(data)
        
        self.request += "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()

    def addFileBase64Input(self, identifier, mimeType, filename):
        self.addExecuteRequestInputStart(identifier)

        self.request += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"

        file = open(filename, 'r')
        self.request += base64.encodestring(file.read())
        file.close()

        self.request += "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()

    def addMultipleGeometryInput(self, identifier, mimeType, schema, encoding, gmldata, useSelected):
        # Multiple raster and vector inputs ########################################
        #if self.tools.isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
        self.addExecuteRequestInputStart(identifier)

        self.request += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + (("\" encoding=\"" + encoding + "\"") if encoding != "" else "\"") + ">"
        self.request += gmldata.replace("> <","><")

        self.request += "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()

    def addMultipleGeometryBase64Input(self, identifier, mimeType, data):
        # Multiple raster and vector inputs ########################################
        #elif self.tools.isMimeTypeVector(mimeType) != None or self.tools.isMimeTypeRaster(mimeType) != None:
        self.addExecuteRequestInputStart(identifier)

        self.request += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
        self.request += createTmpBase64(data)

        self.request += "</wps:ComplexData>\n"
        self.addExecuteRequestInputEnd()

    def addLiteralDataInput(self, identifier, text):
        self.addExecuteRequestInputStart(identifier)
        self.request += "<wps:LiteralData>"+unicode(text)+"</wps:LiteralData>\n"
        self.addExecuteRequestInputEnd()

    def addBoundingBoxInput(self, identifier, bboxArray):
        self.addExecuteRequestInputStart(identifier)
        self.request += '<wps:BoundingBoxData ows:dimensions="2">'
        self.request += '<ows:LowerCorner>'+bboxArray[0]+' '+bboxArray[1]+'</ows:LowerCorner>'
        self.request += '<ows:UpperCorner>'+bboxArray[2]+' '+bboxArray[3]+'</ows:UpperCorner>'          
        self.request += "</wps:BoundingBoxData>\n"
        self.addExecuteRequestInputEnd()

    def addResponseFormStart(self):
        self.request += "<wps:ResponseForm>\n"
        # The server should store the result. No lineage should be returned or status
        self.request += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"false\" status=\"false\">\n"

    def addResponseFormEnd(self):
        self.request += "</wps:ResponseDocument>\n"
        self.request  += "</wps:ResponseForm>\n"

    def addLiteralDataOutput(self, identifier):
        # Attach ALL literal outputs #############################################        
        self.request += "<wps:Output>\n"
        self.request += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"
        self.request += "</wps:Output>\n"

    def addReferenceOutput(self, identifier, mimeType, schema, encoding):
        self.request += "<wps:Output asReference=\"true" + \
        "\" mimeType=\"" + mimeType + "\"" + \
        ((" schema=\"" + schema + "\"") if schema != "" else "") + \
        ((" encoding=\"" + encoding + "\"") if encoding != "" else "") + ">"
        
        # Playlists can be sent as reference or as complex data 
        #   For the latter, comment out next lines
        #self.request += "<wps:Output asReference=\"" + \
        #  ("false" if "playlist" in mimeType.lower() else "true") + \
        #  "\" mimeType=\"" + mimeType + \
        #  (("\" schema=\"" + schema) if schema != "" else "") + "\">"
        self.request += "<ows:Identifier>" + identifier + "</ows:Identifier>\n"
        self.request += "</wps:Output>\n"
