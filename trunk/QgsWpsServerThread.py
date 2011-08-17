from PyQt4.QtCore import *
import urllib2, urllib


class QgsWpsServerThread(QThread):

    def __init__(self,  parent = None):
        QThread.__init__(self, parent)
  
    def setScheme(self, scheme):
        self.scheme = scheme
        
    def setServer(self, server):        
        self.server = server
        
    def setPath(self,  path):
        self.path = path
        
    def setPostString(self,  postString):
        self.postString = postString        

    def run(self):
        url = str(self.scheme)+"://"+str(self.server)+""+str(self.path)
        data = unicode(self.postString, "latin1").replace('<wps:ComplexData>\n','<wps:ComplexData>')
        f = urllib.urlopen( url, data)
        
     # Read the results back.
        wpsRequestResult = f.read()
        self.emit(SIGNAL("serviceFinished(QString)"),  wpsRequestResult)
        self.stop()


    def stop( self ):
        QThread.wait( self  )
