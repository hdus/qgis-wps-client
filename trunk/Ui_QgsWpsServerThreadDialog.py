# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/Threads/ServerThreadDialog.ui'
#
# Created: Mon Aug 15 11:55:13 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ServerThreadDialog(object):
    def setupUi(self, ServerThreadDialog):
        ServerThreadDialog.setObjectName("ServerThreadDialog")
        ServerThreadDialog.resize(541, 146)
        self.gridLayout = QtGui.QGridLayout(ServerThreadDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(ServerThreadDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBox = QtGui.QSpinBox(ServerThreadDialog)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(1000000)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.spinBox)
        self.btnThread = QtGui.QPushButton(ServerThreadDialog)
        self.btnThread.setObjectName("btnThread")
        self.horizontalLayout.addWidget(self.btnThread)
        self.btnNoThread = QtGui.QPushButton(ServerThreadDialog)
        self.btnNoThread.setObjectName("btnNoThread")
        self.horizontalLayout.addWidget(self.btnNoThread)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.progressBar = QtGui.QProgressBar(ServerThreadDialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtGui.QLineEdit(ServerThreadDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.buttonBox = QtGui.QDialogButtonBox(ServerThreadDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.lblTest = QtGui.QLabel(ServerThreadDialog)
        self.lblTest.setText("")
        self.lblTest.setObjectName("lblTest")
        self.gridLayout.addWidget(self.lblTest, 2, 1, 1, 1)

        self.retranslateUi(ServerThreadDialog)
        QtCore.QMetaObject.connectSlotsByName(ServerThreadDialog)

    def retranslateUi(self, ServerThreadDialog):
        ServerThreadDialog.setWindowTitle(QtGui.QApplication.translate("ServerThreadDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ServerThreadDialog", "Number of Iterations:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnThread.setText(QtGui.QApplication.translate("ServerThreadDialog", "start threaded", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNoThread.setText(QtGui.QApplication.translate("ServerThreadDialog", "start unthreaded", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ServerThreadDialog = QtGui.QDialog()
    ui = Ui_ServerThreadDialog()
    ui.setupUi(ServerThreadDialog)
    ServerThreadDialog.show()
    sys.exit(app.exec_())

