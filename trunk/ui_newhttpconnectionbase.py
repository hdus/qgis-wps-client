# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgsnewhttpconnectionbase.ui'
#
# Created: Wed Oct 21 17:45:31 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsNewHttpConnectionBase(object):
    def setupUi(self, QgsNewHttpConnectionBase):
        QgsNewHttpConnectionBase.setObjectName("QgsNewHttpConnectionBase")
        QgsNewHttpConnectionBase.resize(618, 247)
        QgsNewHttpConnectionBase.setSizeGripEnabled(True)
        QgsNewHttpConnectionBase.setModal(True)
        self.gridlayout = QtGui.QGridLayout(QgsNewHttpConnectionBase)
        self.gridlayout.setObjectName("gridlayout")
        self.GroupBox1 = QtGui.QGroupBox(QgsNewHttpConnectionBase)
        self.GroupBox1.setObjectName("GroupBox1")
        self.gridlayout1 = QtGui.QGridLayout(self.GroupBox1)
        self.gridlayout1.setObjectName("gridlayout1")
        self.TextLabel1_2 = QtGui.QLabel(self.GroupBox1)
        self.TextLabel1_2.setMargin(5)
        self.TextLabel1_2.setObjectName("TextLabel1_2")
        self.gridlayout1.addWidget(self.TextLabel1_2, 0, 0, 1, 1)
        self.txtName = QtGui.QLineEdit(self.GroupBox1)
        self.txtName.setMinimumSize(QtCore.QSize(0, 0))
        self.txtName.setFrame(True)
        self.txtName.setObjectName("txtName")
        self.gridlayout1.addWidget(self.txtName, 0, 1, 1, 2)
        self.TextLabel1 = QtGui.QLabel(self.GroupBox1)
        self.TextLabel1.setMargin(5)
        self.TextLabel1.setObjectName("TextLabel1")
        self.gridlayout1.addWidget(self.TextLabel1, 1, 0, 1, 1)
        self.txtUrl = QtGui.QLineEdit(self.GroupBox1)
        self.txtUrl.setObjectName("txtUrl")
        self.gridlayout1.addWidget(self.txtUrl, 1, 1, 1, 2)
        self.label = QtGui.QLabel(self.GroupBox1)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label, 2, 0, 1, 1)
        self.txtVersion = QtGui.QLineEdit(self.GroupBox1)
        self.txtVersion.setObjectName("txtVersion")
        self.gridlayout1.addWidget(self.txtVersion, 2, 1, 1, 2)
        self.gridlayout.addWidget(self.GroupBox1, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(QgsNewHttpConnectionBase)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.TextLabel1_2.setBuddy(self.txtName)
        self.TextLabel1.setBuddy(self.txtUrl)

        self.retranslateUi(QgsNewHttpConnectionBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), QgsNewHttpConnectionBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), QgsNewHttpConnectionBase.reject)
        QtCore.QMetaObject.connectSlotsByName(QgsNewHttpConnectionBase)
        QgsNewHttpConnectionBase.setTabOrder(self.txtName, self.txtUrl)

    def retranslateUi(self, QgsNewHttpConnectionBase):
        QgsNewHttpConnectionBase.setWindowTitle(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "Create a new WPS connection", None, QtGui.QApplication.UnicodeUTF8))
        self.GroupBox1.setTitle(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "Connection details", None, QtGui.QApplication.UnicodeUTF8))
        self.TextLabel1_2.setText(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.txtName.setToolTip(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "Name of the new connection", None, QtGui.QApplication.UnicodeUTF8))
        self.TextLabel1.setText(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "URL", None, QtGui.QApplication.UnicodeUTF8))
        self.txtUrl.setToolTip(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "HTTP address of the Web Map Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("QgsNewHttpConnectionBase", "Version", None, QtGui.QApplication.UnicodeUTF8))

