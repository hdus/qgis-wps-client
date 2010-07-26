# -*- coding: latin1 -*-
from qgswps import QgsWps
def name():
  return "WPS"
def description():
  return "Client for Web Processing Services"
def version():
  return "Version 0.3.32"
def qgisMinimumVersion():
  return "1.4"  
def classFactory(iface):
  return QgsWps(iface)  
