# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/wps/qgswpsgui.ui'
#
# Created: Thu Nov 11 16:18:02 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsWps(object):
    def setupUi(self, QgsWps):
        QgsWps.setObjectName("QgsWps")
        QgsWps.setWindowModality(QtCore.Qt.WindowModal)
        QgsWps.resize(593, 442)
        QgsWps.setAcceptDrops(False)
        self.gridLayout = QtGui.QGridLayout(QgsWps)
        self.gridLayout.setObjectName("gridLayout")
        self.GroupBox1 = QtGui.QGroupBox(QgsWps)
        self.GroupBox1.setObjectName("GroupBox1")
        self.gridlayout = QtGui.QGridLayout(self.GroupBox1)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.btnNew = QtGui.QPushButton(self.GroupBox1)
        self.btnNew.setObjectName("btnNew")
        self.gridlayout.addWidget(self.btnNew, 1, 1, 1, 1)
        self.btnEdit = QtGui.QPushButton(self.GroupBox1)
        self.btnEdit.setEnabled(False)
        self.btnEdit.setObjectName("btnEdit")
        self.gridlayout.addWidget(self.btnEdit, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(171, 30, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 1, 4, 1, 1)
        self.btnConnect = QtGui.QPushButton(self.GroupBox1)
        self.btnConnect.setEnabled(True)
        self.btnConnect.setObjectName("btnConnect")
        self.gridlayout.addWidget(self.btnConnect, 1, 0, 1, 1)
        self.cmbConnections = QtGui.QComboBox(self.GroupBox1)
        self.cmbConnections.setObjectName("cmbConnections")
        self.gridlayout.addWidget(self.cmbConnections, 0, 0, 1, 5)
        self.btnDelete = QtGui.QPushButton(self.GroupBox1)
        self.btnDelete.setEnabled(False)
        self.btnDelete.setObjectName("btnDelete")
        self.gridlayout.addWidget(self.btnDelete, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.GroupBox1, 0, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(QgsWps)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.hboxlayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        self.treeWidget = QtGui.QTreeWidget(QgsWps)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName("treeWidget")
        self.gridLayout.addWidget(self.treeWidget, 2, 0, 1, 1)

        self.retranslateUi(QgsWps)
        QtCore.QMetaObject.connectSlotsByName(QgsWps)

    def retranslateUi(self, QgsWps):
        QgsWps.setWindowTitle(QtGui.QApplication.translate("QgsWps", "Note: this plugin not considered stable yet. Use it on your own risk", None, QtGui.QApplication.UnicodeUTF8))
        self.GroupBox1.setTitle(QtGui.QApplication.translate("QgsWps", "Server Connections", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setText(QtGui.QApplication.translate("QgsWps", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setText(QtGui.QApplication.translate("QgsWps", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setText(QtGui.QApplication.translate("QgsWps", "C&onnect", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("QgsWps", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("QgsWps", "Identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("QgsWps", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(2, QtGui.QApplication.translate("QgsWps", "Abstract", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWps = QtGui.QDialog()
    ui = Ui_QgsWps()
    ui.setupUi(QgsWps)
    QgsWps.show()
    sys.exit(app.exec_())

