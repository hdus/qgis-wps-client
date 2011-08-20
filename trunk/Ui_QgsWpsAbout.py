# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hdus/.qgis/python/plugins/wps/QgsWpsAbout.ui'
#
# Created: Sat Aug 20 15:14:54 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_dlgAbout(object):
    def setupUi(self, dlgAbout):
        dlgAbout.setObjectName("dlgAbout")
        dlgAbout.resize(686, 477)
        self.gridLayout = QtGui.QGridLayout(dlgAbout)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtGui.QWidget(dlgAbout)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setMaximumSize(QtCore.QSize(180, 16777215))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblVersion = QtGui.QLabel(self.widget)
        self.lblVersion.setMaximumSize(QtCore.QSize(16777215, 14))
        self.lblVersion.setObjectName("lblVersion")
        self.verticalLayout.addWidget(self.lblVersion)
        self.lblDate = QtGui.QLabel(self.widget)
        self.lblDate.setMaximumSize(QtCore.QSize(16777215, 14))
        self.lblDate.setObjectName("lblDate")
        self.verticalLayout.addWidget(self.lblDate)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(dlgAbout)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.memAbout = QtGui.QTextEdit(self.tab)
        self.memAbout.setUndoRedoEnabled(False)
        self.memAbout.setReadOnly(True)
        self.memAbout.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.memAbout.setObjectName("memAbout")
        self.gridLayout_2.addWidget(self.memAbout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.memContrib = QtGui.QTextEdit(self.tab_3)
        self.memContrib.setUndoRedoEnabled(False)
        self.memContrib.setReadOnly(True)
        self.memContrib.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.memContrib.setObjectName("memContrib")
        self.gridLayout_3.addWidget(self.memContrib, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_4 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.memAcknowl = QtGui.QTextEdit(self.tab_2)
        self.memAcknowl.setUndoRedoEnabled(False)
        self.memAcknowl.setReadOnly(True)
        self.memAcknowl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.memAcknowl.setObjectName("memAcknowl")
        self.gridLayout_4.addWidget(self.memAcknowl, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)

        self.retranslateUi(dlgAbout)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dlgAbout.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dlgAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgAbout)

    def retranslateUi(self, dlgAbout):
        dlgAbout.setWindowTitle(QtGui.QApplication.translate("dlgAbout", "About QgsWPS", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVersion.setText(QtGui.QApplication.translate("dlgAbout", "Version:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("dlgAbout", "Date:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("dlgAbout", "About QgsWPS", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("dlgAbout", "Contributors", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("dlgAbout", "License", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlgAbout = QtGui.QDialog()
    ui = Ui_dlgAbout()
    ui.setupUi(dlgAbout)
    dlgAbout.show()
    sys.exit(app.exec_())

