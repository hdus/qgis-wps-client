# -*- coding: utf-8 -*-

"""
Module implementing ThreadsDialog.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_QgsWpsServerThreadDialog import Ui_QgsWpsServerThreadDialog
from httplib import *
from urlparse import urlparse
import os, sys, string, tempfile, urllib2, urllib,  mimetypes

class QgsWpsServerThreadDialog(QDialog, Ui_QgsWpsServerThreadDialog):
  def __init__( self, processIdentifier,  scheme,  server,  path,  postString,  parent = None ):
    QDialog.__init__( self,  parent )
    self.setupUi( self )

    self.lblProcess.setText(processIdentifier)

    self.theThread = QgsWpsServerThread(scheme,  server,  path,  postString,  self.parent())
    
    self.connect(self.theThread, SIGNAL("started()"), self.setStarted)          
    self.connect(self.theThread, SIGNAL("finished()"), self.setFinished)          
    self.connect(self.theThread, SIGNAL("terminated()"), self.setTerminated)        
    self.theThread.start()          
    
    
  @pyqtSignature("")
  def on_pushButton_clicked(self):
      if self.pushButton.text() == 'cancel':
          self.stopProcessing()
          self.pushButton.setText('close')
      elif self.pushButton.text() == 'close':
        self.close()

  def setStarted(self):
      self.lineEdit.setText("Process started and running ... ")


  def setFinished(self):
      self.lineEdit.setText("Process finished")
      
  def closeDialog(self):
      self.close()
      
  def setTerminated(self):
      self.lineEdit.setText("Process terminated")          
        
  def stopProcessing( self ):
       if self.theThread != None:
         self.theThread.stop()
         self.theThread = None

class QgsWpsServerThread(QThread):

    def __init__(self,  scheme,  server,  path,  postString,  parent = None):
        QThread.__init__(self, parent)
        self.scheme = scheme
        self.server = server
        self.path = path
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
        
#a = QApplication(sys.argv)
#scheme = 'http'
#server = 'www.kappasys.ch'
#path = '/pywps/pywps.cgi'
#outFile = open('/home/hdus/temp/qwps_execute_request.xml', 'r')
#postString = outFile.read()
#outFile.close()
#processIdentifier = 'Test Process'
#dlg = QgsWpsServerThreadDialog(processIdentifier,  scheme,  server,  path,  postString)
#dlg.show()
#a.exec_()        

