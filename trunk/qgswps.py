# -*- coding: latin1 -*-
"""
 /***************************************************************************
   QGIS Web Processing Service Plugin
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
  *                                                                         *
  ***************************************************************************/
"""
# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from QgsWpsDockWidget import QgsWpsDockWidget
from wps import version
from doAbout import DlgAbout

SEXTANTE_SUPPORT = False
try:
    from sextante.core.Sextante import Sextante
    from wps.sextantewps.WpsAlgorithmProvider import WpsAlgorithmProvider
    SEXTANTE_SUPPORT = True
except ImportError:
    pass

# initialize Qt resources from file resources.py
import resources_rc


DEBUG = False

# Our main class for the plugin
class QgsWps:
  MSG_BOX_TITLE = "WPS Client"
  
  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface  
    self.localePath = ""
    
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
 
    # Create action that will start plugin configuration
     self.action = QAction(QIcon(":/plugins/wps/images/wps-add.png"), "WPS-Client", self.iface.mainWindow())
     QObject.connect(self.action, SIGNAL("triggered()"), self.run)
     
     self.actionAbout = QAction("About", self.iface.mainWindow())
     QObject.connect(self.actionAbout, SIGNAL("triggered()"), self.doAbout)
         
    # Add toolbar button and menu item
     self.iface.addToolBarIcon(self.action)
     
     if hasattr(self.iface,  "addPluginToWebMenu"):
         self.iface.addPluginToWebMenu("WPS-Client", self.action)
         self.iface.addPluginToWebMenu("WPS-Client", self.actionAbout)
     else:
         self.iface.addPluginToMenu("WPS", self.action)
         self.iface.addPluginToWebMenu("WPS", self.action)

     
     self.myDockWidget = QgsWpsDockWidget(self.iface)
     self.myDockWidget.setWindowTitle('WPS')
     self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.myDockWidget)
     self.myDockWidget.show()

     if SEXTANTE_SUPPORT:
         self.provider = WpsAlgorithmProvider(self.myDockWidget)
     else:
         self.provider = None

     if self.provider:
        try:
            Sextante.addProvider(self.provider, True) #Force tree update
        except TypeError:
            Sextante.addProvider(self.provider)



  ##############################################################################

  def unload(self):
     if hasattr(self.iface,  "addPluginToWebMenu"):
         self.iface.removePluginWebMenu("WPS-Client", self.action)
         self.iface.removePluginWebMenu("WPS-Client", self.actionAbout)
     else:
         self.iface.removePluginToMenu("WPS", self.action)      
         self.iface.removePluginToMenu("WPS", self.actionAbout)
         
     self.iface.removeToolBarIcon(self.action)
    
     if self.myDockWidget:
         self.myDockWidget.close()
        
     self.myDockWidget = None

     if self.provider:
        Sextante.removeProvider(self.provider)

##############################################################################

  def run(self):  
    if self.myDockWidget.isVisible():
        self.myDockWidget.hide()
    else:
        self.myDockWidget.show()
        
  def doAbout(self):
      self.dlgAbout = DlgAbout()
      self.dlgAbout.show()

