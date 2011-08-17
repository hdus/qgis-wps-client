# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home_nas/sogis/barpadue/.qgis/python/plugins/wps/QgsWpsDockWidget.ui'
#
# Created: Wed Aug 17 11:33:31 2011
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsWpsDockWidget(object):
    def setupUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setObjectName("QgsWpsDockWidget")
        QgsWpsDockWidget.resize(262, 190)
        QgsWpsDockWidget.setMinimumSize(QtCore.QSize(190, 190))
        QgsWpsDockWidget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(50)
        font.setBold(False)
        QgsWpsDockWidget.setFont(font)
        QgsWpsDockWidget.setFloating(False)
        QgsWpsDockWidget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        QgsWpsDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.warning = QtGui.QLabel(self.dockWidgetContents)
        self.warning.setGeometry(QtCore.QRect(30, 50, 161, 20))
        self.warning.setTextFormat(QtCore.Qt.PlainText)
        self.warning.setObjectName("warning")
        QgsWpsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(QgsWpsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDockWidget)

    def retranslateUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setWindowTitle(QtGui.QApplication.translate("QgsWpsDockWidget", "QgsWps", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDockWidget = QtGui.QDockWidget()
    ui = Ui_QgsWpsDockWidget()
    ui.setupUi(QgsWpsDockWidget)
    QgsWpsDockWidget.show()
    sys.exit(app.exec_())

