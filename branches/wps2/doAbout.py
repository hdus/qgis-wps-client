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
from wps import version,  date
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
        self.lblVersion.setText( self.tr( "Version: %1" ).arg( ver ) )
        self.lblDate.setText( self.tr( "Date: %1" ).arg( dt ) )
    
        # setup texts
        aboutString = QString( "The goal of QgsWPS is to provide client to connect to any WPS-Server. " )
    
        contribString = QString( "<p><center><b>The following people contributed to QgsWPS:</b></center></p>" )
        contribString.append( "<p>Horst Düster (Maintainer)<br>" )
        contribString.append( "Pirmin Kalberer (Sextante Integration)<br>" )
        contribString.append( "Germán Carrillo<br>" )        
        contribString.append( "Sören Gebbert<br>" )
        contribString.append( "Eugeniy Nikulin<br>" )
        contribString.append( "Marco Hugentobler<br>" )
        contribString.append( "Luca Delucchi<br>" )
        contribString.append( "Alexander Bruy (About GUI) <br>" )
        contribString.append("Robert Szczepanek (Icon) <br><br>")
        contribString.append( "<b>and special thanks to the QGIS team</b></p>" )
        
        sponsorString = QString( "<p><center><b>The following people or institutions funded QgsWPS:</b></center></p><br<br>" )
        sponsorString.append("Kanton Solothurn<br><br>")        
        sponsorString.append("Provincia di Terni - Ufficio Cave, Difesa del suolo, Protezione Civile e SIT <br>with the collaboration of Studio Associato GfosServices  <br>")
    
        licenseString = QString("LICENSING INFORMATION:\n\n")
        licenseString.append("QgsWPS Plugin is copyright (C) 2009 Dr. Horst Duester\n\n")
        licenseString.append("horst.duester@kappasys.ch\n\n")
        licenseString.append("QgsWPS-Plugin icon is copyright (C) 2009 Robert Szczepanek\n\n")
        licenseString.append("robert@szczepanek.pl\n\n")
        licenseString .append( "Licensed under the terms of GNU GPL 2.\n\n")
        licenseString.append( "This program is free software; you can redistribute it and/or modify it under ")
        licenseString.append( "the terms of the GNU General Public License as published by the Free ")
        licenseString.append( "Software Foundation; either version 2 of the License, or (at your option) ")
        licenseString.append( "any later version.\n")
        licenseString.append( "This code is distributed in the hope that it will be useful, but WITHOUT ANY ")
        licenseString.append( "WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS ")
        licenseString.append( "FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more ")
        licenseString.append( "details.\n")
        licenseString.append( "A copy of the GNU General Public License is available on the World Wide Web ")
        licenseString.append( "at http://www.gnu.org/copyleft/gpl.html. You can also obtain it by writing ")
        licenseString.append( "to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, ")
        licenseString.append( "MA 02111-1307, USA.")
    
        # write texts
        self.memAbout.setText( self.tr(aboutString ))
        self.memContrib.setText( self.tr(contribString ))
        self.memSponsoring.setText(self.tr(sponsorString))
        self.memAcknowl.setText( self.tr(licenseString ))
    
    
