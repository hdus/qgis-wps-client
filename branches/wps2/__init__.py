# -*- coding: latin1 -*-
"""
***************************************************************************
   qgswps.py QGIS Web Processing Service Plugin
  -------------------------------------------------------------------
 Date                 : 09 November 2009
 Copyright         : (C) 2009 by Dr. Horst Duester
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
def name():
  return "WPS-Client"
  
def description():
  return "Client for Web Processing Services"

def version():
  return "1.0.3"

def qgisMinimumVersion():
  return "1.5"  
  
def qgisMaximumVersion():
  return "1.9"    

def date():
    return '2013-10-04'
    
def email():
    return 'horst.duester@kappasys.ch'
    
def author():
  return "Dr. Horst Duester / Sourcepole AG Zurich"
  
def icon():
	return "images/wps-add.png"   

def homepage():
  return "http://www.kappasys.ch"
  
def classFactory(iface):
  from qgswps import QgsWps
  return QgsWps(iface)  
