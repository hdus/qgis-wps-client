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
# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from PyQt4.QtSql import * 
from PyQt4.QtWebKit import QWebView
from qgis.core import *
import os, sys, string, tempfile, base64
from functools import partial

# initialize Qt resources from file resources.py
import resources_rc




DEBUG = False


# Main helper class, without GUI dependency
class QgsWpsTools(QObject):

  def __init__(self):
    QObject.__init__(self)
    self.doc = QtXml.QDomDocument()


##############################################################################

  def getProxy(self):
      settings = QSettings()
      mySettings = "/proxy"
      result = {}
      result["proxyEnabled"] = settings.value(mySettings+"/proxyEnabled").toString()
      result["proxyHost"] = settings.value(mySettings+"/proxyHost").toString()
      result["proxyPort"] = settings.value(mySettings+"/proxyPort").toString()
      result["proxyUser"] = settings.value(mySettings+"/proxyUser").toString()
      result["proxyPassword"] = settings.value(mySettings+"/proxyPassword").toString()
      result["proxyType"] = settings.value(mySettings+"/proxyType").toString()        
      result["proxyExcludedUrls"] = settings.value(mySettings+"/proxyExcludedUrls").toString()        

      return result


  ##############################################################################

  def webConnectionExists(self, connection):
    try:
      xmlString = self.getServiceXML(connection,"GetCapabilities")
      return True
    except:
      QMessageBox.critical(None,'',QApplication.translate("QgsWps","Web Connection Failed"))
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
    result["port"] =  settings.value(mySettings+"/port")
    result["path"] = settings.value(mySettings+"/path").toString()
    result["method"] = settings.value(mySettings+"/method").toString()
    result["version"] = settings.value(mySettings+"/version").toString()
    return result    


  @staticmethod
  def getBookmarks():
    settings = QSettings()
    settings.beginGroup("WPS-Bookmarks")
    bookmarks = settings.childGroups()
    itemList = []
    for myBookmark in bookmarks:
      settings = QSettings()
      myItem = {}

      mySettings = "/WPS-Bookmarks/"+myBookmark
      myItem['scheme'] = settings.value(mySettings+"/scheme").toString()
      myItem['server'] = settings.value(mySettings+"/server").toString()
      myItem['path'] = settings.value(mySettings+"/path").toString()
      myItem['port'] = settings.value(mySettings+"/port").toString()

      myBookmarkArray = myBookmark.split("@@")
      myItem['service'] = myBookmarkArray[0]
      myItem['version'] = settings.value(mySettings+"/version").toString()
      myItem['identifier'] = settings.value(mySettings+"/identifier").toString()
      itemList.append(myItem)
    #settings.endGroup()
    return itemList


  # Gets Server and Connection Info from Stored Server Connections
  # Param: String ConnectionName
  # Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)
  def getBookmarkXML(self, name):
    settings = QSettings()
    mySettings = "/WPS-Bookmarks/"+name
    scheme = settings.value(mySettings+"/scheme").toString()
    server = settings.value(mySettings+"/server").toString()
    path = settings.value(mySettings+"/path").toString()
    port =  settings.value(mySettings+"/port")
    identifier = settings.value(mySettings+"/identifier").toString()
    version = settings.value(mySettings+"/version").toString()    
    requestFinished = False
    self.myHttp = QgsNetworkAccessManager.instance()     

    url = QUrl()        
    myRequest = "?Request=DescribeProcess&identifier="+identifier+"&Service=WPS&Version="+version
    url.setUrl(scheme+"://"+server+path+myRequest)
    url.setPort(port)
    self.theReply = self.myHttp.get(QNetworkRequest(url))                        
    self.theReply.finished.connect(self.serviceRequestFinished)      
      
      
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
    scheme = result["scheme"]
    requestFinished = False
    self.myHttp = QgsNetworkAccessManager.instance()     

    if identifier <> '':
      url = QUrl()        
      myRequest = "?Request="+request+"&identifier="+identifier+"&Service=WPS&Version="+version
      url.setUrl(scheme+"://"+server+path+myRequest)
      self.theReply = self.myHttp.get(QNetworkRequest(url))                        
      self.theReply.finished.connect(self.serviceRequestFinished)      
    else:
      url = QUrl()        
      myRequest = "?Request="+request+"&Service=WPS&Version="+version
      url.setUrl(scheme+"://"+server+path+myRequest)
      self.theReply = self.myHttp.get(QNetworkRequest(url))      
      self.theReply.finished.connect(self.capabilitiesRequestFinished)

  def executeProcess(self, processUrl, postString, resultHandler):
    postData = QByteArray()
    postData.append(postString)

    scheme = processUrl.scheme()
    path = processUrl.path()
    server = processUrl.host()
    port = processUrl.port()

    wpsConnection = scheme+'://'+server+path

    thePostHttp = QgsNetworkAccessManager.instance()
    url = QUrl(wpsConnection)
    url.setPort(port)
    qDebug("Post URL=" + str(url))

#        thePostHttp.finished.connect(self.resultHandler)
    request = QNetworkRequest(url)
    request.setHeader( QNetworkRequest.ContentTypeHeader, "text/xml" )
    self.thePostReply = thePostHttp.post(request, postData)
    self.thePostReply.finished.connect(partial(resultHandler, self.thePostReply) )

  def capabilitiesRequestFinished(self):
#        self.myHttp.finished.disconnect(self.capabilitiesRequestFinished)      
        self.emit(SIGNAL("capabilitiesRequestIsFinished(QNetworkReply)"), self.theReply) 


  def serviceRequestFinished(self):
#        self.myHttp.finished.disconnect(self.serviceRequestFinished)      
        self.emit(SIGNAL("serviceRequestIsFinished(QNetworkReply)"), self.theReply) 

  ##############################################################################

  def parseCapabilitiesXML(self,  xmlString):    
    self.doc.setContent(xmlString,  True)  
    if self.getServiceVersion(self.doc) != "1.0.0":
      QMessageBox.information(None, QApplication.translate("QgsWps","Only WPS Version 1.0.0 is supported"), xmlString)
#      QMessageBox.information(None, QApplication.translate("QgsWps","Error"), QApplication.translate("QgsWps","Only WPS Version 1.0.0 is supprted"))
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

      itemListAll.append(itemList)

    return itemListAll


  ##############################################################################

  def getServiceVersion(self,  doc):
    root = doc.documentElement()  
    version = root.attribute("version")
    return version


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

  
################################################################################
################################################################################
################################################################################

# Helper class for native QGIS GUI
class QgsWpsGuiTools(QgsWpsTools):
  def __init__(self, iface,  dlg=None):
    QgsWpsTools.__init__(self)
    self.iface = iface
    self.dlg = dlg

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

  def popUpMessageBox(self, title, detailedText):
    """A message box used for debugging"""
    mbox = WPSMessageBox()
    mbox.setText(title)
    mbox.setDetailedText(detailedText)
    mbox.exec_()
    pass

  ##############################################################################

  def addComplexInputComboBox(self, title, name, mimeType, namesList, minOccurs,  dlgProcessScrollAreaWidget,  dlgProcessScrollAreaWidgetLayout):
      """Adds a combobox to select a raster or vector map as input to the process tab"""

      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
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

      myLabel = QLabel(dlgProcessScrollAreaWidget)
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

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return comboBox              


  ##############################################################################

  def addComplexOutputComboBox(self, widget, name, title, mimeType,  processIdentifier):
      """Adds a combobox to select a raster or vector map as input to the process tab"""

      groupbox = QGroupBox(widget)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      namesList = []
      # Generate a unique name for the layer
      namesList.append(self.uniqueLayerName(processIdentifier + "_" + name + "_"))
      namesList.append("<None>")

      comboBox = QComboBox(groupbox)
      comboBox.setEditable(True)
      comboBox.addItems(namesList)
      comboBox.setObjectName(name)
      comboBox.setMinimumWidth(250)
      comboBox.setMaximumWidth(250)
      comboBox.setMinimumHeight(25)
      comboBox.setEditable(False)

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

  def addComplexInputListWidget(self, title, name, mimeType, namesList, minOccurs, dlgProcessScrollAreaWidget,  dlgProcessScrollAreaWidgetLayout):
      """Adds a widget for multiple raster or vector selections as inputs to the process tab"""
      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
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

      myLabel = QLabel(dlgProcessScrollAreaWidget)
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

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return listWidget

  ##############################################################################

  def addComplexInputTextBox(self, title, name, minOccurs,  dlgProcessScrollAreaWidget, dlgProcessScrollAreaWidgetLayout, mimeType=None):
      """Adds a widget to insert text as complex inputs to the process tab"""
      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(50)
      layout = QHBoxLayout()

      textBox = QTextEdit(groupbox)
      textBox.setObjectName(name)
      textBox.setMinimumWidth(200)
      textBox.setMaximumWidth(200)
      textBox.setMinimumHeight(50)

      myLabel = QLabel(dlgProcessScrollAreaWidget)
      myLabel.setObjectName("qLabel"+name)

      if minOccurs > 0:
        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Red'>" + string + "</font>" + ((" <br>(" + mimeType + ")") if mimeType else ""))
      else:
        string = "[" + name + "]\n" + title + ((" <br>(" + mimeType + ")") if mimeType else "")
        myLabel.setText(string)

      myLabel.setWordWrap(True)
      myLabel.setMinimumWidth(400)
      myLabel.setMinimumHeight(25)

      layout.addWidget(myLabel)
      layout.addStretch(1)
      layout.addWidget(textBox)

      groupbox.setLayout(layout)

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return textBox

  ##############################################################################

  def addLiteralComboBox(self, title, name, namesList, minOccurs,  dlgProcessScrollAreaWidget,  dlgProcessScrollAreaWidgetLayout):

      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
      #groupbox.setTitle(name)
      groupbox.setMinimumHeight(25)
      layout = QHBoxLayout()

      comboBox = QComboBox(dlgProcessScrollAreaWidget)
      comboBox.addItems(namesList)
      comboBox.setObjectName(name)
      comboBox.setMinimumWidth(179)
      comboBox.setMaximumWidth(179)
      comboBox.setMinimumHeight(25)

      myLabel = QLabel(dlgProcessScrollAreaWidget)
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

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return comboBox

  ##############################################################################

  def addLiteralLineEdit(self, title, name, minOccurs, dlgProcessScrollAreaWidget,  dlgProcessScrollAreaWidgetLayout,  defaultValue=""):

      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
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

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

      return myLineEdit


  ##############################################################################

  def addCheckBox(self,  title,  name,  dlgProcessScrollAreaWidget,  dlgProcessScrollAreaWidgetLayout):

      groupbox = QGroupBox(dlgProcessScrollAreaWidget)
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

      dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)


  def addDocumentationTab(self, dlgProcessTab,  abstract):
    # Check for URL
    if str(abstract).find("http://") == 0:
      textBox = QWebView(dlgProcessTab)
      textBox.load(QUrl(abstract))
      textBox.show()
    else:
      textBox = QTextBrowser(dlgProcessTab)
      textBox.setText(QString(abstract))

    dlgProcessTab.addTab(textBox, "Documentation")


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

