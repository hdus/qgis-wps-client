# -*- coding: utf-8 -*-

"""
Module implementing DialogQgsWpsErrorMsg.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
from wps import version

from Ui_qgswpserrormsggui import Ui_Dialog

class QgsWpsErrorMsgGui(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('QGIS WPS-Client '+version())
        
    def on_buttonBox_rejected(self):
        self.close()
