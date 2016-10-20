# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 17:16:19 2016

@author: Jack Halliday
"""

import xml.etree.ElementTree as ET

class Diagnostic:
    """
    Base class from which all diagnostics are derived
    """
    def __init__(self, xmlMember):
        self.path = xmlMember.find('filePath').text

    # Load methods for all valid fields should be defined here.
    # Classes which inherit from Diagnostic should not define thier own load 
    # methods: Fields used in multipe diagnostics & have to ensure consistancy
    def _loadTime(self, xmlMember):
        self.time = float( xmlMember.find('time').text )
    
    def _loadScale(self, xmlMember):
        self.scale = float( xmlMember.find('scale').text )
        
    def _loadWavelength(self, xmlMember):
        self.wavelength = float( xmlMember.find('wavelength').text )
        
    def _loadShotFileName(self, xmlMember):
        self.shotFileName = xmlMember.find('shotFileName').text

    def _loadBackFileName(self, xmlMember):
        self.backFileName = xmlMember.find('backFileName').text
    
    def _loadShadowFileName(self, xmlMember):
        self.shadowFileName = xmlMember.find('shadowFileName').text

    def _loadOrigin(self, xmlMember):
        originMember = xmlMember.find('origin')
        originX = int( originMember.find('x').text )
        originY = int( originMember.find('y').text )
        self.origin = (originX, originY)
    
    def _load(self, xmlMember, tag, targetType):
        try:
            return targetType( xmlMember.find(tag).text )
        except AttributeError:
            return None
            
    
    fieldNames = {
                  # Relates field names (as strings) to the load methods
                      'time': _loadTime, 
                      'scale':_loadScale,
                      'wavelength': _loadWavelength,
                      'shotFileName': _loadShotFileName,
                      'backFileName': _loadBackFileName,
                      'shadowFileName': _loadShadowFileName,
                      'origin': _loadOrigin,
                       }
    def LoadFields(self, fieldNameList, xmlMember):
        """
        Loads all the fields given in the fieldName list. Elements of this list
        must be keys in the fieldNames member variable
        """
        for name in fieldNameList:
            try:
                self.fieldNames[name](self, xmlMember)
            except KeyError:
                print ("An unknown field name was provided")

class Interferometry (Diagnostic):
    """
    Class to handle interferometry data
    """
    includedFields = ['time', 'scale', 'wavelength', 'shotFileName', 
                      'backFileName', 'shadowFileName']
                      
    def __init__(self, xmlMember):
        Diagnostic.__init__(self, xmlMember)
        self.LoadFields(self.includedFields, xmlMember)
    
class Shot:
    """
    Class to handle a number of diagnostics
    """
    diagnosticClasses = { 
                         # Relates field tags (in XML) to diagnostic classes
                         'interferometry': Interferometry
                         } 
    
    def __init__(self, xmlMember):
        self.filePath = xmlMember.find('filePath').text
        self.diagnostics = { }
        for xmlChild in xmlMember.iter('diagnostic'):
            diagnosticType = xmlChild.attrib['type']
            try:
                diagnostic = self.diagnosticClasses[diagnosticType](xmlChild)
                self.diagnostics[diagnosticType] = diagnostic  
            except KeyError:
                print ("Diagnostic type: " + diagnosticType + " is unknown")
            