# -*- coding: latin1 -*-
"""
 /***************************************************************************
   qgswps.py QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

  ***************************************************************************
  *                                                                         *
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                          *
  ***************************************************************************/
"""
# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from QgsWpsDockWidget import QgsWpsDockWidget
from wps import version
import sys,  os,  inspect

# initialize Qt resources from file resources.py
import resources_rc

try:
    from sextante.core.Sextante import Sextante
    from wps_sextante.WpsAlgorithmProvider import WpsAlgorithmProvider
    SEXTANTE=True
except:
    SEXTANTE=False
#   
cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)   


DEBUG = False

# Our main class for the plugin
class QgsWps:
  MSG_BOX_TITLE = "WPS Client"
  
  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface  
    self.localePath = ""
    
    if SEXTANTE:
        self.provider = WpsAlgorithmProvider()
    
    #Initialise the translation environment    
    userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path()+"/python/plugins/wps"  
    systemPluginPath = QgsApplication.prefixPath()+"/share/qgis/python/plugins/wps"
    myLocaleName = QSettings().value("locale/userLocale").toString()
    myLocale = myLocaleName[0:2]
    if QFileInfo(userPluginPath).exists():
      self.pluginPath = userPluginPath
      self.localePath = userPluginPath+"/i18n/wps_"+myLocale+".qm"
    elif QFileInfo(systemPluginPath).exists():
      self.pluginPath = systemPluginPath
      self.localePath = systemPluginPath+"/i18n/wps_"+myLocale+".qm"

    if QFileInfo(self.localePath).exists():
      self.translator = QTranslator()
      self.translator.load(self.localePath)
      
      if qVersion() > '4.3.3':        
        QCoreApplication.installTranslator(self.translator)  
        

  ##############################################################################

  def initGui(self):
 
     if SEXTANTE:
         Sextante.addProvider(self.provider)
        
    # Create action that will start plugin configuration
     self.action = QAction(QIcon(":/plugins/wps/images/wps-add.png"), "WPS Client", self.iface.mainWindow())
     QObject.connect(self.action, SIGNAL("triggered()"), self.run)
         
    # Add toolbar button and menu item
     self.iface.addToolBarIcon(self.action)
     self.iface.addPluginToMenu("WPS", self.action)
     
     self.myDockWidget = QgsWpsDockWidget(self.iface)
     self.myDockWidget.setWindowTitle('QGIS WPS-Client '+version())
     self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.myDockWidget)
     self.myDockWidget.show()



  ##############################################################################

  def unload(self):
      
    if SEXTANTE:
        Sextante.removeProvider(self.provider)      
        
    self.iface.removePluginMenu("WPS", self.action)
    self.iface.removeToolBarIcon(self.action)
    
    if self.myDockWidget:
        self.myDockWidget.close()
        
    self.myDockWidget = None

##############################################################################

  def run(self):  
    if self.myDockWidget.isVisible():
        self.myDockWidget.hide()
    else:
        self.myDockWidget.show()

