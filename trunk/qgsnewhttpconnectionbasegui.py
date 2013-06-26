# -*- coding: latin1 -*-
"""
***************************************************************************
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
  ***************************************************************************
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from wps import version
from Ui_qgsnewhttpconnectionbase import Ui_QgsNewHttpConnectionBase
from qgswpsgui import QgsWpsGui
from urlparse import urlparse
import os, sys, string

class QgsNewHttpConnectionBaseGui(QDialog,  QObject, Ui_QgsNewHttpConnectionBase):
  MSG_BOX_TITLE = "WPS"
  
  def __init__(self, parent, fl):
    QDialog.__init__(self, parent, fl)
    self.parent = parent
    self.flags = fl
    self.setupUi(self)
    self.setWindowTitle('QGIS WPS-Client '+version())
    
  @pyqtSignature("on_buttonBox_accepted()")       
  def on_buttonBox_accepted(self):
    settings = QSettings()
    myURL = urlparse(str(self.txtUrl.text()))
    mySettings = "/WPS/"+self.txtName.text()
#    settings.setValue("WPS/connections/selected", QVariant(name) )
    settings.setValue(mySettings+"/scheme",  QVariant(myURL.scheme))
    settings.setValue(mySettings+"/server",  QVariant(myURL.netloc))
    settings.setValue(mySettings+"/path", QVariant(myURL.path))
    settings.setValue(mySettings+"/method",QVariant("GET"))
    settings.setValue(mySettings+"/version",QVariant("1.0.0"))
    settings.setValue(mySettings+"/url",QVariant(self.txtUrl.text()))
    
    self.parent.initQgsWpsGui()    
