# -*- encoding:utf-8 -*-
"""
/***************************************************************************
Client for streaming based WPS.
It exploits asynchronous capabilities of WPS and QGIS for visualizing
  intermediate results from a WPS
                             -------------------
copyright            : (C) 2012 by Germán Carrillo (GeoTux)
email                : geotux_tuxman@linuxmail.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import (QTimer, QUrl, QFile, QIODevice, QVariant, pyqtSignal, 
                          QObject, QProcess, QStringList, QRegExp, QString, 
                          QSettings, SIGNAL, QTextStream)
from PyQt4.QtGui import QColor, QMessageBox
from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager
from qgis.core import (QgsNetworkAccessManager, QgsVectorLayer, QgsRasterLayer, 
                        QgsMapLayerRegistry, QgsFeature, QgsGeometry)
from qgis.gui import QgsRubberBand, QgsVertexMarker

from wpslib.processdescription import getFileExtension,isMimeTypeVector,isMimeTypeRaster
from wpslib.executionresult import decodeBase64

from functools import partial
import tempfile
import os, platform 
import glob

class Streaming(QObject):
    """ Class for keeping track of stream chunks and 
        providing methods for handling and visualizing them 
    """
    
    # Define SIGNALS/SLOTS
    playlistHandled = pyqtSignal(dict)
    urlReady = pyqtSignal('QString', int, 'QString')
    dataReady = pyqtSignal('QString', int)
    
    def __init__(self, parent, iface, chunks, playlistUrl, mimeType, encoding):
        super(Streaming, self).__init__()
        
        self.DEBUG = True
        
        # Variables from other classes
        self.parent = parent # For GUI access
        self.iface = iface
        self.chunks = chunks
        self.playlistUrl = playlistUrl
        self.mimeType = mimeType
        self.encoding = encoding
        
        # Internal variables
        self.__endTag = "#PLAYLIST-END" 
        self.__exceptionTag = "#EXCEPTION"
        self.__exceptionUrl = ""
        self.__exceptionFound = False
        self.__playlistFinished = False # Did the end tag appeared?
        self.__bytesInlastReply = 0 # To compare last and current reply sizes
        self.__loadedChunks = 0   # For keeping track of # of loaded (to local vars) chunks
        self.__deliveredChunks = 0   # For keeping track of # of loaded (to the map) chunks
        self.__bFirstChunk = True
        self.__features = {}      # {0:[f0,f1,f2], 1:[f0,f1]}
        self.__bGeomMulti = False # Is the geometry multi{point|line|polygon}
        self.__geometryType = "" # Values: "Point","LineString","Polygon","Unknown", "NoGeometry"
        self.__tmpGeometry = {} # For visualization purposes {chunkId1: rb1, chunkId2: rb2 }
        self.__memoryLayer = None # The whole merged data
        
        # For rasters only
        self.__legend = self.iface.legendInterface() 
        self.__groupIndex = 0 
        self.__chunksDir = None
        self.__virtualFile = ""  # Virtual raster file path
        if isMimeTypeRaster(self.mimeType, True) != None: 
            self.__chunksDir = tempfile.mkdtemp(prefix="tmpChunks") 
    
        # Other objects
        self.timer = QTimer()  
        self.timer.setInterval(1 * 1000) # 1 second
        self.QNAM4Playlist = QNetworkAccessManager()
        self.QNAM4Chunks = QNetworkAccessManager()
        self.QNAM4Exception = QNetworkAccessManager()
       
        # SIGNAL/SLOT connections
        self.playlistHandled.connect(self.fetchChunks)
        self.urlReady.connect(self.fetchResult)
        self.dataReady.connect(self.loadData)
        self.timer.timeout.connect(partial(self.fetchPlaylist, self.playlistUrl))
            
        self.QNAM4Playlist.finished.connect(self.handlePlaylist) 
        self.QNAM4Chunks.finished.connect(self.handleChunk) 
        self.QNAM4Exception.finished.connect(self.handleException)
        #self.QNAM4Playlist = QgsNetworkAccessManager.instance()
        #theReply2.error.connect(self.handleErrors)
        
        # GUI
        self.parent.progressBar.setRange(0,0)
        self.parent.lblProcess.setText("Reading output playlist...")
    
    
    def start(self):
        """ Start fetching """
        self.fetchPlaylist(self.playlistUrl) # First call
        
        
    def stop(self):
        """ Stop fetching """
        self.timer.stop() 
        self.QNAM4Playlist.finished.disconnect(self.handlePlaylist)    
        self.QNAM4Chunks.finished.disconnect(self.handleChunk) 
        self.removeTempGeometry(self.__geometryType)  
        if self.DEBUG: print "Stop streaming!" 
        
    
    def validateCompletedStream(self):
        """ Is the stream complete (Did the end tag appeared?) """
        #return (self.__loadedChunks >= self.chunks and self.chunks != 0)
        return self.__playlistFinished 
        
        
    def allChunksDelivered(self):
        """ Are all chunks already loaded into the map? """
        return ((self.__loadedChunks == self.__deliveredChunks and 
            self.__playlistFinished) or self.__exceptionFound)
             

    def fetchPlaylist(self, playlistLink):
        url = QUrl(playlistLink)
        self.QNAM4Playlist.get(QNetworkRequest(url)) # SLOT: handlePlaylist


    def handlePlaylist(self, reply):  
        """ Parse the chunk URLs and update the loadedChunks counter """       
        # Check if there is redirection 
        reDir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        if not reDir.isEmpty():
            self.fetchPlaylist(reDir.toString()) 
            return
        
        # Parse URLs only if there is new data in the reply
        if reply.bytesAvailable() > self.__bytesInlastReply:
            if self.DEBUG: print " Parsing the playlist..."
            startFrom = reply.bytesAvailable() - self.__bytesInlastReply # Delta in bytes
            self.__bytesInlastReply = reply.bytesAvailable()
            newURLs = self.parseURLs(reply, startFrom)
        else: 
            if self.DEBUG: print " No new data in the playlist..."
            newURLs = {} 

        # Store new URLs    
        if len(newURLs) > 0:
            self.__loadedChunks += len(newURLs) 
            if self.chunks:
                self.parent.progressBar.setRange(0,self.chunks)
        
        if self.DEBUG: print str(self.__loadedChunks) + " chunks loaded" + ((" out of " + str(self.chunks)) if self.chunks else "")
        
        # If not complete, make additional calls
        if not self.validateCompletedStream():
            if not self.timer.isActive():
                self.timer.start()
                if self.DEBUG: print "Timer started..."
        else:
            self.timer.stop() 
            self.QNAM4Playlist.finished.disconnect(self.handlePlaylist)    
            if self.DEBUG: print "Playlist finished!" 
            
            if self.allChunksDelivered():
                self.finishLoading()   
        
        if self.__exceptionFound:
            self.fetchException()
        
        if len(newURLs) > 0:
            self.playlistHandled.emit(newURLs) # SLOT: fetchChunks
        
    
    def parseURLs(self, reply, startFrom):
        """ Get a dict of new IDs:URLs from the current playlist (newURLs) """
        newURLs = {}  # {0:URL0, 1:URL1, ...}
        count = 0     
        
        #Get the delta and start reading it
        allData = reply.readAll()
        allData = allData.right(startFrom) # Get rid of old data
        response = QTextStream(allData, QIODevice.ReadOnly)
        data = response.readLine()
        
        # Parse 
        while (data):     
            data = str(data.split("\n")[0])
            if data:
                if "#" in data: # It's a playlist comment 
                    if self.__endTag in data: 
                        self.__playlistFinished = True 
                    elif self.__exceptionTag in data:
                        if self.DEBUG: print "Exception found!"
                        self.__exceptionFound = True
                        self.__exceptionUrl = data.split(":",1)[1].strip()
                else: 
                    newURLs[count+self.__loadedChunks] = data
                    count += 1
            data = response.readLine()
    
        return newURLs
        
        
    def fetchChunks(self, newURLs):  
        """ Fetch each url """
        for chunkId in newURLs:
            self.urlReady.emit(self.encoding, chunkId, newURLs[chunkId]) # SLOT: fetchResult


    def fetchResult(self, encoding, chunkId, fileLink): 
        """ Send the GET request """           
        url = QUrl(fileLink)
        theReply2 = self.QNAM4Chunks.get(QNetworkRequest(url))
        theReply2.setProperty("chunkId", QVariant(chunkId))
        theReply2.setProperty("encoding", QVariant(encoding))
                  
    
    def handleErrors(self, error): # TODO connect it
        if self.DEBUG: print "ERROR!!!", error
    
    
    def fetchException(self):
        """ Send the GET request for the exception """
        url = QUrl(self.__exceptionUrl)
        theReply3 = self.QNAM4Exception.get(QNetworkRequest(url)) 
    

    def handleException(self, reply):  
        """ Display the exception """
        # Check if there is redirection 
        reDir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        if not reDir.isEmpty():
            self.__exceptionUrl = reDir.toString()
            self.fetchException()
            return

        resultXML = reply.readAll().data()
        self.parent.setStatusLabel('error')
        self.parent.progressBar.setMinimum(0)
        self.parent.progressBar.setMaximum(100)
        self.parent.errorHandler(resultXML)
    
    
    def handleChunk(self, reply):
        """ Store the file received """
        #reply.deleteLater() # Recommended way to delete the reply
        
        chunkId = reply.property("chunkId").toInt()[0]
        encoding = reply.property("encoding").toString()
        
        # Check if there is redirection 
        reDir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        if not reDir.isEmpty():
            self.urlReady.emit(encoding, chunkId, reDir.toString())
            return

        if self.DEBUG: print "GET chunk", chunkId  

        # Update progressBar        
        if self.chunks:
            self.parent.progressBar.setValue(self.__deliveredChunks + 1)
            self.parent.lblProcess.setText("Downloading chunks... ("+str(self.__deliveredChunks + 1)+"/"+str(self.chunks)+")")


        # Get a unique temporary file name     
        tmpFile = tempfile.NamedTemporaryFile(prefix="base64", 
            suffix=getFileExtension(self.mimeType), dir=self.__chunksDir, delete=False )
        
        # TODO: Check if the file name already exists!!!
        
        # Write the data to the temporary file 
        outFile = QFile(tmpFile.name)
        outFile.open(QIODevice.WriteOnly)
        outFile.write(reply.readAll())
        outFile.close()
        
        # Decode?
        if encoding == "base64":
            resultFile = decodeBase64(tmpFile.name, self.mimeType, self.__chunksDir)  
        else:   
            resultFile = tmpFile.name
            
        # Finally, load the data
        if self.DEBUG: print "READY to be loaded (", resultFile, ", chunkId:", chunkId, ")"
        self.dataReady.emit(resultFile, chunkId) # SLOT: loadData  
      
        
    def loadData(self, resultFile, chunkId):
        """ Load data to the map """
        
        if isMimeTypeVector(self.mimeType, True) != None:                 
            # Memory layer:
            geometryTypes = ["Point","LineString","Polygon","Unknown", "NoGeometry"]
            vlayer = QgsVectorLayer(resultFile, "chunk", "ogr")

            if self.__bFirstChunk:    
                self.__bFirstChunk = False
                self.__geometryType = geometryTypes[vlayer.geometryType()]
                self.__bGeomMulti = vlayer.wkbType() in [4,5,6,11,12,13]
                self.__memoryLayer = QgsVectorLayer(self.__geometryType,"Streamed data","memory")
                self.__memoryLayer.dataProvider().addAttributes(vlayer.pendingFields().values())
                self.__memoryLayer.updateFieldMap()            

            provider = vlayer.dataProvider()
            allAttrs = provider.attributeIndexes()
            vlayer.select(allAttrs)  
            
            # Visualize temporal geometries during the downloading process
            # Don't add temporal geometries if last chunk
            if self.DEBUG: print "Loaded chunkId:",chunkId           
            res = self.__memoryLayer.dataProvider().addFeatures( [feat for feat in vlayer] )
            self.__deliveredChunks += 1      
            
            if not self.allChunksDelivered():
                inFeat = QgsFeature()
                inGeom = QgsGeometry()
                self.createTempGeometry(chunkId, self.__geometryType)
                while provider.nextFeature( inFeat ):
                    inGeom = inFeat.geometry()
                    featList = self.extractAsSingle(self.__geometryType, inGeom) if self.__bGeomMulti else [inGeom]
                    for geom in featList:
                        self.addTempGeometry(chunkId, self.__geometryType, geom)  
            else:
                self.finishLoading()
                                
        # Raster data
        elif isMimeTypeRaster(self.mimeType, True) != None:
            # We can directly attach the new layer
            if self.__bFirstChunk:    
                self.__bFirstChunk = False
                self.__groupIndex = self.__legend.addGroup("Streamed-raster")
                
            rLayer = QgsRasterLayer(resultFile, "raster_"+str(chunkId))
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(rLayer)
            self.stretchRaster(rLayer)
            self.__legend.moveLayer(rLayer, self.__groupIndex + 1)
            
            self.__deliveredChunks += 1
            
            if self.allChunksDelivered():
                self.finishLoading()


    def finishLoading(self):
        """ Finish the loading process, load the definite assembled layer """
        if self.DEBUG: print "DONE!"
            
        if not self.__bFirstChunk:
            if isMimeTypeVector(self.mimeType, True) != None:
                self.removeTempGeometry(self.__geometryType)   
                QgsMapLayerRegistry.instance().addMapLayer(self.__memoryLayer)    
            
            elif isMimeTypeRaster(self.mimeType, True) != None:
                self.parent.lblProcess.setText("All tiles are loaded. Merging them...")

                # Generate gdal virtual raster 
                # Code adapted from GdalTools (C) 2009 by L. Masini and G. Sucameli (Faunalia)
                self.process = QProcess(self)
                self.connect(self.process, SIGNAL("finished(int, QProcess::ExitStatus)"), 
                    self.loadVirtualRaster)
                #self.setProcessEnvironment(self.process) Required in Windows?
                cmd = "gdalbuildvrt"
                arguments = QStringList()
                if platform.system() == "Windows" and cmd[-3:] == ".py":
                    command = cmd[:-3] + ".bat"
                else:
                    command = cmd
                    
                tmpFile = tempfile.NamedTemporaryFile(prefix="virtual", 
                    suffix=".vrt")
                self.__virtualFile = tmpFile.name
                arguments.append(self.__virtualFile)
                rasters = self.getRasterFiles(self.__chunksDir, 
                    getFileExtension(self.mimeType))
                for raster in rasters:
                    arguments.append(raster)
                self.process.start(command, arguments, QIODevice.ReadOnly)
                
        if not self.__exceptionFound:
            self.parent.setStatusLabel('finished')   
            self.parent.progressBar.setRange(0,100)
            self.parent.progressBar.setValue(100)


    def createTempGeometry(self, chunkId, geometryType): 
        """ Create rubber bands for rapid visualization of geometries """     
        if geometryType == "Polygon":
            self.__tmpGeometry[chunkId] = QgsRubberBand(self.iface.mapCanvas(), True)
            self.__tmpGeometry[chunkId].setColor( QColor( 0,255,0,255 ) )
            self.__tmpGeometry[chunkId].setWidth( 2 )
            if self.DEBUG: print "rubberBand created"
        elif geometryType == "LineString":
            self.__tmpGeometry[chunkId] = QgsRubberBand(self.iface.mapCanvas(), False)
            self.__tmpGeometry[chunkId].setColor( QColor( 255,121,48,255 ) )
            self.__tmpGeometry[chunkId].setWidth( 3 )
        elif geometryType == "Point":
            # In the case of points, they will be added as vertex objects later
            self.__tmpGeometry[chunkId] = []


    def addTempGeometry(self, chunkId, geometryType, geometry):
        """ Add geometries as rubber bands or vertex objects """     
        if geometryType == "Polygon" or geometryType == "LineString":
            self.__tmpGeometry[chunkId].addGeometry(geometry, None)      
        elif geometryType == "Point":
            vertex = QgsVertexMarker(self.iface.mapCanvas())
            vertex.setCenter(geometry.asPoint())
            vertex.setColor(QColor(0,255,0))
            vertex.setIconSize(6)
            vertex.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            vertex.setPenWidth(3)
            self.__tmpGeometry[chunkId].append(vertex)


    def removeTempGeometry(self, geometryType):
        """ Remove rubber bands or vertex objects from the map """
        if geometryType == "Polygon" or geometryType == "LineString":
            for chunkId in self.__tmpGeometry.keys():
                self.iface.mapCanvas().scene().removeItem(self.__tmpGeometry[chunkId])
                del self.__tmpGeometry[chunkId]
        elif geometryType == "Point": 
            for chunkId in self.__tmpGeometry.keys():       
                if len( self.__tmpGeometry[chunkId] ) > 0:
                    for vertex in self.__tmpGeometry[chunkId]:
                        self.iface.mapCanvas().scene().removeItem(vertex)
                        del vertex


    def extractAsSingle(self, geometryType, geom):
        """ Extract multi geometries as single ones.
            Required because of a QGIS bug regarding multipolygons and rubber bands
        """        
        # Code adapted from QGIS fTools plugin, (C) 2008-2011  Carson Farmer
        multi_geom = QgsGeometry()
        temp_geom = []
        if geometryType == "Point":
            multi_geom = geom.asMultiPoint()
            for i in multi_geom:
                temp_geom.append( QgsGeometry().fromPoint ( i ) )
        elif geometryType == "LineString":
            multi_geom = geom.asMultiPolyline()
            for i in multi_geom:
                temp_geom.append( QgsGeometry().fromPolyline( i ) )
        elif geometryType == "Polygon":
            multi_geom = geom.asMultiPolygon()
            for i in multi_geom:
                temp_geom.append( QgsGeometry().fromPolygon( i ) )
        return temp_geom


    def loadVirtualRaster(self, exitCode, status):
        """ Load a virtual raster to QGIS """
        if exitCode == 0:
            self.__legend.setGroupVisible( self.__groupIndex, False )
            rLayer = QgsRasterLayer(self.__virtualFile, "virtual")
            bLoaded = QgsMapLayerRegistry.instance().addMapLayer(rLayer)
            self.stretchRaster(rLayer)
        self.process.kill()

        
    def stretchRaster(self, raster):
         raster.setMinimumMaximumUsingLastExtent()
         raster.setContrastEnhancementAlgorithm(1)
         raster.triggerRepaint()
         
         
    def setProcessEnvironment(self, process):
        """ From GdalTools. Set environment variables for running gdalbuildvrt """
        envvar_list = {
            "PATH" : self.getGdalBinPath(), 
            "PYTHONPATH" : self.getGdalPymodPath()
        }
        if self.DEBUG: print envvar_list

        sep = os.pathsep

        for name, val in envvar_list.iteritems():
            if val == None or val == "":
                continue

            envval = os.getenv(name)
            if envval == None or envval == "":
                envval = str(val)
            elif not QString( envval ).split( sep ).contains( val, Qt.CaseInsensitive ):
                envval += "%s%s" % (sep, str(val))
            else:
                envval = None

            if envval != None:
                os.putenv( name, envval )

            if False:  # not needed because os.putenv() has already updated the environment for new child processes
                env = QProcess.systemEnvironment()
                if env.contains( QRegExp( "^%s=(.*)" % name, Qt.CaseInsensitive ) ):
                    env.replaceInStrings( QRegExp( "^%s=(.*)" % name, Qt.CaseInsensitive ), "%s=\\1%s%s" % (name, sep, gdalPath) )
                else:
                    env << "%s=%s" % (name, val)
                process.setEnvironment( env )

    def getRasterFiles(self, dir, extension):
        rasters = QStringList()
        for name in glob.glob(dir + '/*' +  extension):
            rasters.append(name)
        return rasters      
    
   
    def getGdalBinPath(self):
        """ Retrieves GDAL binaries location """
        settings = QSettings()
        return settings.value( "/GdalTools/gdalPath", QVariant( "" ) ).toString()

   
    def getGdalPymodPath(self):
        """ Retrieves GDAL python modules location """
        settings = QSettings()
        return settings.value( "/GdalTools/gdalPymodPath", QVariant( "" ) ).toString()
   
