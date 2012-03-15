# -*- coding: utf-8 -*-

"""
Module implementing Bookmarks.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4 import QtWebKit
from PyQt4 import QtNetwork

from Ui_qgswpsbookmarks import Ui_Bookmarks

class Bookmarks(QDialog, Ui_Bookmarks):
    """
    Class documentation goes here.
    """
    def __init__(self, tools,  fl,  parent=None):
        """
        Constructor
        """
        QDialog.__init__(self, parent,  fl)
        self.setupUi(self)
        
##    self.btnOk.setEnabled(False)
        self.tools = tools
        self.btnConnect.setEnabled(True)
        settings = QSettings()
        settings.beginGroup("WPS-Bookmarks")
        self.bookmarks = settings.childGroups()

        self.initTreeWPSServices()
        
    def initTreeWPSServices(self):
        self.treeWidget.setColumnCount(self.treeWidget.columnCount())
        itemList = []
        for myBookmark in self.bookmarks:
           settings = QSettings()
           item = QTreeWidgetItem()
           mySettings = "/WPS-Bookmarks/"+myBookmark
           scheme = settings.value(mySettings+"/scheme").toString()
           server = settings.value(mySettings+"/server").toString()
           path = settings.value(mySettings+"/path").toString()
           service = scheme+"://"+server+path
           version = settings.value(mySettings+"/version").toString()
           identifier = settings.value(mySettings+"/identifier").toString()
           item.setText(0, myBookmark)  
           item.setText(1,identifier)  
           item.setText(2,service)
           itemList.append(item)
    
        self.treeWidget.addTopLevelItems(itemList)        


    @pyqtSignature("QTreeWidgetItem*, int")
    def on_treeWidget_itemDoubleClicked(self, item, column):
        QMessageBox.information(None, '',item.text(0))
        self.emit(SIGNAL("getBookmarkDescription(QString, QTreeWidgetItem)"), item.text(0),  self.treeWidget.currentItem() )

    @pyqtSignature("")
    def on_btnConnect_clicked(self):
         pass
    
    @pyqtSignature("")
    def on_btnEdit_clicked(self):
         pass
    
    @pyqtSignature("")
    def on_btnRemove_clicked(self):
         pass
    
    @pyqtSignature("")
    def on_btnBoxBookmarks_accepted(self):
         pass
    
    @pyqtSignature("")
    def on_btnBoxBookmarks_rejected(self):
         self.close()
