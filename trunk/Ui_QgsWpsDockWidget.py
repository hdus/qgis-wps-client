# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/dev/qgis/wps-plugin/wps/QgsWpsDockWidget.ui'
#
# Created: Sat Oct  6 10:33:57 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QgsWpsDockWidget(object):
    def setupUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setObjectName(_fromUtf8("QgsWpsDockWidget"))
        QgsWpsDockWidget.resize(285, 190)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(QgsWpsDockWidget.sizePolicy().hasHeightForWidth())
        QgsWpsDockWidget.setSizePolicy(sizePolicy)
        QgsWpsDockWidget.setMinimumSize(QtCore.QSize(189, 190))
        QgsWpsDockWidget.setMaximumSize(QtCore.QSize(524287, 524287))
        QgsWpsDockWidget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        QgsWpsDockWidget.setFont(font)
        QgsWpsDockWidget.setFloating(False)
        QgsWpsDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        QgsWpsDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnConnect = QtGui.QPushButton(self.dockWidgetContents)
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.horizontalLayout.addWidget(self.btnConnect)
        self.btnKill = QtGui.QPushButton(self.dockWidgetContents)
        self.btnKill.setObjectName(_fromUtf8("btnKill"))
        self.horizontalLayout.addWidget(self.btnKill)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(self.dockWidgetContents)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 1)
        QgsWpsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(QgsWpsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDockWidget)

    def retranslateUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setWindowTitle(QtGui.QApplication.translate("QgsWpsDockWidget", "QGIS WPS-Client", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setText(QtGui.QApplication.translate("QgsWpsDockWidget", "connect", None, QtGui.QApplication.UnicodeUTF8))
        self.btnKill.setText(QtGui.QApplication.translate("QgsWpsDockWidget", "kill process", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDockWidget = QtGui.QDockWidget()
    ui = Ui_QgsWpsDockWidget()
    ui.setupUi(QgsWpsDockWidget)
    QgsWpsDockWidget.show()
    sys.exit(app.exec_())

