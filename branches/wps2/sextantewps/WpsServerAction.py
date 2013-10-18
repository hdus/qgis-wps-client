"""
 /***************************************************************************
   QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at sourcepole dot ch

  ***************************************************************************
  *                                                                         *
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                         *
  ***************************************************************************/
"""
from sextante.gui.ToolboxAction import ToolboxAction
from sextante.core.Sextante import Sextante
from WpsAlgorithm import WpsAlgorithm
from wps2.wpslib.processdescription import ProcessDescription
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
