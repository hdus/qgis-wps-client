# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/wps/QgsWpsServerThreadDialog.ui'
#
# Created: Mon Aug 15 14:17:37 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsWpsServerThreadDialog(object):
    def setupUi(self, QgsWpsServerThreadDialog):
        QgsWpsServerThreadDialog.setObjectName("QgsWpsServerThreadDialog")
        QgsWpsServerThreadDialog.resize(573, 72)
        self.gridLayout = QtGui.QGridLayout(QgsWpsServerThreadDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(QgsWpsServerThreadDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.lblProcess = QtGui.QLabel(QgsWpsServerThreadDialog)
        self.lblProcess.setText("")
        self.lblProcess.setObjectName("lblProcess")
        self.gridLayout.addWidget(self.lblProcess, 0, 1, 1, 3)
        self.lineEdit = QtGui.QLineEdit(QgsWpsServerThreadDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 2, 1, 1)
        self.lblTest = QtGui.QLabel(QgsWpsServerThreadDialog)
        self.lblTest.setText("")
        self.lblTest.setObjectName("lblTest")
        self.gridLayout.addWidget(self.lblTest, 1, 4, 1, 1)
        self.label = QtGui.QLabel(QgsWpsServerThreadDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(QgsWpsServerThreadDialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 3, 1, 1)

        self.retranslateUi(QgsWpsServerThreadDialog)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsServerThreadDialog)

    def retranslateUi(self, QgsWpsServerThreadDialog):
        QgsWpsServerThreadDialog.setWindowTitle(QtGui.QApplication.translate("QgsWpsServerThreadDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("QgsWpsServerThreadDialog", "Process:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("QgsWpsServerThreadDialog", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("QgsWpsServerThreadDialog", "cancel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsServerThreadDialog = QtGui.QDialog()
    ui = Ui_QgsWpsServerThreadDialog()
    ui.setupUi(QgsWpsServerThreadDialog)
    QgsWpsServerThreadDialog.show()
    sys.exit(app.exec_())

