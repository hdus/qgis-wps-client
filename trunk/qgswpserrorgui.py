# -*- coding: utf-8 -*-

"""
Module implementing ErrorGUI.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Ui_qgswpserrorgui import Ui_Dialog


class ErrorGUI(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        QMessageBox.information(None, '', 'Hallo')

    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
