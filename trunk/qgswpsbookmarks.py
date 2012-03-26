# -*- coding: utf-8 -*-

"""
Module implementing Bookmarks.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

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
        
##    self.btnOk.setEnabled(False)
#        self.btnConnect.setEnabled(True)
        self.initTreeWPSServices()
        
    def initTreeWPSServices(self):
        settings = QSettings()
        settings.beginGroup("WPS-Bookmarks")
        bookmarks = settings.childGroups()        
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(self.treeWidget.columnCount())
        itemList = []
        for myBookmark in bookmarks:
           settings = QSettings()
           self.myItem = QTreeWidgetItem()
           mySettings = "/WPS-Bookmarks/"+myBookmark
           scheme = settings.value(mySettings+"/scheme").toString()
           server = settings.value(mySettings+"/server").toString()
           path = settings.value(mySettings+"/path").toString()
           service = scheme+"://"+server+path
           version = settings.value(mySettings+"/version").toString()
           identifier = settings.value(mySettings+"/identifier").toString()
           self.myItem.setText(0, server)  
           self.myItem.setText(1,identifier)  
           self.myItem.setText(2,service)
           itemList.append(self.myItem)
    
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
         self.emit(SIGNAL("removeBookmark(QTreeWidgetItem, int)"), self.treeWidget.currentItem(),  self.treeWidget.currentColumn())    
    
    @pyqtSignature("")
    def on_btnBoxBookmarks_accepted(self):
        self.emit(SIGNAL("getBookmarkDescription(QTreeWidgetItem)"), self.myItem)

    
    @pyqtSignature("")
    def on_btnBoxBookmarks_rejected(self):
         self.close()
