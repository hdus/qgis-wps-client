# -*- coding: latin1 -*-
# /***************************************************************************
#   qgswps.py QGIS Web Processing Service Plugin
#  -------------------------------------------------------------------
# Date                 : 09 November 2009
# Copyright            : (C) 2009 by Dr. Horst Duester
# email                : horst dot duester at bd dot so dot ch
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
from qgis.core import *
from qgswpstools import QgsWpsTools
from qgswpsgui import QgsWpsGui
from qgswpsdescribeprocessgui import QgsWpsDescribeProcessGui
from qgsnewhttpconnectionbasegui import QgsNewHttpConnectionBaseGui
from httplib import *
from urlparse import urlparse
import os, sys, string, tempfile, urllib2, urllib,  mimetypes

# initialize Qt resources from file resources.py
import resources

# Our main class for the plugin
class QgsWps:
  MSG_BOX_TITLE = "WPS Client"
  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface  
    self.minimumRevision = 12026
        

  def initGui(self):
    
    qgsRevision = QGis.QGIS_SVN_VERSION[0:5]
    
    versionMessage = unicode("Quantum GIS revision detected: "+str(qgsRevision)+"\n"
                    +"WPS-Client plugin requires Revision at least "+str(self.minimumRevision)+"!\n"
                    +"Plugin not loaded.",'latin1')       
                                                                    
#    if int(qgsRevision) < int(self.minimumRevision):
#        QMessageBox.warning(None, "Version", versionMessage)
#        return 1
                                                                     
  # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/wps/images/wps-add.png"), "WPS Client", self.iface.mainWindow())
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)

    
    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("WPS", self.action)
    
    self.doc = QtXml.QDomDocument()
    self.tmpPath = QDir.tempPath()
    
    self.tools = QgsWpsTools(self.iface)
    
  def unload(self):
    self.iface.removePluginMenu("WPS", self.action)
    self.iface.removeToolBarIcon(self.action)
    
  def run(self):  
       
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
 
    self.dlg = QgsWpsGui(self.iface.mainWindow(),  flags)    
    QObject.connect(self.dlg, SIGNAL("getDescription(QString, QTreeWidgetItem)"), self.createProcessGUI)    
    QObject.connect(self.dlg, SIGNAL("newServer()"), self.newServer)    
    QObject.connect(self.dlg, SIGNAL("editServer(QString)"), self.editServer)    
    QObject.connect(self.dlg, SIGNAL("deleteServer(QString)"), self.deleteServer)        
    QObject.connect(self.dlg, SIGNAL("connectServer(QString)"), self.createCapabiliesGUI)    

    self.dlg.initQgsWpsGui()
    self.dlg.show()

  def newServer(self):
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgNew = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgNew.show()
    self.dlg.initQgsWpsGui()
    
  def editServer(self, name):
    info = self.tools.getServer(name)
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    dlgEdit = QgsNewHttpConnectionBaseGui(self.dlg,  flags)  
    dlgEdit.txtName.setText(name)
    dlgEdit.txtUrl.setText(info[0]+"://"+info[1]+info[2])
#    dlgEdit.txtVersion.setText(info[4])
    dlgEdit.show()
    self.dlg.initQgsWpsGui()    
    
  def deleteServer(self,  name):
    settings = QSettings()
    settings.beginGroup("WPS")
    settings.remove(name)
    settings.endGroup()
    self.dlg.initQgsWpsGui() 



  def createCapabiliesGUI(self, connection):
    if not self.tools.webConnectionExists(connection):
        return 0
        
    itemListAll = self.tools.getCapabilities(connection)
    
#    QMessageBox.information(None, '', itemListAll)
    self.dlg.initTreeWPSServices(itemListAll)
      
  def createProcessGUI(self,name,  item):
    try:
      self.processIdentifier = item.text(0)
    except:
      QMessageBox.warning(None,'','Please select a Process')
      return 0
    self.processName = name
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    self.doc.setContent(self.tools.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier), True)     
    DataInputs = self.doc.elementsByTagName("Input")
    DataOutputs = self.doc.elementsByTagName("Output")
    self.dlgProcess = QgsWpsDescribeProcessGui(self.dlg, flags) 
    
    wVdist = 30   
    
    self.complexComboBoxList = []
    self.valueComboBoxList = []    
    self.dataTypeList = []

    # If no Input Data  are requested
    if DataInputs.size()==0:
      self.startProcess()
      return 0
    
    wHdist = self.getObjectSpace(DataInputs)      
    
    for i in range(DataInputs.size()):
      f_element = DataInputs.at(i).toElement()
      
      self.processDataIdentifier = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
      title      = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()
      abstract   = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract").at(0).toElement().text().simplified()
      complexData = f_element.elementsByTagName("ComplexData")
      literalData = f_element.elementsByTagName("LiteralData")
      bBoxData = f_element.elementsByTagName("BoundingBoxData")
      
# Durch alle ComplexDataTypes gehen und die entsprechenden Comboboxen aufbauen    
      if complexData.size() > 0:
        # Das i-te ComplexData Objekt auswerten
        complexDataTypeElement = complexData.at(0).toElement()
        complexDataFormat = self.tools.getMimeType(complexDataTypeElement,  'Default')
        supportedComplexDataFormat = self.tools.getMimeType(complexDataTypeElement, 'Supported')
##        QMessageBox.information(None,'',supportedComplexDataFormat)
        
# Wenn Das complexDataFormat leer ist wird default text/xml angenommen
#   Die sichtbaren Layer der Legende zur weiteren Bearbeitung holen
        if complexDataFormat == "" or complexDataFormat.toLower() == "text/xml":
          layerNamesList = self.tools.getLayerNameList(0)
        else:
          layerNamesList = self.tools.getLayerNameList(1)
#          QMessageBox.warning(None,'','Unfortunately rasterdata support is not available yet :-((')
          pass
        
        self.dataTypeList.append(complexDataFormat)
        self.complexComboBoxList.append(self.addComplexComboBox(title, self.processDataIdentifier, complexDataFormat,  wVdist, wHdist, layerNamesList, i))
        wVdist = int(wVdist) + int(50)

      if literalData.size() > 0:
        allowedValuesElement = literalData.at(0).toElement()
        aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
        if aValues.size() > 0:
          valList = self.tools.allowedValues(aValues)         
          if len(valList) > 0:
            if len(valList[0]) > 0:
              self.valueComboBoxList.append(self.addValueComboBox(title, self.processDataIdentifier, wVdist, wHdist, valList, i))
            else:
              self.addLineEdit(title, self.processDataIdentifier, wVdist, wHdist,  i)
        else:
          self.addLineEdit(title, self.processDataIdentifier, wVdist, wHdist,  i)
        
        wVdist = int(wVdist) + int(50)              
        
      if bBoxData.size() > 0:
        crsListe = []
        bBoxElement = bBoxData.at(0).toElement()
        defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
        defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href")
        crsListe.append(defaultCrs)
        self.addLineEdit(title+"(minx,miny,maxx,maxy)", self.processDataIdentifier, wVdist, wHdist, i)
        wVdist = int(wVdist) + int(50)              
        
        supportedCrsElements = bBoxElement.elementsByTagName("Supported")
        
        for i in range(supportedCrsElements.size()):
          crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))
        
        self.valueComboBoxList.append(self.addValueComboBox("Supported CRS", self.processDataIdentifier, wVdist, wHdist, crsListe, i))
        
        wVdist = int(wVdist) + int(50)   
        
    
    self.addCheckBox("Only process selected objects", "Selected" ,  wVdist,  wHdist)

# Formulieren der GUI Objekte fuer das OUTPUT-Handling
    for i in range(DataOutputs.size()):
      f_element = DataOutputs.at(i).toElement()
      
      self.processOutDataIdentifier = unicode(f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text(),'latin1').strip()
      title      = unicode(f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text(),'latin1').strip()
      abstract   = unicode(f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract").at(0).toElement().text(),'latin1').strip()

#      complexData = f_element.elementsByTagName("ComplexData")
      literalData = f_element.elementsByTagName("LiteralData")
      allowedValues = f_element.elementsByTagName("AllowedValues")       
      complexOutput = f_element.elementsByTagName("ComplexOutput")
      wVdist = int(wVdist) + int(50)
    
    btnOk = QPushButton(self.dlgProcess)
    btnOk.setGeometry(QRect(20,wVdist+50,100,27))
    btnOk.setText("OK")
    
    btnAbbrechen = QPushButton(self.dlgProcess)
    btnAbbrechen.setGeometry(QRect(125,wVdist+50,100,27))
    btnAbbrechen.setText("abbrechen")

    QObject.connect(btnOk,SIGNAL("clicked()"),self.startProcess)
    QObject.connect(btnAbbrechen,SIGNAL("clicked()"),self.dlgProcess.close)        
    
    self.dlgProcess.setGeometry(QRect(190,100,600,wVdist+100))   
    self.dlgProcess.show()
         
       
  def startProcess(self):
    self.doc.setContent(self.tools.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier))     
    dataInputs = self.doc.elementsByTagName("Input")
    dataOutputs = self.doc.elementsByTagName("Output")
    
    QApplication.setOverrideCursor(Qt.WaitCursor)    
    result = self.tools.getServer(self.processName)
    protocol = result[0]
    path = result[2]
    server = result[1]
    method = result[3]
    version = result[4]
    inputString = ""
#    comboBoxes = self.dlgProcess.findChildren(QComboBox)
    lineEdits  = self.dlgProcess.findChildren(QLineEdit)
    checkBoxes = self.dlgProcess.findChildren(QCheckBox)
    
    if len(checkBoxes) > 0:
      useSelected = checkBoxes[0].isChecked()
    
    postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
    postString += "<wps:Execute service=\"WPS\" version=\""+self.tools.getServiceVersion()+"\" xmlns:wps=\"http://www.opengis.net/wps/1.0.0\" xmlns:ows=\"http://www.opengis.net/ows/1.1\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">\n"
    postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
    postString += "<wps:DataInputs>"
    
    for i in range(len(self.complexComboBoxList)):
       postString += "<wps:Input>\n"
       postString += "<ows:Identifier>"+self.complexComboBoxList[i].objectName()+"</ows:Identifier>\n"
       postString += "<ows:Title>"+self.complexComboBoxList[i].objectName()+"</ows:Title>\n"
       postString += "<wps:Data>\n"
       if self.dataTypeList[i] == "text/xml":
         postString += "<wps:ComplexData>\n"
         postString += self.tools.createTmpGML(self.complexComboBoxList[i].currentText(), useSelected).replace('"','\"').replace("\n","")
       else:
         postString += "<wps:ComplexData>"
         postString += self.tools.createTmpBase64(self.complexComboBoxList[i].currentText()).replace('"','\"').replace("\n","")
       postString += "</wps:ComplexData>\n"  
       postString += "</wps:Data>\n"  
       postString += "</wps:Input>\n"
    
    for i in range(len(self.valueComboBoxList)):
       postString += "<wps:Input>\n"
       postString += "<ows:Identifier>"+self.valueComboBoxList[i].objectName()+"</ows:Identifier>\n"
       postString += "<ows:Title>"+self.valueComboBoxList[i].objectName()+"</ows:Title>\n"
       postString += "<wps:Data>\n"
       postString += "<wps:LiteralData>"+self.valueComboBoxList[i].currentText()+"</wps:LiteralData>\n"
       postString += "</wps:Data>\n"
       postString += "</wps:Input>\n"
      
    for i in range(len(lineEdits)):
      postString += "<wps:Input>\n"
      postString += "<ows:Identifier>"+lineEdits[i].objectName()+"</ows:Identifier>\n"
      postString += "<ows:Title>"+lineEdits[i].objectName()+"</ows:Title>\n"
      postString += "<wps:Data>\n"
      postString += "<wps:LiteralData>"+lineEdits[i].text()+"</wps:LiteralData>\n"
      postString += "</wps:Data>\n"
      postString += "</wps:Input>\n"
    
    postString += "</wps:DataInputs>\n"
    postString += "<wps:ResponseForm>\n"
    postString += "<wps:ResponseDocument wps:lineage=\"true\" wps:storeExecuteResponse=\"true\" wps:status=\"true\">\n"
    for i in range(dataOutputs.size()):
      f_element = dataOutputs.at(i).toElement()
      outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
      literalOutputType = f_element.elementsByTagName("LiteralOutput")
      
      if literalOutputType.size()==0:
        postString += "<wps:Output asReference=\"true\">\n"
      else:
        postString += "<wps:Output>\n"
      postString += "<ows:Identifier>"+outputIdentifier+"</ows:Identifier>\n"
      postString += "</wps:Output>\n"
    postString += "</wps:ResponseDocument>\n"
    postString  += "</wps:ResponseForm>\n"
    postString += "</wps:Execute>\n"

#    f = urllib.urlopen( str(protocol)+"://"+str(server)+""+str(path), unicode(postString, "latin1").replace('"','\"').replace("\n",""))
    f = urllib.urlopen( str(protocol)+"://"+str(server)+""+str(path), unicode(postString, "latin1").replace('<wps:ComplexData>\n','<wps:ComplexData>'))
#    print postString

    # Read the results back.
    wpsRequestResult = f.read()
    
#    QMessageBox.information(None, '', wpsRequestResult)
#    QApplication .setOverrideCursor(Qt.ArrowCursor)
    QApplication.restoreOverrideCursor()
    QApplication .setOverrideCursor(Qt.ArrowCursor)
    self.resultHandler(wpsRequestResult)
    
  def resultHandler(self, resultXML, resultType="store"):
#    QMessageBox.information(None, '', resultXML)
    self.doc.setContent(resultXML,  True)
    resultNodeList = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Output")   
    layerName = self.tools.uniqueLayerName("WPSResult")   

    for i in range(resultNodeList.size()):
      f_element = resultNodeList.at(i).toElement()
      
      if f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "Reference").size() > 0:
        identifier = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
        reference = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Reference").at(0).toElement()
      
        fileLink = reference.attributeNS("http://www.w3.org/1999/xlink", "href", "0")
        mimeType = reference.attribute("mimeType", "0")
      
        if fileLink <> '0':
          resultFileConnector = urllib.urlretrieve(unicode(fileLink,'latin1'))
          resultFile = resultFileConnector[0]
          if mimeType=='text/xml':
            QMessageBox.information(None, '', resultFile)          
            vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
#          elif mimeType == 'image/tiff':
          else:
            newResultFile = self.tools.decodeBase64(resultFile)
#            newResultFile = resultFile
            QMessageBox.information(None, '', newResultFile)         
            rLayer = QgsRasterLayer(newResultFile, layerName)
            QgsMapLayerRegistry.instance().addMapLayer(rLayer)
      elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
        QApplication.restoreOverrideCursor()
        literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
        QMessageBox.information(None,'Result',literalText)
      else:
        self.tools.errorHandler(resultXML)

  def addComplexComboBox(self, title, name, mimeType,  wVdist, wHdist,  namesList, i):
      comboBox = QComboBox(self.dlgProcess)
      comboBox.addItems(namesList)
      comboBox.setGeometry(QRect(wHdist+16,wVdist,179,25))
      comboBox.setObjectName(name)
      myLabel = QLabel(self.dlgProcess)
      myLabel.setGeometry(QRect(20,int(wVdist),wHdist,19))       
      myLabel.setObjectName("qLabel"+name)  
      myLabel.setText(QString(title)+" ("+QString(mimeType)+")")
      return comboBox              

  def addValueComboBox(self, title, name, wVdist, wHdist,  namesList, i):
      comboBox = QComboBox(self.dlgProcess)
      comboBox.addItems(namesList)
      comboBox.setGeometry(QRect(wHdist+16,wVdist,179,  25))
      comboBox.setObjectName(name)
      myLabel = QLabel(self.dlgProcess)
      
      myLabel.setGeometry(QRect(20,int(wVdist),wHdist,19))       
      myLabel.setObjectName("qLabel"+name)  
      myLabel.setText(QString(title))        
      return comboBox

  def addLineEdit(self, title, name, wVdist, wHdist,  i):  
      myLineEdit = QLineEdit(self.dlgProcess)
      myLineEdit.setGeometry(QRect(wHdist+16,int(wVdist),179,27))
      myLineEdit.setObjectName(name)
      
      myLabel = QLabel(self.dlgProcess)
      myLabel.setGeometry(QRect(20,int(wVdist),wHdist,19))       
      myLabel.setObjectName("qLabel"+name)  
      myLabel.setText(QString(title))         
      
  def addCheckBox(self,  title,  name,  wVdist,  wHdist):
      myCheckBox = QCheckBox(self.dlgProcess)
      myCheckBox.setGeometry(QRect(20,int(wVdist),179,27))
      myCheckBox.setObjectName("chkBox"+name)
      myCheckBox.setChecked(False)
#      QMessageBox.information(None, '', "chkBox"+name)
      
      myLabel = QLabel(self.dlgProcess)
      myLabel.setGeometry(QRect(40,int(wVdist),wHdist,19))       
      myLabel.setObjectName("qLabel"+name)  
      myLabel.setText(QString(title))         
          
  def  getObjectSpace(self,  DataInputs):
    maxSize = 0
    for i in range(DataInputs.size()):
       f_element = DataInputs.at(i).toElement()
       dataIdentifier = f_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()
#       mimeType = self.tools.getMimeType(f_element)+self.tools.getMimeType(f_element, 'Supported')
       mimeType = self.tools.getMimeType(f_element)
       
       if len(unicode(dataIdentifier, 'latin1')+" "+unicode(mimeType, 'latin1')) > maxSize:
         maxSize = len(unicode(dataIdentifier, 'latin1')+" "+unicode(mimeType, 'latin1'))
    
    return maxSize*8  
      
    
