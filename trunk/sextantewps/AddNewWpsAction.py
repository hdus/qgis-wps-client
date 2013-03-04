from sextante.script.EditScriptDialog import EditScriptDialog
from sextante.gui.ToolboxAction import ToolboxAction
import os
from PyQt4 import QtGui

class AddNewWpsAction(ToolboxAction):

    def __init__(self, wpsDockWidget):
        self.name="Add new WPS"
        self.group="Tools"
        self.wpsDockWidget = wpsDockWidget

    def getIcon(self):
        return QtGui.QIcon(os.path.dirname(__file__) + "/../images/script.png")

    def execute(self):
        self.wpsDockWidget.on_btnConnect_clicked()
        #self.toolbox.updateTree()
