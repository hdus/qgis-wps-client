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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from wps2 import version,  date
#from wps import date

import webbrowser, os

from Ui_QgsWpsAbout import Ui_dlgAbout

class DlgAbout( QDialog, Ui_dlgAbout ):
    def __init__( self, iface=None ):
        QDialog.__init__( self )
        self.iface = iface
        self.setupUi( self )
        self.setWindowTitle('QGIS WPS-Client '+version())
        self.tabWidget.setCurrentIndex( 0 )
    
        # setup labels
        ver = version()
        dt = date()
        self.lblVersion.setText( self.tr("Version: ")+ver) 
        self.lblDate.setText( self.tr( "Date: ")+dt)
    
        # setup texts
        aboutString = "The goal of QgsWPS is to provide client to connect to any WPS-Server. " 
    
        contribString =  "<p><center><b>The following people contributed to QgsWPS:</b></center></p>" 
        contribString+= "<p>Horst Düster / Sourcepole (Maintainer)<br>" 
        contribString+= "Pirmin Kalberer / Sourcepole (Sextante Integration)<br>" 
        contribString+= "Germán Carrillo<br>" 
        contribString+= "Sören Gebbert<br>" 
        contribString+= "Eugeniy Nikulin<br>" 
        contribString+= "Marco Hugentobler / Sourcepole<br>" 
        contribString+= "Luca Delucchi<br>" 
        contribString+= "Alexander Bruy (About GUI) <br>" 
        contribString+="Robert Szczepanek (Icon) <br><br>"
        contribString+= "<b>and special thanks to the QGIS team</b></p>" 
        
        sponsorString =  "<p><center><b>The following people or institutions funded QgsWPS:</b></center></p><br<br>" 
        sponsorString+="Kanton Solothurn<br><br>"
        sponsorString+="Provincia di Terni - Ufficio Cave, Difesa del suolo, Protezione Civile e SIT <br>with the collaboration of Studio Associato GfosServices  <br>"
    
        licenseString = "LICENSING INFORMATION:\n\n"
        licenseString+="QgsWPS Plugin is copyright (C) 2009 Dr. Horst Duester\n\n"
        licenseString+="horst.duester@kappasys.ch\n\n"
        licenseString+="QgsWPS-Plugin icon is copyright (C) 2009 Robert Szczepanek\n\n"
        licenseString+="robert@szczepanek.pl\n\n"
        licenseString += "Licensed under the terms of GNU GPL 2.\n\n"
        licenseString+= "This program is free software; you can redistribute it and/or modify it under "
        licenseString+= "the terms of the GNU General Public License as published by the Free "
        licenseString+= "Software Foundation; either version 2 of the License, or (at your option) "
        licenseString+= "any later version.\n"
        licenseString+= "This code is distributed in the hope that it will be useful, but WITHOUT ANY "
        licenseString+= "WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS "
        licenseString+= "FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more "
        licenseString+= "details.\n"
        licenseString+= "A copy of the GNU General Public License is available on the World Wide Web "
        licenseString+= "at http://www.gnu.org/copyleft/gpl.html. You can also obtain it by writing "
        licenseString+= "to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, "
        licenseString+= "MA 02111-1307, USA."
    
        # write texts
        self.memAbout.setText( self.tr(aboutString ))
        self.memContrib.setText( self.tr(contribString ))
        self.memSponsoring.setText(self.tr(sponsorString))
        self.memAcknowl.setText( self.tr(licenseString ))
    
    
