# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ApiCompat
                                 A QGIS plugin
 API compatibility layer
                              -------------------
        begin                : 2013-07-02
        copyright            : (C) 2013 by Pirmin Kalberer, Sourcepole
        email                : pka@sourcepole.ch

        Modified             : 2025-10-22 by [Herve Squividant]
        Description          : Updated for PyQt5+ compatibility. 
                               Seems to work with at least version 3.44 of QGis.
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify *
 *   it under the terms of the GNU General Public License as published by *
 *   the Free Software Foundation; either version 2 of the License, or    *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import builtins
import qgis.PyQt.QtCore  # Ensures PyQt5/Qt environment is available

# -----------------------------------------------------------------------------
# Function: sipv1
# Purpose: Detect whether the legacy SIP API v1 is in use (used in PyQt4)
# In PyQt5 and later, sip.getapi('QVariant') raises a ValueError because
# 'QVariant' API no longer exists. We catch the exception to handle this gracefully.
# -----------------------------------------------------------------------------
def sipv1():
    try:
        import sip
        # Only available in PyQt4; will raise ValueError in PyQt5+
        return sip.getapi("QVariant") == 1
    except (AttributeError, ValueError):
        # In PyQt5+, assume SIP API v2 is active
        return False

# Make the function globally available to other plugin modules
builtins.sipv1 = sipv1

# Import appropriate compatibility layer depending on SIP API version
if sipv1():
    from .sipv1 import compat
    from .sipv1 import vectorapi
else:
    from .sipv2 import compat
