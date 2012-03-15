# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/wps/qgswpsbookmarks.ui'
#
# Created: Thu Mar 15 22:19:36 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Bookmarks(object):
    def setupUi(self, Bookmarks):
        Bookmarks.setObjectName(_fromUtf8("Bookmarks"))
        Bookmarks.resize(753, 422)
        Bookmarks.setWindowTitle(QtGui.QApplication.translate("Bookmarks", "WPS-Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(Bookmarks)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnRemove = QtGui.QPushButton(Bookmarks)
        self.btnRemove.setText(QtGui.QApplication.translate("Bookmarks", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setObjectName(_fromUtf8("btnRemove"))
        self.horizontalLayout.addWidget(self.btnRemove)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.treeWidget = QtGui.QTreeWidget(Bookmarks)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("Bookmarks", "Service", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("Bookmarks", "Identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(2, QtGui.QApplication.translate("Bookmarks", "URL", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.header().setDefaultSectionSize(250)
        self.gridLayout.addWidget(self.treeWidget, 1, 0, 1, 1)
        self.btnBoxBookmarks = QtGui.QDialogButtonBox(Bookmarks)
        self.btnBoxBookmarks.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.btnBoxBookmarks.setObjectName(_fromUtf8("btnBoxBookmarks"))
        self.gridLayout.addWidget(self.btnBoxBookmarks, 2, 0, 1, 1)

        self.retranslateUi(Bookmarks)
        QtCore.QMetaObject.connectSlotsByName(Bookmarks)

    def retranslateUi(self, Bookmarks):
        self.treeWidget.setSortingEnabled(True)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Bookmarks = QtGui.QDialog()
    ui = Ui_Bookmarks()
    ui.setupUi(Bookmarks)
    Bookmarks.show()
    sys.exit(app.exec_())

