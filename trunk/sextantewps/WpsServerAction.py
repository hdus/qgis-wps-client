from sextante.gui.ToolboxAction import ToolboxAction
from sextante.core.Sextante import Sextante
from WpsAlgorithm import WpsAlgorithm
from wps.wpslib.processdescription import ProcessDescription
import os
from PyQt4 import QtGui
from PyQt4.QtCore import *

class WpsServerAction(ToolboxAction):

    def __init__(self, server):
        self.server = server
        self.processalgs = []
        self.name = "Load processes from server"
        self.group = WpsAlgorithm.groupName(server)

    def execute(self):
        QObject.connect(self.server, SIGNAL("capabilitiesRequestFinished"), self._capabilitiesRequestFinished)
        self.server.requestCapabilities()

    def _capabilitiesRequestFinished(self):
        self.processalgs = []
        self.server.parseCapabilitiesXML()
        for process in self.server.processes:
            self.processalgs.append( WpsAlgorithm(process) )
        Sextante.updateAlgsList()
