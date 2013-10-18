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
