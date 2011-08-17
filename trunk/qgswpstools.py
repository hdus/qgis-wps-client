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
import resources_rc


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

DEBUG = False

# Our help class for the plugin
class QgsWpsTools:
    
  def __init__(self, iface,  dlg=None):
    self.iface = iface
    self.doc = QtXml.QDomDocument()
    self.dlg = dlg

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
    
    for i in range(identifier.size()):
      v_element = version.at(i).toElement()
      i_element = identifier.at(i).toElement()
      t_element = title.at(i+1).toElement()
      a_element = abstract.at(i+1).toElement()                       

      itemList = []
      itemList.append(i_element.text()) 
      itemList.append(t_element.text()) 
      if "*"+a_element.text()+"*"== "**":
         itemList.append("*")
      else:
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
    tmpFile = unicode(myQTempFile.fileName()+".gml",'latin1')
    
    vLayer = self.getVLayer(layer)    
    fieldList = self.getFieldList(vLayer)
    
    if vLayer.dataProvider().name() == "postgres":
      encoding = self.getDBEncoding(vLayer.dataProvider())
    else:
      encoding = vLayer.dataProvider().encoding()

    writer = self.createGMLFileWriter(tmpFile, fieldList, vLayer.dataProvider().geometryType(), vLayer.dataProvider().crs(),  encoding)
    
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

    
    myQTempFile.close()

    myFile = QFile(tmpFile)
    if (not myFile.open(QIODevice.ReadOnly | QIODevice.Text)):
      QMessageBox.information(None, '', 'File open problem')
      pass    

    myGML = QTextStream(myFile)
    gmlString = ""
# Overread the first Line of GML Result    
    dummy = myGML.readLine()
    gmlString += myGML.readAll()
    myFile.close()
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
         
#     print str(valList)
     return valList        

  ##############################################################################

  def errorHandler(self, resultXML):
     errorDoc = QtXml.QDomDocument()
     myResult = errorDoc.setContent(resultXML.simplified(), True)
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
         pass

  ##############################################################################

  # Creates a QgsVectorFileWriter for GML
  # Return: QgsVectorFileWriter
  def createGMLFileWriter(self, myTempFile, fields, geometryType, crs,  encoding):
    writer = QgsVectorFileWriter(myTempFile, encoding, fields, geometryType, crs, "GML")
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
    pass

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
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>" + " <br>(" + mimeType + ")")
      else:
        string = "[" + name + "]\n" + title + " <br>(" + mimeType + ")"
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
      namesList.append(self.uniqueLayerName(self.processIdentifier + "_" + name + "_"))
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

      string = "[" + name + "] <br>" + title
      myLabel.setText("<font color='Green'>" + string + "</font>" + " <br>(" + mimeType + ")")

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
      """Adds a widget for multiple raster or vector selections as inputs to the process tab"""
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
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>" + " <br>(" + mimeType + ")")
      else:
        string = "[" + name + "]\n" + title + " <br>(" + mimeType + ")"
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
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "[" + name + "]\n" + title
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
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "[" + name + "]\n" + title
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

  def addLiteralLineEdit(self, title, name, minOccurs, defaultValue=""):

      groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      myLineEdit = QLineEdit(groupbox)
      myLineEdit.setObjectName(name)
      myLineEdit.setMinimumWidth(179)
      myLineEdit.setMaximumWidth(179)
      myLineEdit.setMinimumHeight(25)
      myLineEdit.setText(defaultValue)
      
      myLabel = QLabel(groupbox)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>")
      else:
        string = "[" + name + "]\n" + title
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

    groupBox = QFrame()
    layout = QHBoxLayout()

    btnOk = QPushButton(groupBox)
    btnOk.setText(QString("Run"))
    btnOk.setMinimumWidth(100)
    btnOk.setMaximumWidth(100)

    btnCancel = QPushButton(groupBox)
    btnCancel.setText("Back")
    btnCancel.setMinimumWidth(100)
    btnCancel.setMaximumWidth(100)

    layout.addStretch(10)
    layout.addWidget(btnCancel)
    layout.addWidget(btnOk)
    
    groupBox.setLayout(layout)
    self.dlgProcessTabFrameLayout.addWidget(groupBox)

    QObject.connect(btnOk,SIGNAL("clicked()"),self.defineProcess)
    QObject.connect(btnCancel,SIGNAL("clicked()"),self.dlgProcess.close)


##############################################################################

  def generateProcessInputsGUI(self, DataInputs):
    """Generate the GUI for all Inputs defined in the process description XML file"""

    # Create the complex inputs at first
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

      complexData = f_element.elementsByTagName("ComplexData")
      minOccurs = int(f_element.attribute("minOccurs"))
      maxOccurs = int(f_element.attribute("maxOccurs"))

      # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
      if complexData.size() > 0:
        # Das i-te ComplexData Objekt auswerten
        complexDataTypeElement = complexData.at(0).toElement()
        complexDataFormat = self.getDefaultMimeType(complexDataTypeElement)
        supportedComplexDataFormat = self.getSupportedMimeTypes(complexDataTypeElement)

        # Store the input formats
        self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
        self.inputDataTypeList[inputIdentifier] = complexDataFormat

        # Attach the selected vector or raster maps
        if self.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
          # Vector inputs
          layerNamesList = self.getLayerNameList(0)
          if maxOccurs == 1:
            self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
          else:
            self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        elif self.isMimeTypeText(complexDataFormat["MimeType"]) != None:
          # Text inputs
          self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))
        elif self.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:
          # Raster inputs
          layerNamesList = self.getLayerNameList(1)
          if maxOccurs == 1:
            self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
          else:
            self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        else:
          # We assume text inputs in case of an unknown mime type
          self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))            

    # Create the literal inputs as second
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

      literalData = f_element.elementsByTagName("LiteralData")
      minOccurs = int(f_element.attribute("minOccurs"))
      maxOccurs = int(f_element.attribute("maxOccurs"))

      if literalData.size() > 0:
        allowedValuesElement = literalData.at(0).toElement()
        aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
        dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
#        print "Checking allowed values " + str(aValues.size())
        if aValues.size() > 0:
          valList = self.allowedValues(aValues)
          if len(valList) > 0:
            if len(valList[0]) > 0:
              self.literalInputComboBoxList.append(self.addLiteralComboBox(title, inputIdentifier, valList, minOccurs))
            else:
              self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, str(valList)))
        else:
          self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, dValue))

    # At last, create the bounding box inputs
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()

      inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
      
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

      outputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
      complexOutput = f_element.elementsByTagName("ComplexOutput")

      # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
      if complexOutput.size() > 0:
        # Das i-te ComplexData Objekt auswerten
        complexOutputTypeElement = complexOutput.at(0).toElement()
        complexOutputFormat = self.getDefaultMimeType(complexOutputTypeElement)
        supportedcomplexOutputFormat = self.getSupportedMimeTypes(complexOutputTypeElement)

        # Store the input formats
        self.outputsMetaInfo[outputIdentifier] = supportedcomplexOutputFormat
        self.outputDataTypeList[outputIdentifier] = complexOutputFormat
        
        widget, comboBox = self.addComplexOutputComboBox(groupbox, outputIdentifier, title, str(complexOutputFormat))
        self.complexOutputComboBoxList.append(comboBox)
        layout.addWidget(widget)
    
    # Set the layout
    groupbox.setLayout(layout)
    # Add the outputs
    self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
    

    
    
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
    info = self.getServer(name)
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgEdit = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgEdit.txtName.setText(name)
    dlgEdit.txtUrl.setText(info["scheme"]+"://"+info["server"]+info["path"])
    dlgEdit.show()
    self.dlg.initQgsWpsGui()     
    


  ##############################################################################

  def resultHandler(self, resultXML,  resultType="store"):
    """Handle the result of the WPS Execute request and add the outputs as new
       map layers to the regestry or open an information window to show literal
       outputs."""
# This is for debug purpose only
    if DEBUG == True:
        self.popUpMessageBox("Result XML", resultXML)
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
              QMessageBox.warning(None, '', str(QCoreApplication.translate("WPS Error: Unable to download the result of reference: ")) + str(fileLink))
              return

            # Get the mime type of the result
            mimeType = str(reference.attribute("mimeType", "0").toLower())

            if fileLink != '0':                            
              # Set a valid layerName
              layerName = self.uniqueLayerName(self.processIdentifier + "_" + identifier)
              # The layername is normally defined in the comboBox
              for comboBox in self.complexOutputComboBoxList:
                if comboBox.objectName() == identifier:
                  layerName = comboBox.currentText()

              resultFileConnector = urllib.urlretrieve(unicode(fileLink,'latin1'))
              resultFile = resultFileConnector[0]
              # Vector data 
              # TODO: Check for schema GML and KML
              if self.isMimeTypeVector(mimeType) != None:
                vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
                vlayer.setCrs(self.myLayer.dataProvider().crs())
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
              # Raster data
              elif self.isMimeTypeRaster(mimeType) != None:
                # We can directly attach the new layer
                rLayer = QgsRasterLayer(resultFile, layerName)
                QgsMapLayerRegistry.instance().addMapLayer(rLayer)
              # Text data
              elif self.isMimeTypeText(mimeType) != None:
                #TODO: this should be handled in a separate diaqgswps.pylog to save the text output as file'
                QApplication.restoreOverrideCursor()
                text = open(resultFile, 'r').read()
                # TODO: This should be a text dialog with safe option
                self.popUpMessageBox(QCoreApplication.translate("QgsWps",'Process result (text/plain)'),text)
              # Everything else
              else:
                # For unsupported mime types we assume text
                QApplication.restoreOverrideCursor()
                content = open(resultFile, 'r').read()
                # TODO: This should have a safe option
                self.popUpMessageBox(QCoreApplication.translate("QgsWps", 'Process result (unsupported mime type)'), content)
                
          elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
            QApplication.restoreOverrideCursor()
            literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
            self.popUpMessageBox(QCoreApplication.translate("QgsWps",'Result'),literalText)
          else:
            QMessageBox.warning(None, '', str(QCoreApplication.translate("WPS Error: Missing reference or literal data in response")))
    else:
        print "Error"
        self.errorHandler(resultXML)

    pass
    
    
  ##############################################################################

  def newServer(self):
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgNew = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgNew.show()
    self.dlg.initQgsWpsGui()
    


  ##############################################################################  
  def defineProcess(self):
    """Create the execute request"""
    self.doc.setContent(self.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier))
    dataInputs = self.doc.elementsByTagName("Input")
    dataOutputs = self.doc.elementsByTagName("Output")

    QApplication.setOverrideCursor(Qt.WaitCursor)
    result = self.getServer(self.processName)
    scheme = result["scheme"]
    path = result["path"]
    server = result["server"]

    checkBoxes = self.dlgProcess.findChildren(QCheckBox)

    if len(checkBoxes) > 0:
      useSelected = checkBoxes[0].isChecked()

    postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
    postString += "<wps:Execute service=\"WPS\" version=\""+ self.getServiceVersion() + "\"" + \
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

      postString += self.xmlExecuteRequestInputStart(textBox.objectName())
      postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
      postString += self.xmlExecuteRequestInputEnd()


    # Single raster and vector inputs ##########################################
    for comboBox in self.complexInputComboBoxList:
      # Do not add undefined inputs
      if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
        continue
           
      postString += self.xmlExecuteRequestInputStart(comboBox.objectName())

      # TODO: Check for more types
      mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
      schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
      encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]
      self.myLayer = self.getVLayer(comboBox.currentText())
      
      if self.isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
        postString += self.createTmpGML(comboBox.currentText(), useSelected).replace("> <","><")
        postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", "xsi:schemaLocation=\"http://schemas.opengis.net/gml/3.1.1/base/ gml.xsd\"")
      elif self.isMimeTypeVector(mimeType) != None or self.isMimeTypeRaster(mimeType) != None:
        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
        postString += self.createTmpBase64(comboBox.currentText())

      postString += "</wps:ComplexData>\n"
      postString += self.xmlExecuteRequestInputEnd()

    # Multiple raster and vector inputs ########################################
    for listWidgets in self.complexInputListWidgetList:
      # Do not add undefined inputs
      if listWidgets == None:
        continue
        
      mimeType = self.inputDataTypeList[listWidgets.objectName()]["MimeType"]
      schema = self.inputDataTypeList[listWidgets.objectName()]["Schema"]
      encoding = self.inputDataTypeList[listWidgets.objectName()]["Encoding"]
      
      # Iterate over each seletced item
      for i in range(listWidgets.count()):
        listWidget = listWidgets.item(i)
        if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
          continue
          
        postString += self.xmlExecuteRequestInputStart(listWidgets.objectName())

        # TODO: Check for more types
        if self.isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
          postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
#          postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <","><").replace("http://ogr.maptools.org/ qt_temp.xsd","http://ogr.maptools.org/qt_temp.xsd")
          postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <","><")
        elif self.isMimeTypeVector(mimeType) != None or self.isMimeTypeRaster(mimeType) != None:
          postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
          postString += self.createTmpBase64(listWidget.text())

        postString += "</wps:ComplexData>\n"
        postString += self.xmlExecuteRequestInputEnd()

    # Literal data as combo box choice #########################################
    for comboBox in self.literalInputComboBoxList:
      if comboBox == None or comboBox.currentText() == "":
          continue

      postString += self.xmlExecuteRequestInputStart(comboBox.objectName())
      postString += "<wps:LiteralData>"+comboBox.currentText()+"</wps:LiteralData>\n"
      postString += self.xmlExecuteRequestInputEnd()

   # Literal data as combo box choice #########################################
    for lineEdit in self.literalInputLineEditList:
      if lineEdit == None or lineEdit.text() == "":
          continue

      postString += self.xmlExecuteRequestInputStart(lineEdit.objectName())
      postString += "<wps:LiteralData>"+lineEdit.text()+"</wps:LiteralData>\n"
      postString += self.xmlExecuteRequestInputEnd()

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
        
        mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
        schema = self.outputDataTypeList[outputIdentifier]["Schema"]
        encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]
        
        postString += "<wps:Output asReference=\"true\" mimeType=\"" + mimeType + "\" schema=\"" + schema + "\">"
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
    QApplication .setOverrideCursor(Qt.ArrowCursor)
    
    self.theThread.setScheme(scheme)
    self.theThread.setServer(server)
    self.theThread.setPath(path)
    self.theThread.setPostString(postString)
    
    self.theThread.start()          
     
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
        
