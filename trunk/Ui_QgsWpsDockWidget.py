# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home_nas/sogis/barpadue/.qgis/python/plugins/wps/QgsWpsDockWidget.ui'
#
# Created: Wed Aug 17 11:32:22 2011
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_gewissoDockWidget(object):
    def setupUi(self, gewissoDockWidget):
        gewissoDockWidget.setObjectName("gewissoDockWidget")
        gewissoDockWidget.resize(262, 190)
        gewissoDockWidget.setMinimumSize(QtCore.QSize(190, 190))
        gewissoDockWidget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(50)
        font.setBold(False)
        gewissoDockWidget.setFont(font)
        gewissoDockWidget.setFloating(False)
        gewissoDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        gewissoDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.radioReal = QtGui.QRadioButton(self.dockWidgetContents)
        self.radioReal.setGeometry(QtCore.QRect(160, 20, 61, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.radioReal.setFont(font)
        self.radioReal.setObjectName("radioReal")
        self.radioKarto = QtGui.QRadioButton(self.dockWidgetContents)
        self.radioKarto.setGeometry(QtCore.QRect(30, 20, 113, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioKarto.sizePolicy().hasHeightForWidth())
        self.radioKarto.setSizePolicy(sizePolicy)
        self.radioKarto.setMinimumSize(QtCore.QSize(0, 2))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.radioKarto.setFont(font)
        self.radioKarto.setObjectName("radioKarto")
        self.warning = QtGui.QLabel(self.dockWidgetContents)
        self.warning.setGeometry(QtCore.QRect(30, 50, 161, 20))
        self.warning.setTextFormat(QtCore.Qt.PlainText)
        self.warning.setObjectName("warning")
        self.btnFlip = QtGui.QPushButton(self.dockWidgetContents)
        self.btnFlip.setGeometry(QtCore.QRect(30, 60, 78, 27))
        self.btnFlip.setObjectName("btnFlip")
        gewissoDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(gewissoDockWidget)
        QtCore.QMetaObject.connectSlotsByName(gewissoDockWidget)

    def retranslateUi(self, gewissoDockWidget):
        gewissoDockWidget.setWindowTitle(QtGui.QApplication.translate("gewissoDockWidget", "Nachführung Gewisso", None, QtGui.QApplication.UnicodeUTF8))
        self.radioReal.setText(QtGui.QApplication.translate("gewissoDockWidget", "real", None, QtGui.QApplication.UnicodeUTF8))
        self.radioKarto.setText(QtGui.QApplication.translate("gewissoDockWidget", "kartografisch", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFlip.setText(QtGui.QApplication.translate("gewissoDockWidget", "Flip", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    gewissoDockWidget = QtGui.QDockWidget()
    ui = Ui_gewissoDockWidget()
    ui.setupUi(gewissoDockWidget)
    gewissoDockWidget.show()
    sys.exit(app.exec_())

