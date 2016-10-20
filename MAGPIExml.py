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
    # methods: Fields used in multipe diagnostics & have to ensure consistancy.
    # If a field is not found in the XML, its load method should write a None 
    # type to the target variable 
    def _LoadTime(self, xmlMember):
        self.time = self._Load(xmlMember, 'time', float)
    
    def _LoadScale(self, xmlMember):
        self.scale = self._Load(xmlMember, 'scale', float)
        
    def _LoadWavelength(self, xmlMember):
        self.wavelength = self._Load(xmlMember, 'wavelegnth', str)
        
    def _LoadShotFileName(self, xmlMember):
        self.shadowFileName = self._Load(xmlMember, 'shotFileName', str)

    def _LoadBackFileName(self, xmlMember):
        self.backFileName = self._Load(xmlMember, 'backFileName', str)
    
    def _LoadShadowFileName(self, xmlMember):
        self.shadowFileName = self._Load(xmlMember, 'shadowFileName', str)

    def _LoadOrigin(self, xmlMember):
        originMember = xmlMember.find('origin')
        originX = self._Load(originMember, 'x', int)
        originY = self._Load(originMember, 'y', int)
        isValidInput = type(originX)!=None and type(originY)!=None
        if(isValidInput):    
            self.origin = (originX, originY)
        else:
            self.origin = None
            
    def _Load(self, xmlMember, tag, targetType):
        """
        Method to load specified tag from xmlMember, and cast to targetType.
        If specified type not found, method returns None.
        """
        try:
            return targetType( xmlMember.find(tag).text )
        except AttributeError:
            return None
            
    
    fieldNames = {
                  # Relates field names (as strings) to the load methods
                      'time': _LoadTime, 
                      'scale':_LoadScale,
                      'wavelength': _LoadWavelength,
                      'shotFileName': _LoadShotFileName,
                      'backFileName': _LoadBackFileName,
                      'shadowFileName': _LoadShadowFileName,
                      'origin': _LoadOrigin,
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
            