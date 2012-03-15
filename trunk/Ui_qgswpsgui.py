# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/barpadue/.qgis/python/plugins/wps/qgswpsgui.ui'
#
# Created: Thu Mar 15 14:23:34 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QgsWps(object):
    def setupUi(self, QgsWps):
        QgsWps.setObjectName(_fromUtf8("QgsWps"))
        QgsWps.setWindowModality(QtCore.Qt.NonModal)
        QgsWps.resize(780, 604)
        QgsWps.setAcceptDrops(False)
        QgsWps.setWindowTitle(QtGui.QApplication.translate("QgsWps", "Note: this plugin not considered stable yet. Use it on your own risk", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(QgsWps)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnAbout = QtGui.QPushButton(QgsWps)
        self.btnAbout.setText(QtGui.QApplication.translate("QgsWps", "about", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbout.setObjectName(_fromUtf8("btnAbout"))
        self.hboxlayout.addWidget(self.btnAbout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(QgsWps)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.hboxlayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        self.treeWidget = QtGui.QTreeWidget(QgsWps)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("QgsWps", "Identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("QgsWps", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(2, QtGui.QApplication.translate("QgsWps", "Abstract", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.treeWidget, 2, 0, 1, 1)
        self.GroupBox1 = QtGui.QGroupBox(QgsWps)
        self.GroupBox1.setTitle(QtGui.QApplication.translate("QgsWps", "Server Connections", None, QtGui.QApplication.UnicodeUTF8))
        self.GroupBox1.setObjectName(_fromUtf8("GroupBox1"))
        self.gridlayout = QtGui.QGridLayout(self.GroupBox1)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.btnNew = QtGui.QPushButton(self.GroupBox1)
        self.btnNew.setText(QtGui.QApplication.translate("QgsWps", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setObjectName(_fromUtf8("btnNew"))
        self.gridlayout.addWidget(self.btnNew, 1, 1, 1, 1)
        self.btnEdit = QtGui.QPushButton(self.GroupBox1)
        self.btnEdit.setEnabled(False)
        self.btnEdit.setText(QtGui.QApplication.translate("QgsWps", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.gridlayout.addWidget(self.btnEdit, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(171, 30, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.btnConnect = QtGui.QPushButton(self.GroupBox1)
        self.btnConnect.setEnabled(True)
        self.btnConnect.setText(QtGui.QApplication.translate("QgsWps", "C&onnect", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.gridlayout.addWidget(self.btnConnect, 1, 0, 1, 1)
        self.cmbConnections = QtGui.QComboBox(self.GroupBox1)
        self.cmbConnections.setObjectName(_fromUtf8("cmbConnections"))
        self.gridlayout.addWidget(self.cmbConnections, 0, 0, 1, 7)
        self.btnDelete = QtGui.QPushButton(self.GroupBox1)
        self.btnDelete.setEnabled(False)
        self.btnDelete.setText(QtGui.QApplication.translate("QgsWps", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.gridlayout.addWidget(self.btnDelete, 1, 3, 1, 1)
        self.pushDefaultServer = QtGui.QPushButton(self.GroupBox1)
        self.pushDefaultServer.setText(QtGui.QApplication.translate("QgsWps", "Add default server", None, QtGui.QApplication.UnicodeUTF8))
        self.pushDefaultServer.setObjectName(_fromUtf8("pushDefaultServer"))
        self.gridlayout.addWidget(self.pushDefaultServer, 1, 6, 1, 1)
        self.btnBookmarks = QtGui.QPushButton(self.GroupBox1)
        self.btnBookmarks.setText(QtGui.QApplication.translate("QgsWps", "Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBookmarks.setObjectName(_fromUtf8("btnBookmarks"))
        self.gridlayout.addWidget(self.btnBookmarks, 1, 5, 1, 1)
        self.gridLayout.addWidget(self.GroupBox1, 0, 0, 1, 1)

        self.retranslateUi(QgsWps)
        QtCore.QMetaObject.connectSlotsByName(QgsWps)

    def retranslateUi(self, QgsWps):
        self.treeWidget.setSortingEnabled(True)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWps = QtGui.QDialog()
    ui = Ui_QgsWps()
    ui.setupUi(QgsWps)
    QgsWps.show()
    sys.exit(app.exec_())

