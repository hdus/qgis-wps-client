# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home_nas/sogis/barpadue/.qgis/python/plugins/wps/qgswpsdockwidget.ui'
#
# Created: Wed Aug 17 11:25:53 2011
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsWpsDockWidget(object):
    def setupUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setObjectName("QgsWpsDockWidget")
        QgsWpsDockWidget.resize(450, 134)

        self.retranslateUi(QgsWpsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDockWidget)

    def retranslateUi(self, QgsWpsDockWidget):
        QgsWpsDockWidget.setWindowTitle(QtGui.QApplication.translate("QgsWpsDockWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDockWidget = QtGui.QDockWidget()
    ui = Ui_QgsWpsDockWidget()
    ui.setupUi(QgsWpsDockWidget)
    QgsWpsDockWidget.show()
    sys.exit(app.exec_())

