# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/wps/QgsWpsDockWidget.ui'
#
# Created: Thu Apr 12 18:30:20 2012
#      by: PyQt4 UI code generator 4.8.5
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
        QgsWpsDockWidget.resize(358, 190)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(QgsWpsDockWidget.sizePolicy().hasHeightForWidth())
        QgsWpsDockWidget.setSizePolicy(sizePolicy)
        QgsWpsDockWidget.setMinimumSize(QtCore.QSize(285, 190))
        QgsWpsDockWidget.setMaximumSize(QtCore.QSize(524287, 190))
        QgsWpsDockWidget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        QgsWpsDockWidget.setFont(font)
        QgsWpsDockWidget.setFloating(False)
        QgsWpsDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        QgsWpsDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        QgsWpsDockWidget.setWindowTitle(QtGui.QApplication.translate("QgsWpsDockWidget", "QGIS WPS-Client", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnConnect = QtGui.QPushButton(self.dockWidgetContents)
        self.btnConnect.setText(QtGui.QApplication.translate("QgsWpsDockWidget", "connect", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.horizontalLayout.addWidget(self.btnConnect)
        self.btnKill = QtGui.QPushButton(self.dockWidgetContents)
        self.btnKill.setText(QtGui.QApplication.translate("QgsWpsDockWidget", "kill process", None, QtGui.QApplication.UnicodeUTF8))
        self.btnKill.setObjectName(_fromUtf8("btnKill"))
        self.horizontalLayout.addWidget(self.btnKill)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.lblProcess = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProcess.sizePolicy().hasHeightForWidth())
        self.lblProcess.setSizePolicy(sizePolicy)
        self.lblProcess.setText(_fromUtf8(""))
        self.lblProcess.setWordWrap(True)
        self.lblProcess.setObjectName(_fromUtf8("lblProcess"))
        self.gridLayout.addWidget(self.lblProcess, 1, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(self.dockWidgetContents)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 1)
        QgsWpsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(QgsWpsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDockWidget)

    def retranslateUi(self, QgsWpsDockWidget):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDockWidget = QtGui.QDockWidget()
    ui = Ui_QgsWpsDockWidget()
    ui.setupUi(QgsWpsDockWidget)
    QgsWpsDockWidget.show()
    sys.exit(app.exec_())

