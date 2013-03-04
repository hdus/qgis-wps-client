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
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from qgis.core import QgsNetworkAccessManager
from collections import namedtuple


# Process description example:
#
#<?xml version="1.0" encoding="utf-8"?>
#<wps:ProcessDescriptions xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd" service="WPS" version="1.0.0" xml:lang="eng">
#    <ProcessDescription wps:processVersion="1.0" storeSupported="true" statusSupported="true">
#        <ows:Identifier>returner</ows:Identifier>
#        <ows:Title>Return process</ows:Title>
#        <ows:Abstract>This is demonstration process of PyWPS, returns the same file, it gets on input, as the output.</ows:Abstract>
#        <DataInputs>
#            <Input minOccurs="1" maxOccurs="1">
#                <ows:Identifier>text</ows:Identifier>
#                <ows:Title>Some width</ows:Title>
#                <LiteralData>
#                    <ows:DataType ows:reference="http://www.w3.org/TR/xmlschema-2/#string">string</ows:DataType>
#                    <ows:AnyValue />
#                </LiteralData>
#            </Input>
#            <Input minOccurs="1" maxOccurs="1">
#                <ows:Identifier>data</ows:Identifier>
#                <ows:Title>Input vector data</ows:Title>
#                <ComplexData>
#                    <Default>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Default>
#                    <Supported>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Supported>
#                </ComplexData>
#            </Input>
#        </DataInputs>
#        <ProcessOutputs>
#            <Output>
#                <ows:Identifier>output2</ows:Identifier>
#                <ows:Title>Output vector data</ows:Title>
#                <ComplexOutput>
#                    <Default>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Default>
#                    <Supported>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Supported>
#                </ComplexOutput>
#            </Output>
#            <Output>
#                <ows:Identifier>text</ows:Identifier>
#                <ows:Title>Output literal data</ows:Title>
#                <LiteralOutput>
#                    <ows:DataType ows:reference="http://www.w3.org/TR/xmlschema-2/#integer">integer</ows:DataType>
#                </LiteralOutput>
#            </Output>
#            <Output>
#                <ows:Identifier>output1</ows:Identifier>
#                <ows:Title>Output vector data</ows:Title>
#                <ComplexOutput>
#                    <Default>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Default>
#                    <Supported>
#                        <Format>
#                            <ows:MimeType>text/xml</ows:MimeType>
#                        </Format>
#                    </Supported>
#                </ComplexOutput>
#            </Output>
#        </ProcessOutputs>
#    </ProcessDescription>
#</wps:ProcessDescriptions>

# All supported import raster formats
RASTER_MIMETYPES = [{"MIMETYPE":"image/tiff", "GDALID":"GTiff", "EXTENSION":"tif"},
                           {"MIMETYPE":"image/png", "GDALID":"PNG", "EXTENSION":"png"}, \
                           {"MIMETYPE":"image/gif", "GDALID":"GIF", "EXTENSION":"gif"}, \
                           {"MIMETYPE":"image/jpeg", "GDALID":"JPEG", "EXTENSION":"jpg"}, \
                           {"MIMETYPE":"image/geotiff", "GDALID":"GTiff", "EXTENSION":"tif"}, \
                           {"MIMETYPE":"application/x-erdas-hfa", "GDALID":"HFA", "EXTENSION":""}, \
                           {"MIMETYPE":"application/netcdf", "GDALID":"netCDF", "EXTENSION":""}, \
                           {"MIMETYPE":"application/x-netcdf", "GDALID":"netCDF", "EXTENSION":""}, \
                           {"MIMETYPE":"application/geotiff", "GDALID":"GTiff", "EXTENSION":"tif"}, \
                           {"MIMETYPE":"application/x-geotiff", "GDALID":"GTiff", "EXTENSION":"tif"}, \
                           {"MIMETYPE":"application/x-esri-ascii-grid", "GDALID":"AAIGrid", "EXTENSION":"asc"}, \
                           {"MIMETYPE":"application/image-ascii-grass", "GDALID":"GRASSASCIIGrid", "EXTENSION":"asc"}]
# All supported input vector formats [mime type, schema]
VECTOR_MIMETYPES = [{"MIMETYPE":"application/x-zipped-shp", "SCHEMA":"", "GDALID":"ESRI Shapefile", "DATATYPE":"SHP", "EXTENSION":"zip"}, \
                           {"MIMETYPE":"application/vnd.google-earth.kml+xml", "SCHEMA":"KML", "GDALID":"KML", "DATATYPE":"KML", "EXTENSION":"kml"}, \
                           {"MIMETYPE":"text/xml", "SCHEMA":"GML", "GDALID":"GML", "DATATYPE":"GML", "EXTENSION":"gml"}, \
                           {"MIMETYPE":"text/xml; subtype=gml/2.", "SCHEMA":"GML2", "GDALID":"GML", "DATATYPE":"GML2", "EXTENSION":"gml"}, \
                           {"MIMETYPE":"text/xml; subtype=gml/3.", "SCHEMA":"GML3", "GDALID":"GML", "DATATYPE":"GML3", "EXTENSION":"gml"}, \
                           {"MIMETYPE":"application/json", "SCHEMA":"JSON", "GDALID":"GEOJSON", "DATATYPE":"JSON", "EXTENSION":"json"}, \
                           {"MIMETYPE":"application/geojson", "SCHEMA":"GEOJSON", "GDALID":"GEOJSON", "DATATYPE":"GEOJSON", "EXTENSION":"geojson"}]
# mimeTypes for streaming
PLAYLIST_MIMETYPES = [{"MIMETYPE":"application/x-ogc-playlist+", "SCHEMA":"", "GDALID":"", "DATATYPE":"PLAYLIST", "EXTENSION":"txt"}]


# Helper methods for reading WPS XML

def getOwsElement(element, name):
    return element.elementsByTagNameNS("http://www.opengis.net/ows/1.1", name)

def getIdentifierTitleAbstractFromElement(element):
    identifier = getOwsElement(element, "Identifier").at(0).toElement().text().simplified()
    title = getOwsElement(element, "Title").at(0).toElement().text().simplified()
    abstract = getOwsElement(element, "Abstract").at(0).toElement().text().simplified()
    return identifier, title, abstract

def getDefaultMimeType(inElement):
    myElement = inElement.elementsByTagName("Default").at(0).toElement()
    return getMimeTypeSchemaEncoding(myElement)

def getSupportedMimeTypes(inElement):
    mimeTypes = []
    myElements = inElement.elementsByTagName("Supported").at(0).toElement()
    myFormats = myElements.elementsByTagName('Format')
    for i in range(myFormats.size()):
      myElement = myFormats.at(i).toElement()
      mimeTypes.append(getMimeTypeSchemaEncoding(myElement))
    return mimeTypes

def getMimeTypeSchemaEncoding(element):
    mimeType = ""
    schema = ""
    encoding = ""
    try:
        mimeType = str(element.elementsByTagName("MimeType").at(0).toElement().text().simplified().toLower())
        schema = str(element.elementsByTagName("Schema").at(0).toElement().text().simplified().toLower())
        encoding = str(element.elementsByTagName("Encoding").at(0).toElement().text().simplified().toLower())
    except:
        pass

    return {"MimeType":mimeType, "Schema":schema, "Encoding":encoding}

def isMimeTypeRaster(mimeType, ignorePlaylist = False):
    """Check for raster input"""
    if not ignorePlaylist:
      if isMimeTypePlaylist(mimeType) != None:
        return None

    for rasterType in RASTER_MIMETYPES:
        if rasterType["MIMETYPE"] in mimeType.lower():
          return rasterType["GDALID"]
    return None

def isMimeTypeVector(mimeType, ignorePlaylist = False):
    """Check for vector input. Zipped shapefiles must be extracted"""
    if not ignorePlaylist:
      if isMimeTypePlaylist(mimeType) != None:
        return None

    for vectorType in VECTOR_MIMETYPES:
        if vectorType["MIMETYPE"] in mimeType.lower():
          return vectorType["GDALID"]
    return None

def isMimeTypeText(mimeType):
    """Check for text file input"""
    if mimeType.upper() == "TEXT/PLAIN":
       return "TXT"
    else:
       return None

def isMimeTypeFile(mimeType):
    """Check for file output"""
    for fileType in FILE_MIMETYPES: # TODO define FILE_MIMETYPES, sometimes it yields errors
        if mimeType.upper() == fileType["MIMETYPE"]:
          return "ZIP"
    return None

def isMimeTypePlaylist(mimeType):
    """Check for playlists"""
    for playlistType in PLAYLIST_MIMETYPES:
        if playlistType["MIMETYPE"] in mimeType.lower():
          return playlistType["DATATYPE"]
    return None

def getBaseMimeType(dataType):
    # Return a base mimeType (might not be completed) from a data type (e.g.GML2)
    for vectorType in VECTOR_MIMETYPES:
      if vectorType["DATATYPE"] == dataType.upper():
        return vectorType["MIMETYPE"]
    return None

def getFileExtension(mimeType):
    # Return the extension associated to the mime type (e.g. tif)

    if isMimeTypeVector(mimeType):
      for vectorType in VECTOR_MIMETYPES:
        if vectorType["MIMETYPE"] in mimeType.lower():
          return "." + vectorType["EXTENSION"]

    elif isMimeTypeRaster(mimeType):
      for rasterType in RASTER_MIMETYPES:
        if rasterType["MIMETYPE"] in mimeType.lower():
          return "." + rasterType["EXTENSION"]

    return ""

def getOGRVersion():
  # Data conversion options might vary according to the OGR version
  try:
    import osgeo.gdal
    return int(osgeo.gdal.VersionInfo())
  except:
    return 0 # If not accessible, assume it is 0

def isGML3SupportedByOGR():
  # GDAL/OGR versions <= 1800 don't support the FORMAT=GML3 option
  version = getOGRVersion()
  if version < 1800: # OGR < 1.8.0
     return False
  else:
     return True

def allowedValues(aValues):
     valList = []

     # Manage a value list defined by a range
     value_element = aValues.at(0).toElement()
     v_range_element = getOwsElement(value_element, "Range")

     if v_range_element.size() > 0:
       min_val = getOwsElement(value_element, "MinimumValue").at(0).toElement().text()
       max_val = getOwsElement(value_element, "MaximumValue").at(0).toElement().text()

       try:
          for n in range(int(min_val), int(max_val) + 1):
              myVal = QString()
              myVal.append(str(n))
              valList.append(myVal)
       except:
           QMessageBox.critical(None, QApplication.translate("QgsWps", "Error"), QApplication.translate("QgsWps", "Maximum allowed Value is too large"))

     # Manage a value list defined by single values
     v_element = getOwsElement(value_element, "Value")
     if v_element.size() > 0:
       for n in range(v_element.size()):
         mv_element = v_element.at(n).toElement()
         valList.append(unicode(mv_element.text(), 'latin1').strip())

     return valList


StringInput = namedtuple('StringInput', 'identifier title minOccurs')
SelectionInput = namedtuple('SelectionInput', 'identifier title valList')
VectorInput = namedtuple('VectorInput', 'identifier title minOccurs dataFormat')
MultipleVectorInput = namedtuple('MultipleVectorInput', 'identifier title minOccurs dataFormat')
RasterInput = namedtuple('RasterInput', 'identifier title minOccurs dataFormat')
MultipleRasterInput = namedtuple('MultipleRasterInput', 'identifier title minOccurs dataFormat')
ExtentInput = namedtuple('ExtentInput', 'identifier title minOccurs')
CrsInput = namedtuple('CrsInput', 'identifier title minOccurs crsListe')
VectorOutput = namedtuple('VectorOutput', 'identifier title dataFormat')


class ProcessDescription(QObject):
    """
    Request and parse a WPS process description
    """

    def __init__(self):
        QObject.__init__(self)

    def requestDescribeProcess(self, baseUrl, identifier, version):
        """
        Request process description
        """
        self.doc = None
        self.inputs = []
        self.outputs = []

        url = QUrl()
        myRequest = "?Request=DescribeProcess&identifier=" + identifier + "&Service=WPS&Version=" + version
        url.setUrl(baseUrl + myRequest)
        myHttp = QgsNetworkAccessManager.instance()
        self._theReply = myHttp.get(QNetworkRequest(url))
        self._theReply.finished.connect(self._describeProcessFinished)

    @pyqtSlot()
    def _describeProcessFinished(self):
        # Receive the XML process description
        self.processUrl = self._theReply.url()
        self.processXML = self._theReply.readAll().data()
        self.doc = QtXml.QDomDocument()
        self.doc.setContent(self.processXML, True)

        self.identifier, self.title, self.abstract = getIdentifierTitleAbstractFromElement(self.doc)
        self._parseProcessInputs()
        self._parseProcessOutputs()

        self.emit(SIGNAL("describeProcessFinished"))

    def _parseProcessInputs(self):
        """
        Populate self.inputs and self.outputs arrays from process description
        """
        self._inputsMetaInfo = {} # dictionary for input metainfo, key is the input identifier
        dataInputs = self.doc.elementsByTagName("Input")

        # Create the complex inputs at first
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()

          inputIdentifier, title, abstract = getIdentifierTitleAbstractFromElement(f_element)

          complexData = f_element.elementsByTagName("ComplexData")
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))

          # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
          if complexData.size() > 0:
            # Das i-te ComplexData Objekt auswerten
            complexDataTypeElement = complexData.at(0).toElement()
            supportedComplexDataFormat = getSupportedMimeTypes(complexDataTypeElement)
            complexDataFormat = getDefaultMimeType(complexDataTypeElement)

            # Store the input formats
            self._inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat

            # Attach the selected vector or raster maps
            if isMimeTypeVector(complexDataFormat["MimeType"]) != None:

              # Since it is a vector, choose an appropriate GML version
              complexDataFormat = self.getSupportedGMLDataFormat(inputIdentifier)

              if complexDataFormat == None :
                QMessageBox.warning(self.iface.mainWindow(), QApplication.translate("QgsWps", "Error"),
                  QApplication.translate("QgsWps", "The process '%1' does not seem to support GML for the parameter '%2', which is required by the QGIS WPS client.").arg(self.processIdentifier).arg(inputIdentifier))
                return 0

              # Vector inputs
              if maxOccurs == 1:
                self.inputs.append(VectorInput(inputIdentifier, title, minOccurs, complexDataFormat))
              else:
                self.inputs.append(MultipleVectorInput(inputIdentifier, title, minOccurs, complexDataFormat))
            elif isMimeTypeText(complexDataFormat["MimeType"]) != None:
              # Text inputs
              self.inputs.append(StringInput(inputIdentifier, title))
            elif isMimeTypeRaster(complexDataFormat["MimeType"]) != None:

              # Raster inputs
              if maxOccurs == 1:
                self.inputs.append(RasterInput(inputIdentifier, title, minOccurs, complexDataFormat))
              else:
                self.inputs.append(MultipleRasterInput(inputIdentifier, title, minOccurs, complexDataFormat))

            elif isMimeTypePlaylist(complexDataFormat["MimeType"]) != None:
              # Playlist (text) inputs
              self.inputs.append(StringInput(inputIdentifier, title, minOccurs, complexDataFormat))

            else:
              # We assume text inputs in case of an unknown mime type
              self.inputs.append(StringInput(inputIdentifier, title, minOccurs))

        # Create the literal inputs as second
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()

          inputIdentifier, title, abstract = getIdentifierTitleAbstractFromElement(f_element)

          literalData = f_element.elementsByTagName("LiteralData")
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))

          if literalData.size() > 0:
            allowedValuesElement = literalData.at(0).toElement()
            aValues = getOwsElement(allowedValuesElement, "AllowedValues")
            dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
            if aValues.size() > 0:
              valList = allowedValues(aValues)
              if len(valList) > 0:
                if len(valList[0]) > 0:
                    self.inputs.append(SelectionInput(inputIdentifier, title, valList))
                else:
                    self.inputs.append(StringInput(inputIdentifier, title, minOccurs))
            else:
                self.inputs.append(StringInput(inputIdentifier, title, minOccurs))

        # At last, create the bounding box inputs
        for i in range(dataInputs.size()):
          f_element = dataInputs.at(i).toElement()

          inputIdentifier, title, abstract = getIdentifierTitleAbstractFromElement(f_element)

          bBoxData = f_element.elementsByTagName("BoundingBoxData")
          minOccurs = int(f_element.attribute("minOccurs"))
          maxOccurs = int(f_element.attribute("maxOccurs"))

          if bBoxData.size() > 0:
            crsListe = []
            bBoxElement = bBoxData.at(0).toElement()
            defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
            defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href")
            crsListe.append(defaultCrs)

            self.inputs.append(ExtentInput(inputIdentifier, title, minOccurs))

            supportedCrsElements = bBoxElement.elementsByTagName("Supported")

            for i in range(supportedCrsElements.size()):
              crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))

            self.inputs.append(CrsInput(inputIdentifier, title, minOccurs, crsListe))

    def _parseProcessOutputs(self):
        dataOutputs = self.doc.elementsByTagName("Output")
        if dataOutputs.size() < 1:
            return

        # Add all complex outputs
        for i in range(dataOutputs.size()):
          f_element = dataOutputs.at(i).toElement()

          outputIdentifier, title, abstract = getIdentifierTitleAbstractFromElement(f_element)
          complexOutput = f_element.elementsByTagName("ComplexOutput")

          # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
          if complexOutput.size() > 0:
            # Das i-te ComplexData Objekt auswerten
            complexOutputTypeElement = complexOutput.at(0).toElement()
            complexOutputFormat = getDefaultMimeType(complexOutputTypeElement)
            supportedcomplexOutputFormat = getSupportedMimeTypes(complexOutputTypeElement)
            # Store the input formats
            self.outputs.append(VectorOutput(outputIdentifier, title, complexOutputFormat))

    def isDataTypeSupportedByServer(self, baseMimeType, name):
      # Return if the given data type is supported by the WPS server
      for dataType in self._inputsMetaInfo[name]:
        if baseMimeType in dataType['MimeType']:
          return True
      return False

    def getDataTypeInfo(self, mimeType, name):
      # Return a dict with mimeType, schema and encoding for the given mimeType
      for dataType in self._inputsMetaInfo[name]:
        if mimeType in dataType['MimeType']:
          return dataType
      return None

    def getSupportedGMLVersion(self, dataIdentifier):
      # Return GML version, e.g., GML, GML2, GML3 
      if isGML3SupportedByOGR() and self.isDataTypeSupportedByServer(getBaseMimeType("GML3"), dataIdentifier):
        return "GML3"
      elif self.isDataTypeSupportedByServer(getBaseMimeType("GML2"), dataIdentifier):
        return "GML2"
      elif self.isDataTypeSupportedByServer(getBaseMimeType("GML"), dataIdentifier):
        return "GML"
      else:
        return ""

    def getSupportedGMLDataFormat(self, dataIdentifier):
      # Return mimeType, schema and encoding for the supported GML version 
      supportedGML = self.getSupportedGMLVersion(dataIdentifier)

      if supportedGML != "":
        return self.getDataTypeInfo(getBaseMimeType(supportedGML), dataIdentifier)
      else:
        return None
