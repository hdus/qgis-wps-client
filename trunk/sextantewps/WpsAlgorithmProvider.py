from sextante.core.AlgorithmProvider import AlgorithmProvider
from sextante.core.SextanteConfig import Setting, SextanteConfig
from sextante.core.SextanteUtils import mkdir, SextanteUtils
from WpsAlgorithm import WpsAlgorithm
from AddNewWpsAction import AddNewWpsAction
from wps.wpslib.processdescription import ProcessDescription
import os

class WpsAlgorithmProvider(AlgorithmProvider):

    WPS_DESCRIPTIONS = "WPS_DESCRIPTIONS"

    def __init__(self, wpsDockWidget):
        AlgorithmProvider.__init__(self)
        self.actions.append(AddNewWpsAction(wpsDockWidget))

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        SextanteConfig.addSetting(Setting(self.getDescription(),
                                          WpsAlgorithmProvider.WPS_DESCRIPTIONS,
                                          "WPS description cache folder",
                                          WpsAlgorithmProvider.WpsDescriptionFolder()))

    @staticmethod
    def WpsDescriptionFolder():
        folder = SextanteConfig.getSetting(WpsAlgorithmProvider.WPS_DESCRIPTIONS)
        if folder == None:
            folder = unicode(os.path.join(SextanteUtils.userFolder(), "wps"))
        mkdir(folder)
        return os.path.abspath(folder)

    def unload(self):
        AlgorithmProvider.unload(self)
        SextanteConfig.removeSetting( WpsAlgorithmProvider.WPS_DESCRIPTIONS)

    def getName(self):
        return "wps"

    def getDescription(self):
        '''This is the name that will appear on the toolbox group.'''
        return "WPS"

    def getSupportedOutputVectorLayerExtensions(self):
        return ["gml"] #TODO: rasters?

    def getIcon(self):
        return AlgorithmProvider.getIcon(self)

    def _bookmarkAlgsList(self):
        bookmarkAlgs = []
        for process in ProcessDescription.getBookmarks():
            bookmarkAlgs.append( WpsAlgorithm(process) )
        return bookmarkAlgs

    def _loadAlgorithms(self):
        self.algs = self._bookmarkAlgsList()
