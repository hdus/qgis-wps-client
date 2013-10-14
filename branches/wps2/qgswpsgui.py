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
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from qgis.core import *
from wps import version
from wpslib.wpsserver import WpsServer
from Ui_qgswpsgui import Ui_QgsWps
from qgswpsbookmarks import Bookmarks
from doAbout import DlgAbout


import os, sys, string

class QgsWpsGui(QDialog, QObject, Ui_QgsWps):
  MSG_BOX_TITLE = "WPS"
  
  def __init__(self, parent, fl):
    QDialog.__init__(self, parent, fl)
    self.setupUi(self)
    self.fl = fl
    self.setWindowTitle('QGIS WPS-Client '+version())
    self.dlgAbout = DlgAbout(parent)
   
  def initQgsWpsGui(self):    
##    self.btnOk.setEnabled(False)
    self.btnConnect.setEnabled(False)
    settings = QSettings()
    settings.beginGroup("WPS")
    connections = settings.childGroups()
    self.cmbConnections.clear()
    self.cmbConnections.addItems(connections)
    self.treeWidget.clear()
        
    if self.cmbConnections.size() > 0:
      self.btnConnect.setEnabled(True)
      self.btnEdit.setEnabled(True)
      self.btnDelete.setEnabled(True)
    return 1    


  def getBookmark(self, item):
      self.emit(SIGNAL("requestDescribeProcess(QString, QString)"), item.text(0), item.text(1))
        
  def on_buttonBox_rejected(self):
    self.close()

  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  @pyqtSignature("on_buttonBox_accepted()")          
  def on_buttonBox_accepted(self):
    if  self.treeWidget.topLevelItemCount() == 0:
      QMessageBox.warning(None, 'WPS Warning','No Service connected!')
    else:
      self.emit(SIGNAL("getDescription(QString,QTreeWidgetItem)"), self.cmbConnections.currentText(),  self.treeWidget.currentItem() )
    
  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  @pyqtSignature("on_btnConnect_clicked()")       
  def on_btnConnect_clicked(self):
    self.treeWidget.clear()
    selectedWPS = self.cmbConnections.currentText()
    self.server = WpsServer.getServer(selectedWPS)
    QObject.connect(self.server, SIGNAL("capabilitiesRequestFinished"), self.createCapabilitiesGUI)
    self.server.requestCapabilities()

  @pyqtSignature("on_btnBookmarks_clicked()")       
  def on_btnBookmarks_clicked(self):    
      self.dlgBookmarks = Bookmarks(self.fl)
      QObject.connect(self.dlgBookmarks, SIGNAL("getBookmarkDescription(QTreeWidgetItem)"), self.getBookmark)
      QObject.connect(self.dlgBookmarks, SIGNAL("bookmarksChanged()"), self, SIGNAL("bookmarksChanged()"))
      self.dlgBookmarks.show()

  @pyqtSignature("on_btnNew_clicked()")       
  def on_btnNew_clicked(self):    
    self.emit(SIGNAL("newServer()"))
    
  @pyqtSignature("on_btnEdit_clicked()")       
  def on_btnEdit_clicked(self):    
    self.emit(SIGNAL("editServer(QString)"), self.cmbConnections.currentText())    

  @pyqtSignature("on_cmbConnections_currentIndexChanged()")           
  def on_cmbConnections_currentIndexChanged(self):
    pass
  
  @pyqtSignature("on_btnDelete_clicked()")       
  def on_btnDelete_clicked(self):    
    self.emit(SIGNAL("deleteServer(QString)"), self.cmbConnections.currentText())    

  @pyqtSignature("on_pushDefaultServer_clicked()")       
  def on_pushDefaultServer_clicked(self):    
    self.emit(SIGNAL("pushDefaultServer()"))   

  def initTreeWPSServices(self, taglist):
    self.treeWidget.setColumnCount(self.treeWidget.columnCount())
    itemList = []
    for items in taglist:
      item = QTreeWidgetItem()
      ident = unicode(items[0],'latin1')
      title = unicode(items[1],'latin1')
      abstract = unicode(items[2],'latin1')
      item.setText(0,ident.strip())
      item.setText(1,title.strip())  
      item.setText(2,abstract.strip())  
      itemList.append(item)
    
    self.treeWidget.addTopLevelItems(itemList)
    
  @pyqtSignature("on_btnAbout_clicked()")       
  def on_btnAbout_clicked(self):
      self.dlgAbout.show()
      pass
    
  @pyqtSignature("QTreeWidgetItem*, int")
  def on_treeWidget_itemDoubleClicked(self, item, column):
      self.emit(SIGNAL("getDescription(QString,QTreeWidgetItem)"), self.cmbConnections.currentText(),  self.treeWidget.currentItem() )

  def createCapabilitiesGUI(self):
      try:
          self.treeWidget.clear()
          itemListAll = self.server.parseCapabilitiesXML()
          self.initTreeWPSServices(itemListAll)
      except:
          pass
