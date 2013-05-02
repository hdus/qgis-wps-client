from sextante.gui.ToolboxAction import ToolboxAction
from sextante.core.Sextante import Sextante
import os
from PyQt4 import QtGui
from PyQt4.QtCore import *

class AddNewWpsAction(ToolboxAction):

    def __init__(self, wpsDockWidget):
        self.name="Connect to WPS servers"
        self.group="Tools"
        self.wpsDockWidget = wpsDockWidget
        QObject.connect(wpsDockWidget, SIGNAL("bookmarksChanged()"), Sextante.updateAlgsList)

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/script.png")

    def execute(self):
        self.wpsDockWidget.on_btnConnect_clicked()
