# -*- coding: latin1 -*-
# /***************************************************************************
#   qgswpstools.py QGIS Web Processing Service Plugin
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
from PyQt4.QtSql import *
from qgis.core import *
from httplib import *
from urlparse import urlparse
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
import os, sys, string, tempfile,  base64

# initialize Qt resources from file resources.py
import resources


# All supported import raster formats
RASTER_MIMETYPES =        [{"MIMETYPE":"IMAGE/TIFF", "GDALID":"GTiff"},
                           {"MIMETYPE":"IMAGE/PNG", "GDALID":"PNG"}, \
                           {"MIMETYPE":"IMAGE/GIF", "GDALID":"GIF"}, \
                           {"MIMETYPE":"IMAGE/JPEG", "GDALID":"JPEG"}, \
                           {"MIMETYPE":"IMAGE/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-ERDAS-HFA", "GDALID":"HFA"}, \
                           {"MIMETYPE":"APPLICATION/NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/X-NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-GEOTIFF", "GDALID":"GTiff"}]
# All supported input vector formats [mime type, schema]
VECTOR_MIMETYPES =        [{"MIMETYPE":"TEXT/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
                           {"MIMETYPE":"TEXT/XML", "SCHEMA":"KML", "GDALID":"KML"}, \
                           {"MIMETYPE":"APPLICATION/DGN", "SCHEMA":"", "GDALID":"DGN"}, \
                           #{"MIMETYPE":"APPLICATION/X-ZIPPED-SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}, \
                           {"MIMETYPE":"APPLICATION/SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}]

# Our help class for the plugin
class QgsWpsTools:
    
  def __init__(self, iface):
    self.iface = iface
    self.doc = QtXml.QDomDocument()

  ##############################################################################

  def webConnectionExists(self, connection):
    try:
      xmlString = self.getServiceXML(connection,"GetCapabilities")
      return True
    except:
      QMessageBox.critical(None,'','Web Connection Failed')
      return False


  ##############################################################################

  # Gets Server and Connection Info from Stored Server Connections in QGIS Settings
  # Param: String ConnectionName
  # Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)
  def getServer(self,name):
    settings = QSettings()
    mySettings = "/WPS/"+name
    result = {}
    result["scheme"] = settings.value(mySettings+"/scheme").toString()
    result["server"] = settings.value(mySettings+"/server").toString()
    result["path"] = settings.value(mySettings+"/path").toString()
    result["method"] = settings.value(mySettings+"/method").toString()
    result["version"] = settings.value(mySettings+"/version").toString()
    return result    

  ##############################################################################
  
  # Gets Server and Connection Info from Stored Server Connections
  # Param: String ConnectionName
  # Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)
  def getServiceXML(self, name, request, identifier=''):
    result = self.getServer(name)
    path = result["path"]
    server = result["server"]
    method = result["method"]
    version = result["version"]
    if identifier <> '':
      myRequest = "?Request="+request+"&identifier="+identifier+"&Service=WPS&Version="+version
    else:
      myRequest = "?Request="+request+"&Service=WPS&Version="+version
    
    myPath = path+myRequest
    self.verbindung = HTTPConnection(str(server))
    self.verbindung.request(str(method),str(myPath))
    result = self.verbindung.getresponse()
    return result.read()


  ##############################################################################

  def getCapabilities(self, connection):
    
    xmlString = self.getServiceXML(connection,"GetCapabilities")
    self.doc.setContent(xmlString,  True)  

    if self.getServiceVersion() != "1.0.0":
      QMessageBox.information(None, 'Error', 'Only WPS Version 1.0.0 is supprted')
      return 0
      
    version    = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Process")
    title      = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title")    
    identifier = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier")
    abstract   = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract")

    itemListAll = []
    
    for i in range(version.size()):
      v_element = version.at(i).toElement()
      i_element = identifier.at(i).toElement()
      t_element = title.at(i+1).toElement()
      a_element = abstract.at(i+1).toElement()                       

      itemList = []
      itemList.append(i_element.text()) 
      itemList.append(t_element.text()) 
      itemList.append(a_element.text()) 
#      print i_element.text()
      itemListAll.append(itemList)

    return itemListAll
    

  ##############################################################################

  def getServiceVersion(self):
    root = self.doc.documentElement()  
    version = root.attribute("version")
    return version

  ##############################################################################

  def getFileReference(self):
    pass

  ##############################################################################

  def getDefaultMimeType(self,  inElement):
    myElement = inElement.elementsByTagName("Default").at(0).toElement()
    return self._getMimeTypeSchemaEncoding(myElement)

  ##############################################################################

  def getSupportedMimeTypes(self,  inElement):
    mimeTypes = []
    myElements = inElement.elementsByTagName("Supported").at(0).toElement()
    myFormats = myElements.elementsByTagName('Format')
    for i in range(myFormats.size()):
      myElement = myFormats.at(i).toElement()
      mimeTypes.append(self._getMimeTypeSchemaEncoding(myElement))
    return mimeTypes

  ##############################################################################

  def _getMimeTypeSchemaEncoding(self,  Element):
    mimeType = ""
    schema = ""
    encoding = ""
    try:
        mimeType = str(Element.elementsByTagName("MimeType").at(0).toElement().text().simplified().toLower())
        schema = str(Element.elementsByTagName("Schema").at(0).toElement().text().simplified().toLower())
        encoding = str(Element.elementsByTagName("Encoding").at(0).toElement().text().simplified().toLower())
    except:
        pass
    
    return {"MimeType":mimeType,"Schema":schema,"Encoding":encoding}

  ##############################################################################

  def getIdentifierTitleAbstractFromElement(self, element):

      inputIdentifier = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
      title      = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()
      abstract   = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract").at(0).toElement().text().simplified()

      return inputIdentifier, title, abstract

  ##############################################################################

  def createTmpBase64(self,  layer):
    try:
        filename = tempfile.mktemp(prefix="base64")         
        rLayer = self.getVLayer(layer)
        infile = open(rLayer.source())
        outfile = open(filename, 'w')
        base64.encode(infile,outfile)
        outfile.close()
        outfile =  open(filename, 'r')
        base64String = outfile.read()
        os.remove(filename)
    except:
        QMessageBox.error(None, '', "Unable to create temporal file: " + filename + " for base64 encoding")  
    return base64String

  ##############################################################################

  def decodeBase64(self, infileName,  mimeType="image/tiff"):

#   This is till untested
#   TODO: test it
    try:
        # User project dir
        #filename = QFileDialog.getSaveFileName(None, "Chose filename for output file", "/home/soeren");
        filename = tempfile.mktemp(prefix="base64") 
        infile = open(infileName)
        outfile = open(filename, 'w')
        base64.decode(infile,outfile)
        infile.close()
        outfile.close()
    except:
        raise
 
    return filename

  ##############################################################################

  def createTmpGML(self, layer, processSelection="False"):
    myQTempFile = QTemporaryFile()
    myQTempFile.open()
    tmpFile = unicode(myQTempFile.fileName(),'latin1')
    
    vLayer = self.getVLayer(layer)    
    fieldList = self.getFieldList(vLayer)
    
    if vLayer.dataProvider().name() == "postgres":
      encoding = self.getDBEncoding(vLayer.dataProvider())
    else:
      encoding = vLayer.dataProvider().encoding()

    writer = self.createGMLFileWriter(tmpFile, fieldList, vLayer.dataProvider().geometryType(),encoding)

##    print "TEMP-GML-File Name: "+tmpFile    
    
    provider = vLayer.dataProvider()

    feat = QgsFeature()
    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)
    
    featureList = vLayer.selectedFeatures()
    
    if processSelection and vLayer.selectedFeatureCount() > 0:
      for feat in featureList:
        writer.addFeature(feat)
    else:
      while provider.nextFeature(feat):
        writer.addFeature(feat)

    del writer        
        
    myFile = QFile(tmpFile)
    if (not myFile.open(QIODevice.ReadOnly | QIODevice.Text)):
      pass    

    myGML = QTextStream(myFile)
    gmlString = ""
    
# Overread the first Line of GML Result    
    dummy = myGML.readLine()
    gmlString += myGML.readAll()
    myFile.close()
    myQTempFile.close()
    return gmlString.simplified()

  ##############################################################################
  
  def getVLayer(self,name):
  #   Die sichtbaren Layer der Legende zur weiteren Bearbeitung holen
        # get the map canvas
    mc=self.iface.mapCanvas()
        
     # how many layers are there?
    nLayers=mc.layerCount()

    for l in range(nLayers):
      layer = mc.layer(l)
      if layer.name() == name:
        return layer  

  ##############################################################################

  def getProviderName(self, name):
    mc=self.iface.mapCanvas()
        
     # how many layers are there?
    nLayers=mc.layerCount()

    for l in range(nLayers):
      layer = mc.layer(l)
      if layer.name() == name:    
       layerProvider = layer.dataProvider()
       providerName = layerProvider.name()    
    
    return providerName

  ##############################################################################

  def getTableName(self, name):
    #  Die sichtbaren Layer der Legende zur weiteren Bearbeitung holen
    # get the map canvas
    mc=self.iface.mapCanvas()
        
     # how many layers are there?
    nLayers=mc.layerCount()

    for l in range(nLayers):
      layer = mc.layer(l)
      if layer.name() == name:
        dataSource = QgsDataSourceURI(layer.dataProvider().dataSourceUri())
        theTableName = dataSource.quotedTablename()
        theTableName.replace('"','')
        return theTableName 

  ##############################################################################

  def getLayerSourceList(self):
    # get the map canvas
    mc=self.iface.mapCanvas()

    # how many layers are there?
    nLayers=mc.layerCount()

    # loopage:
    layerSourceList = []

    for l in range(nLayers):
       layer = mc.layer(l)
       layerSource = unicode(layer.publicSource(),'latin1').lower()
       layerSourceList.append(layerSource)

    return layerSourceList

  ##############################################################################

  def allowedValues(self, aValues):
     valList = []

     # Manage a value list defined by a range
     value_element = aValues.at(0).toElement()
     v_range_element = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Range")
     
     if v_range_element.size() > 0:
       min_val = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MinimumValue").at(0).toElement().text()
       max_val = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MaximumValue").at(0).toElement().text()
#       QMessageBox.information(None, '', min_val+' - '+max_val)
       for n in range(int(min_val),int(max_val)+1):
           myVal = QString()
           myVal.append(str(n))
           valList.append(myVal)

     # Manage a value list defined by single values
     v_element = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Value")
     if v_element.size() > 0:
       for n in range(v_element.size()):
         mv_element = v_element.at(n).toElement() 
         valList.append(unicode(mv_element.text(),'latin1').strip())
     return valList        

  ##############################################################################

  def errorHandler(self, resultXML):
     errorDoc = QtXml.QDomDocument()
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
         self.popUpMessageBox("WPS Error", resultXML)

  ##############################################################################

  # Creates a QgsVectorFileWriter for GML
  # Return: QgsVectorFileWriter
  def createGMLFileWriter(self, myTempFile, fields, geometryType, encoding):
    
    writer = QgsVectorFileWriter(myTempFile, encoding, fields, geometryType, None, "GML")
    if writer.hasError() != QgsVectorFileWriter.NoError:
      message = self.writerErrorMessage(writer.hasError())
      QMessageBox.warning(None, '', message)
      return 0
    return writer

  ##############################################################################

  # Get the List of Fields
  # Return: QGsFieldMap
  def getFieldList(self, vlayer):
    fProvider = vlayer.dataProvider()
    feat = QgsFeature()
    allAttrs = fProvider.attributeIndexes()


    # start data retrieval: all attributes for each feature
    fProvider.select(allAttrs, QgsRectangle(), False)

    # retrieve every feature with its attributes
    myFields = fProvider.fields()
      
    return myFields

  ##############################################################################

  # Get the Features of a vector Layer
  # Return: QgsFieldMap
  def getFeatureList(self, vlayer):
    provider = vlayer.dataProvider()

    feat = QgsFeature()
    allAttrs = provider.allAttributesList()
    provider.select(allAttrs)

    # retrieve every feature with its attributes
    myFields = provider.fields()
      
    return myFields

  ##############################################################################

  def uniqueLayerName(self, name):
    
    mapLayers = QgsMapLayerRegistry.instance().mapLayers()
    i=1
    layerNameList = []    
    for (k, layer) in mapLayers.iteritems():
      layerNameList.append(layer.name())
    
    layerNameList.sort()
    
    for layerName in layerNameList:
      if layerName == name+unicode(str(i),'latin1'):    
        i += 1
    
    newName = name+unicode(str(i),'latin1')
    return newName

  ##############################################################################

  def getLayerNameList(self, dataType=0, all=False):
    myLayerList = []    
        
    if all:
      mapLayers = QgsMapLayerRegistry.instance().mapLayers()      
      for (k, layer) in mapLayers.iteritems():
        myLayerList.append(layer.name())
    else:
      mc=self.iface.mapCanvas()
      nLayers=mc.layerCount()
      
      for l in range(nLayers):
        # Nur die Layer des gew�nschten Datentypes ausw�hlen 0=Vectorlayer 1=Rasterlayer
        if mc.layer(l).type() == dataType:
          myLayerList.append(mc.layer(l).name())
    
    return myLayerList

  ##############################################################################

  def getDBEncoding(self, layerProvider):
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

  ##############################################################################

  def popUpMessageBox(self, title, detailedText):
    """A message box used for debugging"""
    mbox = WPSMessageBox()
    mbox.setText(title)
    mbox.setDetailedText(detailedText)
    mbox.exec_()

  ##############################################################################

  def xmlExecuteRequestInputStart(self, identifier):
    string = ""
    string += "<wps:Input>\n"
    string += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"
    string += "<ows:Title>"+identifier+"</ows:Title>\n"
    string += "<wps:Data>\n"
    return string

  ##############################################################################

  def xmlExecuteRequestInputEnd(self):
    string = ""
    string += "</wps:Data>\n"
    string += "</wps:Input>\n"
    return string

  ############################################################################
  
  def isMimeTypeRaster(self, mimeType):
    """Check for raster input"""
    for rasterType in RASTER_MIMETYPES:
        if mimeType.upper() == rasterType["MIMETYPE"]:
          return rasterType["GDALID"]
    return None

  ############################################################################
  
  def isMimeTypeVector(self, mimeType):
    """Check for vector input. Zipped shapefiles must be extracted"""
    for vectorType in VECTOR_MIMETYPES:
        if mimeType.upper() == vectorType["MIMETYPE"]:
          return vectorType["GDALID"]
    return None

  ############################################################################
  
  def isMimeTypeText(self, mimeType):
    """Check for text file input"""
    if mimeType.upper() == "TEXT/PLAIN":
       return "TXT"
    else:
       return None
      


################################################################################
################################################################################
################################################################################

class WPSMessageBox(QMessageBox):
    """A resizable message box to show debug info"""
    def __init__(self):
        QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QMessageBox.event(self, e)

        self.setMinimumHeight(600)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(800)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(300)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(300)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result
        
