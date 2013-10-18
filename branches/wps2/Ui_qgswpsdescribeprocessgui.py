# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis2/python/plugins/wps2/qgswpsdescribeprocessgui.ui'
#
# Created: Fri Oct 18 21:04:46 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QgsWpsDescribeProcessGUI(object):
    def setupUi(self, QgsWpsDescribeProcessGUI):
        QgsWpsDescribeProcessGUI.setObjectName(_fromUtf8("QgsWpsDescribeProcessGUI"))
        QgsWpsDescribeProcessGUI.setWindowModality(QtCore.Qt.NonModal)
        QgsWpsDescribeProcessGUI.resize(800, 600)

        self.retranslateUi(QgsWpsDescribeProcessGUI)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDescribeProcessGUI)

    def retranslateUi(self, QgsWpsDescribeProcessGUI):
        QgsWpsDescribeProcessGUI.setWindowTitle(QtGui.QApplication.translate("QgsWpsDescribeProcessGUI", "Describe Process", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDescribeProcessGUI = QtGui.QDialog()
    ui = Ui_QgsWpsDescribeProcessGUI()
    ui.setupUi(QgsWpsDescribeProcessGUI)
    QgsWpsDescribeProcessGUI.show()
    sys.exit(app.exec_())

