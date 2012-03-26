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
        settings = QSettings()
        settings.beginGroup("WPS-Bookmarks")
        settings.remove(item.text(0))
        settings.endGroup()
        self.initTreeWPSServices()          
