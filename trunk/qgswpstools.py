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

# Our main class for the plugin
class QgsWpsTools:
    
  def __init__(self, iface):
    self.iface = iface
    self.doc = QtXml.QDomDocument()

  def webConnectionExists(self, connection):
    try:
      xmlString = self.getServiceXML(connection,"GetCapabilities")
      return True
    except:
      QMessageBox.critical(None,'','Web Connection Failed')
      return False


# Gets Server and Connection Info from Stored Server Connections in QGIS Settings
# Param: String ConnectionName
# Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)            
  def getServer(self,name):
    settings = QSettings()
    mySettings = "/WPS/"+name
    scheme = settings.value(mySettings+"/scheme").toString()
    server = settings.value(mySettings+"/server").toString()
    path = settings.value(mySettings+"/path").toString()
    method = settings.value(mySettings+"/method").toString()
    version = settings.value(mySettings+"/version").toString()
    result = [scheme, server, path, method, version]
    return result    
    
# Gets Server and Connection Info from Stored Server Connections
# Param: String ConnectionName
# Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)              
  def getServiceXML(self, name, request, identifier=''):    
    result = self.getServer(name)
    path = result[2]
    server = result[1]
    method = result[3]
    version = result[4]
    if identifier <> '':
      myRequest = "?Request="+request+"&identifier="+identifier+"&Service=WPS&Version="+version
    else:
      myRequest = "?Request="+request+"&Service=WPS&Version="+version
    
    result = self.getServer(name)
    myPath = path+myRequest
    self.verbindung = HTTPConnection(str(server))
    self.verbindung.request(str(method),str(myPath))
    result = self.verbindung.getresponse()
    return result.read()

    
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
    

  def getServiceVersion(self):
    root = self.doc.documentElement()  
    version = root.attribute("version")
    return version

  def getFileReference(self):
    pass

  def getMimeType(self,  inElement,  elementNode="Default"):
    mimeType = ''
    if elementNode == "Default":
      myElement = inElement.elementsByTagName(elementNode).at(0).toElement()
      mimeType = myElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MimeType").at(0).toElement().text().simplified()
      if len(mimeType) == 0:
        mimeType = myElement.elementsByTagName("MimeType").at(0).toElement().text().simplified()
    else:
        myElements = inElement.elementsByTagName(elementNode).at(0).toElement()
        myFormats = myElements.elementsByTagName('Format')
        for i in range(myFormats.size()):
          myFormat = myFormats.at(i).toElement()
          myMimeType = myFormat.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MimeType").at(0).toElement().text().simplified()
          if len(myMimeType) == 0:
            mimeType += myFormat.elementsByTagName("MimeType").at(0).toElement().text().simplified()+', '
          else:
            mimeType += myFormat.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MimeType").at(0).toElement().text().simplified()
    print mimeType
    return mimeType.toLower()
    
  def createTmpBase64(self,  layer):
    myQTempFile = QTemporaryFile()
    myQTempFile.open()
    tmpFile = unicode(myQTempFile.fileName(),'latin1')

    rLayer = self.getVLayer(layer)    

    infile = open(rLayer.source())
    outfile = open(tmpFile+".base64","w")
    base64.encode(infile,outfile)
    myQTempFile.close()
    
    myFile = QFile(tmpFile+".base64")
    if (not myFile.open(QIODevice.ReadOnly | QIODevice.Text)):
      pass    

    line = myFile.readLine()
    base64String = line

    while not line.isNull():
      line = myFile.readLine()
      base64String += line

    myFile.close()
    myFile.remove()

    return base64String
    

  def decodeBase64(self, infileName,  mimeType="image/tiff"):
    myQTempFile = QTemporaryFile()
    myQTempFile.open()
    tmpFile = unicode(myQTempFile.fileName(),'latin1')
    tmpFileName = tmpFile+".tif"
    infile = open(infileName)
    outfile = open(tmpFileName, "w")    
    base64.decode(infile, outfile)
    infile.close()
    outfile.close()
    
    return tmpFileName

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

  def getTableName(self, name):
  #   Die sichtbaren Layer der Legende zur weiteren Bearbeitung holen
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

  def errorHandler(self, resultXML):
#     QMessageBox.information(None, 'Error', resultXML)
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

     #       QMessageBox.warning(None,'WPS Error',exceptionText)
     if len(exceptionText) > 0:
         flags = Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint
         msgBox = QMessageBox(None)
         msgBox.setMinimumSize(400, 400)
         msgBox.setText("WPS Error")
         msgBox.setInformativeText(exceptionText)
         msgBox.setDetailedText(resultXML)
         ret = msgBox.exec_()
    
#Creates a QgsVectorFileWriter for GML
#Return: QgsVectorFileWriter
  def createGMLFileWriter(self, myTempFile, fields, geometryType, encoding):
    
    writer = QgsVectorFileWriter(myTempFile, encoding, fields, geometryType, None, "GML")
    if writer.hasError() != QgsVectorFileWriter.NoError:
      message = self.writerErrorMessage(writer.hasError())
      QMessageBox.warning(None, '', message)
      return 0
    return writer

#Get the List of Fields
#Return: QGsFieldMap
  def getFieldList(self, vlayer):
    fProvider = vlayer.dataProvider()
    feat = QgsFeature()
    allAttrs = fProvider.attributeIndexes()


# start data retrieval: all attributes for each feature
    fProvider.select(allAttrs, QgsRectangle(), False)

# retrieve every feature with its attributes
    myFields = fProvider.fields()
      
    return myFields

#Get the Features of a vector Layer
#Return: QgsFieldMap       
  def getFeatureList(self, vlayer):
    provider = vlayer.dataProvider()

    feat = QgsFeature()
    allAttrs = provider.allAttributesList()
    provider.select(allAttrs)

# retrieve every feature with its attributes
    myFields = provider.fields()
      
    return myFields


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
##    print newName
    return newName

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
        # Nur die Layer des gewünschten Datentypes auswählen 0=Vectorlayer 1=Rasterlayer
        if mc.layer(l).type() == dataType:
          myLayerList.append(mc.layer(l).name())
    
    return myLayerList


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
