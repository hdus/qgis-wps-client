from sextante.core.AlgorithmProvider import AlgorithmProvider
from sextante.core.SextanteConfig import Setting, SextanteConfig
from sextante.core.SextanteLog import SextanteLog
from sextante.outputs.OutputFactory import OutputFactory

from WpsAlgorithm import WpsAlgorithm
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os,  inspect

class WpsAlgorithmProvider(AlgorithmProvider):

    MY_DUMMY_SETTING = "MY_DUMMY_SETTING"

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.createAlgsList() #preloading algorithms to speed up
        self.alglist = self.preloadedAlgs        

    @staticmethod
    def wpsDescriptionPath():
        return os.path.join(os.path.dirname(__file__), "description")
        
    def createAlgsList(self):
        self.preloadedAlgs = []
        folder = self.wpsDescriptionPath()
        for descriptionFile in os.listdir(folder):
            if QFileInfo(descriptionFile).suffix() == 'txt':
                try:
                    if descriptionFile.startswith("alg_"):
                        alg = WpsAlgorithm(os.path.join(folder, descriptionFile))
                        if alg.name.strip() != "":
#                            QMessageBox.information(None, 'in try', os.path.join(folder, descriptionFile))                                        
                            self.preloadedAlgs.append(alg)
                        else:
                            SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open WPS algorithm (alg.name empty): " + descriptionFile)
                except Exception,e:
                    SextanteLog.addToLog(SextanteLog.LOG_ERROR, "Could not open WPS algorithm: " + descriptionFile)            

    def initializeSettings(self):
        '''In this method we add settings needed to configure our provider.
        Do not forget to call the parent method, since it takes care or
        automatically adding a setting for activating or deactivating the
        algorithms in the provider'''
        AlgorithmProvider.initializeSettings(self)
        SextanteConfig.addSetting(Setting("WPS", self.MY_DUMMY_SETTING, "WPS setting", "Default value"))
        '''To get the parameter of a setting parameter, use SextanteConfig.getSetting(name_of_parameter)'''

    def unload(self):
        '''Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded'''
        AlgorithmProvider.unload(self)
        SextanteConfig.removeSetting( self.MY_DUMMY_SETTING)

    def getIcon(self):
        '''We return the default icon'''
        return AlgorithmProvider.getIcon(self)

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs

    def getName(self):
        return "WPS"

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/wps-add.png")        

#
#    def _loadAlgorithms(self):
#        '''Here we fill the list of algorithms in self.algs.
#        This method is called whenever the list of algorithms should be updated.
#        If the list of algorithms can change while executing SEXTANTE for QGIS
#        (for instance, if it contains algorithms from user-defined scripts and
#        a new script might have been added), you should create the list again
#        here.
#        In this case, since the list is always the same, we assign from the pre-made list.
#        This assignment has to be done in this method even if the list does not change,
#        since the self.algs list is cleared before calling this method'''
#        self.algs = self.alglist
#        
#        for alg in self.alglist:
#            QMessageBox.information(None, 'single algorithms', alg)        
