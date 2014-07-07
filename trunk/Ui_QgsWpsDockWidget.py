# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QgsWpsDockWidget.ui'
#
# Created: Thu Jul  3 17:22:57 2014
#      by: PyQt4 UI code generator 4.11.1-snapshot-9d5a6843b580
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QgsWpsDockWidget(object):
    def setupUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setObjectName(_fromUtf8("QgsWpsDockWidget"))
        QgsWpsDockWidget.resize(285, 190)
        QgsWpsDockWidget.setMinimumSize(QtCore.QSize(285, 190))
        QgsWpsDockWidget.setMaximumSize(QtCore.QSize(524287, 190))
        QgsWpsDockWidget.setBaseSize(QtCore.QSize(0, 0))
        QgsWpsDockWidget.setFloating(False)
        QgsWpsDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        QgsWpsDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.statusLabel = QtGui.QLabel(self.groupBox)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.verticalLayout.addWidget(self.statusLabel)
        self.progressBar = QtGui.QProgressBar(self.groupBox)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 2)
        self.btnConnect = QtGui.QPushButton(self.dockWidgetContents)
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.gridLayout.addWidget(self.btnConnect, 0, 0, 1, 1)
        self.btnKill = QtGui.QPushButton(self.dockWidgetContents)
        self.btnKill.setEnabled(False)
        self.btnKill.setObjectName(_fromUtf8("btnKill"))
        self.gridLayout.addWidget(self.btnKill, 0, 1, 1, 1)
        QgsWpsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(QgsWpsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDockWidget)

    def retranslateUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setWindowTitle(_translate("QgsWpsDockWidget", "QGIS WPS-Client", None))
        self.btnConnect.setText(_translate("QgsWpsDockWidget", "connect", None))
        self.btnKill.setText(_translate("QgsWpsDockWidget", "kill process", None))

