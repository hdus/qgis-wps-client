# -*- coding: utf-8 -*-
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
        self.lblVersion.setText( self.tr( "Version: " )+ ver )
        self.lblDate.setText( self.tr( "Date: " )+ dt )
    
        # setup texts
        aboutString = pystring( "The goal of QgsWPS is to provide client to connect to any WPS-Server. " )
    
        contribString = pystring( "<p><center><b>The following people contributed to QgsWPS:</b></center></p>" )
        contribString += pystring(u"<p>Horst Düster (Maintainer) Sourcepole AG / Zürich<br>" )
        contribString += pystring(u"Pirmin Kalberer (Sextante Integration) Sourcepole AG / Zürich<br>" )
        contribString += pystring(u"Sandro Mani Sourcepole AG / Zürich<br>" )
        contribString += pystring( u"Germán Carrillo<br>" )        
        contribString += pystring( u"Sören Gebbert<br>" )
        contribString += pystring( "Eugeniy Nikulin<br>" )
        contribString += pystring( "Marco Hugentobler<br>" )
        contribString += pystring( "Luca Delucchi<br>" )
        contribString += pystring( "Enrico De Guidi<br>" )
        contribString += pystring( "Alexander Bruy (About GUI) <br>" )
        contribString += pystring("Robert Szczepanek (Icon) <br><br>")
        contribString += pystring( "<b>and special thanks to the QGIS team</b></p>" )
        
        sponsorString = pystring( "<p><center><b>The following people or institutions funded QgsWPS:</b></center></p><br<br>" )
        sponsorString += pystring(u"Sourcepole AG, Weberstrasse 5, CH-8004 Zürich<br><br>")        
        sponsorString += pystring("Provincia di Terni - Ufficio Cave, Difesa del suolo, Protezione Civile e SIT <br>with the collaboration of Studio Associato GfosServices  <br>")
    
        licenseString = pystring("LICENSING INFORMATION:\n\n")
        licenseString += pystring("QgsWPS Plugin is copyright (C) 2009 Dr. Horst Duester\n\n")
        licenseString += pystring("horst.duester@kappasys.ch\n\n")
        licenseString += pystring("QgsWPS-Plugin icon is copyright (C) 2009 Robert Szczepanek\n\n")
        licenseString += pystring("robert@szczepanek.pl\n\n")
        licenseString += pystring( "Licensed under the terms of GNU GPL 2.\n\n")
        licenseString += pystring( "This program is free software; you can redistribute it and/or modify it under ")
        licenseString += pystring( "the terms of the GNU General Public License as published by the Free ")
        licenseString += pystring( "Software Foundation; either version 2 of the License, or (at your option) ")
        licenseString += pystring( "any later version.\n")
        licenseString += pystring( "This code is distributed in the hope that it will be useful, but WITHOUT ANY ")
        licenseString += pystring( "WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS ")
        licenseString += pystring( "FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more ")
        licenseString += pystring( "details.\n")
        licenseString += pystring( "A copy of the GNU General Public License is available on the World Wide Web ")
        licenseString += pystring( "at http://www.gnu.org/copyleft/gpl.html. You can also obtain it by writing ")
        licenseString += pystring( "to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, ")
        licenseString += pystring( "MA 02111-1307, USA.")
    
        # write texts
        self.memAbout.setText( self.tr(aboutString ))
        self.memContrib.setText( self.tr(contribString ))
        self.memSponsoring.setText(self.tr(sponsorString))
        self.memAcknowl.setText( self.tr(licenseString ))
    
    
