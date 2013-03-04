from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.outputs.OutputVector import OutputVector
from sextante.parameters.ParameterVector import ParameterVector
from sextante.core.Sextante import Sextante
from sextante.parameters.ParameterExtent import ParameterExtent
from sextante.parameters.ParameterCrs import ParameterCrs


class BookmarksAlgorithm(GeoAlgorithm):

    def __init__(self, config):
        self.config = config
        GeoAlgorithm.__init__(self) #calls defineCharacteristics

    def defineCharacteristics(self):
        self.name = str(self.config['identifier'])
        self.group = "Bookmarks"

        #self.addParameter(ParameterVector(self.INPUT_LAYER, "Input layer", ParameterVector.VECTOR_TYPE_ANY, False))
        #self.addParameter(ParameterExtent("EXTENT","EXTENT"))
        #self.addParameter(ParameterCrs("CRS", "CRS"))
        #self.addOutput(OutputVector(self.OUTPUT_LAYER, "Output layer with selected features"))

        #self.doc.setContent(self.tools.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier), True)
        #DataInputs = self.doc.elementsByTagName("Input")
        #DataOutputs = self.doc.elementsByTagName("Output")
        #
        #identifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(self.doc)
        #self.addIntroduction(identifier, title)
        #
        ## If no Input Data  are requested
        #if DataInputs.size()==0:
        #  self.defineProcess()
        #  return 0
        #
        ## Generate the input GUI buttons and widgets
        #self.generateProcessInputsGUI(DataInputs)
        ## Generate the editable outpt widgets, you can set the output to none if it is not requested
        #self.generateProcessOutputsGUI(DataOutputs)

        #def generateProcessInputsGUI(self, DataInputs):
        #  """Generate the GUI for all Inputs defined in the process description XML file"""
        #
        #  # Create the complex inputs at first
        #  for i in range(DataInputs.size()):
        #    f_element = DataInputs.at(i).toElement()
        #
        #    inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
        #
        #    complexData = f_element.elementsByTagName("ComplexData")
        #    minOccurs = int(f_element.attribute("minOccurs"))
        #    maxOccurs = int(f_element.attribute("maxOccurs"))
        #
        #    # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
        #    if complexData.size() > 0:
        #      # Das i-te ComplexData Objekt auswerten
        #      complexDataTypeElement = complexData.at(0).toElement()
        #      complexDataFormat = self.tools.getDefaultMimeType(complexDataTypeElement)
        #      supportedComplexDataFormat = self.tools.getSupportedMimeTypes(complexDataTypeElement)
        #
        #      # Store the input formats
        #      self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
        #      self.inputDataTypeList[inputIdentifier] = complexDataFormat
        #
        #      # Attach the selected vector or raster maps
        #      if self.tools.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
        #        # Vector inputs
        #        layerNamesList = self.tools.getLayerNameList(0)
        #        if maxOccurs == 1:
        #          self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        #        else:
        #          self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        #      elif self.tools.isMimeTypeText(complexDataFormat["MimeType"]) != None:
        #        # Text inputs
        #        self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))
        #      elif self.tools.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:
        #        # Raster inputs
        #        layerNamesList = self.tools.getLayerNameList(1)
        #        if maxOccurs == 1:
        #          self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        #        else:
        #          self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
        #      else:
        #        # We assume text inputs in case of an unknown mime type
        #        self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))            
        #
        #  # Create the literal inputs as second
        #  for i in range(DataInputs.size()):
        #    f_element = DataInputs.at(i).toElement()
        #
        #    inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
        #
        #    literalData = f_element.elementsByTagName("LiteralData")
        #    minOccurs = int(f_element.attribute("minOccurs"))
        #    maxOccurs = int(f_element.attribute("maxOccurs"))
        #
        #    if literalData.size() > 0:
        #      allowedValuesElement = literalData.at(0).toElement()
        #      aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
        #      dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
        ##        print "Checking allowed values " + str(aValues.size())
        #      if aValues.size() > 0:
        #        valList = self.tools.allowedValues(aValues)
        #        if len(valList) > 0:
        #          if len(valList[0]) > 0:
        #            self.literalInputComboBoxList.append(self.addLiteralComboBox(title, inputIdentifier, valList, minOccurs))
        #          else:
        #            self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, str(valList)))
        #      else:
        #        self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, dValue))
        #
        #  # At last, create the bounding box inputs
        #  for i in range(DataInputs.size()):
        #    f_element = DataInputs.at(i).toElement()
        #
        #    inputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
        #    
        #    bBoxData = f_element.elementsByTagName("BoundingBoxData")
        #    minOccurs = int(f_element.attribute("minOccurs"))
        #    maxOccurs = int(f_element.attribute("maxOccurs"))
        #
        #    if bBoxData.size() > 0:
        #      crsListe = []
        #      bBoxElement = bBoxData.at(0).toElement()
        #      defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
        #      defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href")
        #      crsListe.append(defaultCrs)
        #      self.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs)
        #
        #      supportedCrsElements = bBoxElement.elementsByTagName("Supported")
        #
        #      for i in range(supportedCrsElements.size()):
        #        crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))
        #
        #      self.literalInputComboBoxList.append(self.addLiteralComboBox("Supported CRS", inputIdentifier,crsListe, minOccurs))
        #
        #
        #  self.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"))
        #  
        ###############################################################################
        #
        #def generateProcessOutputsGUI(self, DataOutputs):
        #  """Generate the GUI for all complex ouputs defined in the process description XML file"""
        #
        #  if DataOutputs.size() < 1:
        #      return
        #
        #  groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #  groupbox.setTitle("Complex output(s)")
        #  layout = QVBoxLayout()
        #
        #  # Add all complex outputs
        #  for i in range(DataOutputs.size()):
        #    f_element = DataOutputs.at(i).toElement()
        #
        #    outputIdentifier, title, abstract = self.tools.getIdentifierTitleAbstractFromElement(f_element)
        #    complexOutput = f_element.elementsByTagName("ComplexOutput")
        #
        #    # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
        #    if complexOutput.size() > 0:
        #      # Das i-te ComplexData Objekt auswerten
        #      complexOutputTypeElement = complexOutput.at(0).toElement()
        #      complexOutputFormat = self.tools.getDefaultMimeType(complexOutputTypeElement)
        #      supportedcomplexOutputFormat = self.tools.getSupportedMimeTypes(complexOutputTypeElement)
        #
        #      # Store the input formats
        #      self.outputsMetaInfo[outputIdentifier] = supportedcomplexOutputFormat
        #      self.outputDataTypeList[outputIdentifier] = complexOutputFormat
        #      
        #      widget, comboBox = self.addComplexOutputComboBox(groupbox, outputIdentifier, title, str(complexOutputFormat))
        #      self.complexOutputComboBoxList.append(comboBox)
        #      layout.addWidget(widget)
        #  
        #  # Set the layout
        #  groupbox.setLayout(layout)
        #  # Add the outputs
        #  self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)


    def processAlgorithm(self, progress):
        pass
