# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home_nas/sogis/barpadue/.qgis/python/plugins/wps/qgswpsdescribeprocessgui.ui'
#
# Created: Wed Dec  8 10:42:15 2010
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QgsWpsDescribeProcessGUI(object):
    def setupUi(self, QgsWpsDescribeProcessGUI):
        QgsWpsDescribeProcessGUI.setObjectName("QgsWpsDescribeProcessGUI")
        QgsWpsDescribeProcessGUI.setWindowModality(QtCore.Qt.NonModal)
        QgsWpsDescribeProcessGUI.resize(800, 600)

        self.retranslateUi(QgsWpsDescribeProcessGUI)
        QtCore.QMetaObject.connectSlotsByName(QgsWpsDescribeProcessGUI)

    def retranslateUi(self, QgsWpsDescribeProcessGUI):
        QgsWpsDescribeProcessGUI.setWindowTitle(QtGui.QApplication.translate("QgsWpsDescribeProcessGUI", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QgsWpsDescribeProcessGUI = QtGui.QDialog()
    ui = Ui_QgsWpsDescribeProcessGUI()
    ui.setupUi(QgsWpsDescribeProcessGUI)
    QgsWpsDescribeProcessGUI.show()
    sys.exit(app.exec_())

