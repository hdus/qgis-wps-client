# -*- coding: utf-8 -*-

"""
Module implementing ThreadsDialog.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_ServerThreadDialog import Ui_ServerThreadDialog
import time, sys

class ServerThreadDialog(QDialog, Ui_ServerThreadDialog):
  def __init__( self, parent = None ):
    QDialog.__init__( self,  parent )
    self.setupUi( self )
    self.theThread = None            
    
  def setStarted(self):
      self.lineEdit.setText("Thread started")


  def setFinished(self):
      self.lineEdit.setText("Thread finished")
      
  def setTerminated(self):
      self.lineEdit.setText("Thread terminated")

  def result(self,  message):
      self.btnThread.setEnabled(True)        
      QMessageBox.information(None, '', message)                   

  @pyqtSignature("")
  def on_btnThread_clicked(self):
      self.theThread = MyThread(self.spinBox.value(),  self.parent())
      self.connect(self.theThread, SIGNAL("started()"), self.setStarted)          
      self.connect(self.theThread, SIGNAL("finished()"), self.setFinished)          
      self.connect(self.theThread, SIGNAL("terminated()"), self.setTerminated)        
      self.connect(self.theThread, SIGNAL("serviceFinished(QString)"), self.result)          
      self.btnThread.setEnabled(False)
      self.theThread.start()        
      
      
  @pyqtSignature("")
  def on_btnNoThread_clicked(self):
      self.connect(self, SIGNAL("serviceFinished(QString)"), self.result)          
      self.runUnThreaded(self.spinBox.value())
      pass
      
  def runUnThreaded(self,  maxIt):
        t = QTime()
        t.start()
        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setRange(0, 100)
        for i in range(maxIt):
           self.progressBar.setValue((float(i)+1)/float(maxIt)*100.0)
        
        self.emit(SIGNAL("serviceFinished(QString)"),  'Thread finished after '+str(i+1)+' iterations. Time elapsed: '+str(t.elapsed())+' ms')
              
        
  def stopProcessing( self ):
       if self.theThread != None:
         self.theThread.stop()
         self.theThread = None
     
  
  @pyqtSignature("")
  def on_buttonBox_rejected(self):
      self.stopProcessing()

class MyThread(QThread):

    def __init__(self,  maxIt, parent = None):
        QThread.__init__(self, parent)
        self.maxIt = maxIt

    def run(self):
        t = QTime()
        t.start()
        for i in range(self.maxIt):
          n = i * i
        self.emit(SIGNAL("serviceFinished(QString)"),  'Thread finished after '+str(n)+' iterations. Time elapsed: '+str(t.elapsed())+' ms')
        self.stop()


    def stop( self ):
        QThread.wait( self  )
        
a = QApplication(sys.argv)
dlg = ServerThreadDialog()
dlg.show()
a.exec_()        

