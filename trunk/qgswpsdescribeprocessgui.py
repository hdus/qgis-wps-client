# -*- coding: latin1 -*-
"""
***************************************************************************
   qgswps.py QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright            : (C) 2009 by Dr. Horst Duester
 email                : horst dot duester at kappasys dot ch

 Authors              : Dr. Horst Duester

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
from ui_qgswpsdescribeprocess import Ui_QgsWpsDescribeProcessGUI
import os, sys, string

class QgsWpsDescribeProcessGui(QDialog, QObject, Ui_QgsWpsDescribeProcessGUI):
  MSG_BOX_TITLE = "QGIS WPS Client"
  
  def __init__(self, parent, fl):
    QDialog.__init__(self, parent, fl)
    self.setupUi(self)

  @pyqtSignature("on_btnOk_clicked()")    
  def on_btnAbbrechen_clicked(self):
    self.close()

  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  @pyqtSignature("on_btnOk_clicked()")          
  def on_btnOk_clicked(self):
    self.close()
               
