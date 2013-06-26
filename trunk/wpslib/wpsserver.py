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
from PyQt4.QtNetwork import *
from PyQt4.QtGui import QApplication,QMessageBox
from PyQt4 import QtXml
from qgis.core import QgsNetworkAccessManager


class WpsServer(QObject):

    def __init__(self, connectionName, server, baseUrl, version):
        QObject.__init__(self)
        self.connectionName = connectionName
        self.server = server
        self.baseUrl = baseUrl
        self.version = version
        self.processes = []

    @staticmethod
    def getServers():
        settingsgrp = QSettings()
        settingsgrp.beginGroup("WPS")
        connections = settingsgrp.childGroups()
        servers = []
        for connectionName in connections:
            settings = QSettings()
            entry = "/WPS/"+connectionName
            scheme = settings.value(entry+"/scheme").toString()
            server = settings.value(entry+"/server").toString()
            port =  settings.value(entry+"/port")
            path = settings.value(entry+"/path").toString()
            #method = settings.value(entry+"/method").toString()
            version = settings.value(entry+"/version").toString()
            url = settings.value(entry+"/url").toString()

            baseUrl = scheme+"://"+server+path
            server = WpsServer(connectionName, server, baseUrl, version)
            servers.append(server)
        settingsgrp.endGroup()
        return servers

    # Gets Server and Connection Info from Stored Server Connections in QGIS Settings
    # Param: String ConnectionName
    @staticmethod
    def getServer(connectionName):
        settings = QSettings()
        mySettings = "/WPS/"+connectionName
        scheme = settings.value(mySettings+"/scheme").toString()
        server = settings.value(mySettings+"/server").toString()
        port =  settings.value(mySettings+"/port")
        path = settings.value(mySettings+"/path").toString()
        #method = settings.value(mySettings+"/method").toString()
        version = settings.value(mySettings+"/version").toString()
        url = settings.value(mySettings+"/url").toString()
  
        if url == '':
            baseUrl = scheme+"://"+server+path
        else:
            baseUrl = url
        return WpsServer(connectionName, server, baseUrl, version)

    def processDescriptionFolder(self, basePath):
        return basePath + '/' + str(self.connectionName)

    def requestCapabilities(self):
        """
        Request server capabilities
        """
        self.doc = None
        url = QUrl()
        
        if self.baseUrl.contains('?'):
            myRequest = "&Request=GetCapabilities&identifier=&Service=WPS&Version=" + self.version
        else:    
            myRequest = "?Request=GetCapabilities&identifier=&Service=WPS&Version=" + self.version
            
        url.setUrl(self.baseUrl + myRequest)
        myHttp = QgsNetworkAccessManager.instance()
        self._theReply = myHttp.get(QNetworkRequest(url))
        self._theReply.finished.connect(self._capabilitiesRequestFinished)

    @pyqtSlot()
    def _capabilitiesRequestFinished(self):
        # Receive the server capabilities XML
        if self._theReply.error() == 1:
            QMessageBox.information(None, '', QApplication.translate("QgsWpsGui","Connection Refused. Please check your Proxy-Settings"))
            pass

        xmlString = self._theReply.readAll().data()
        self.doc = QtXml.QDomDocument()
        self.doc.setContent(xmlString,  True)

        root = self.doc.documentElement()  
        version = root.attribute("version")
        if version != "1.0.0":
            QMessageBox.information(None, QApplication.translate("QgsWps","Only WPS Version 1.0.0 is supported"), xmlString)
            pass
        self.emit(SIGNAL("capabilitiesRequestFinished"))

    def parseCapabilitiesXML(self):
        from wps.wpslib.processdescription import ProcessDescription
        version    = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Process")
        title      = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title")    
        identifier = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier")
        abstract   = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract")
    
        self.processes = []
        itemListAll = [] #Text array for list view
    
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

          self.processes.append(ProcessDescription(self, str(i_element.text())))
          itemListAll.append(itemList)
    
        return itemListAll
