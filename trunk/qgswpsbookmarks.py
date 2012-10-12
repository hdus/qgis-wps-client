# -*- coding: latin1 -*-
"""
 /***************************************************************************
   qgswps.py QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch
"""
***************************************************************************
   qgswps.py QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

 Authors              : Dr. Horst Duester

  ***************************************************************************
  *                                                                         *
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                          *
  ***************************************************************************
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from wps import version

from Ui_qgswpsbookmarks import Ui_Bookmarks

class Bookmarks(QDialog, QObject,  Ui_Bookmarks):
    """
    Class documentation goes here.
    """
    def __init__(self, fl,  parent=None):
        """
        Constructor
        """
        QDialog.__init__(self, parent,  fl)
        self.setupUi(self)
        self.setWindowTitle('QGIS WPS-Client '+version())
        self.initTreeWPSServices()
        
    def initTreeWPSServices(self):
        settings = QSettings()
        settings.beginGroup("WPS-Bookmarks")
        bookmarks = settings.childGroups()        
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(self.treeWidget.columnCount())
        itemList = []
        
        self.btnOK.setEnabled(False)
                
        for myBookmark in bookmarks:
           settings = QSettings()
           self.myItem = QTreeWidgetItem()
           
           mySettings = "/WPS-Bookmarks/"+myBookmark
           scheme = settings.value(mySettings+"/scheme").toString()
           server = settings.value(mySettings+"/server").toString()
           path = settings.value(mySettings+"/path").toString()
           port = settings.value(mySettings+"/port").toString()

           myBookmarkArray = myBookmark.split("@@")
           service = myBookmarkArray[0]
           version = settings.value(mySettings+"/version").toString()
           identifier = settings.value(mySettings+"/identifier").toString()
           self.myItem.setText(0, service)  
           self.myItem.setText(1,identifier)  
           self.myItem.setText(2,server)
           itemList.append(self.myItem)
           self.btnOK.setEnabled(True)
           
    
        self.treeWidget.addTopLevelItems(itemList)        


    @pyqtSignature("QTreeWidgetItem*, int")
    def on_treeWidget_itemDoubleClicked(self, item, column):
        self.emit(SIGNAL("getBookmarkDescription(QTreeWidgetItem)"), item)
        self.close()

    @pyqtSignature("")
    def on_btnConnect_clicked(self):
#        self.emit(SIGNAL("getBookmarkDescription(QString, QTreeWidgetItem)"), self.myItem.text(0),  self.myItem)
        self.close()

    
    @pyqtSignature("")
    def on_btnEdit_clicked(self):
         pass
    
    @pyqtSignature("")
    def on_btnRemove_clicked(self):
        self.removeBookmark(self.treeWidget.currentItem())
       
    @pyqtSignature("")
    def on_btnOK_clicked(self):
        self.emit(SIGNAL("getBookmarkDescription(QTreeWidgetItem)"), self.myItem)

    
    @pyqtSignature("")
    def on_btnClose_clicked(self):
         self.close()
         
    def removeBookmark(self,  item):
        QMessageBox.information(None, '', item.text(0)+'@@'+item.text(1))
        settings = QSettings()
        settings.beginGroup("WPS-Bookmarks")
        settings.remove(item.text(0)+'@@'+item.text(1))
        settings.endGroup()
        self.initTreeWPSServices()          
