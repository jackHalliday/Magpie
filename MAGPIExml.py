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
        self.tag = xmlMember.tag
        self.path = xmlMember.find('filePath').text

    # IO methods for all valid fields should be defined here.
    # Classes which inherit from Diagnostic should not define their own IO 
    # methods: Fields used in multiple diagnostics & have to ensure consistency.
    # If a field is not found in the XML, its load method should write a None 
    # type to the target variable. 
    def _IoTime(self, xmlMember, tag, load=True):
        if(load):
            self.time = self._Load(xmlMember, tag, float)
        else:
            self._Store(self.time, xmlMember,tag, str)
        
    def _IoScale(self, xmlMember, tag, load=True):
        if(load):
            self.scale = self._Load(xmlMember, tag, float)
        else:
            self._Store(self.scale, xmlMember,tag, str)
        
    def _IoWavelength(self, xmlMember, tag, load=True):
        if(load):   
            self.wavelength = self._Load(xmlMember, tag, str)
        else:
            self._Store(self.wavelength, xmlMember,tag, str)
        
    def _IoShotFileName(self, xmlMember, tag, load=True):
        if(load):
            self.shotFileName = self._Load(xmlMember, tag, str)
        else:
            self._Store(self.shotFileName, xmlMember,tag, str)

    def _IoBackFileName(self, xmlMember, tag, load=True):
        if(load):
            self.backFileName = self._Load(xmlMember, tag, str)
        else:
            self._Store(self.backFileName, xmlMember, tag, str)
    
    def _IoShadowFileName(self, xmlMember, tag, load=True):
        if(load):
            self.shadowFileName = self._Load(xmlMember, tag, str)
        else:
            self._Store(self.shadowFileName, xmlMember,tag, str)

    def _IoOrigin(self, xmlMember, tag, load=True):
        #TODO: tidy this method up -- there is a less ugly way to do this
        if(load):
            try:
                originMember = xmlMember.find(tag)
                originX = self._Load(originMember, 'x', int)
                originY = self._Load(originMember, 'y', int)
                isValidInput = type(originX)!=None and type(originY)!=None
                if(isValidInput):    
                    self.origin = (originX, originY)
                else:
                    self.origin = None
            except AttributeError:
                return None
        else:
            if( type(self.origin)!=None ):
                originMember = ET.Element(tag)
                xmlMember.append(originMember)
                self._Store(self.origin[0], originMember, 'x', str)
                self._Store(self.origin[1], originMember, 'y', str)
                    
    def _Load(self, xmlMember, tag, cast):
        """
        Loads specified tag from xmlMember, then acts on loaded data with cast
        function & returns result. If the tag is not found in xmlMember, 
        returns None.
        """
        try:
            return cast( xmlMember.find(tag).text )
        except AttributeError:
            return None
    
    def _Store(self, value, xmlMember, tag, cast):
        """
        Creates a child of xmlMember, with specified tag, and the result of 
        cast(value) as text 
        """
        if( type(value)!= type(None) ):
            childMember = ET.Element(tag)
            childMember.text = cast(value)
            xmlMember.append(childMember)
    
    fieldNames = {
                  # Relates field names (as strings) to the load methods
                      'time': _IoTime, 
                      'scale':_IoScale,
                      'wavelength': _IoWavelength,
                      'shotFileName': _IoShotFileName,
                      'backFileName': _IoBackFileName,
                      'shadowFileName': _IoShadowFileName,
                      'origin': _IoOrigin,
                       }
    def LoadFields(self, fieldNameList, xmlMember):
        """
        Loads all the fields given in the fieldName list. Elements of this list
        must be keys in the fieldNames member variable
        """
        #TODO: Refactor so this method is consistant with StoreFields
        for tag in fieldNameList:
            try:
                self.fieldNames[tag](self, xmlMember, tag)
            except KeyError:
                print ("An unknown field name was provided: "+ tag)
                
    def StoreFields(self, xmlMember):
        """
        Packs all the member variables as child elements in xmlMember. Method 
        does not check to see if xmlMember already contains an entry for each 
        field so implicitly  assumes that xmlMember is an empty xml object!
        """
        childMember = ET.Element('filePath')
        childMember.text = self.path
        xmlMember.append(childMember)
        for tag in self.includedFields:
            try:
                self.fieldNames[tag](self, xmlMember, tag, False)
            except KeyError:
                print ("An unknown field name was provided: "+ tag)

class Interferometry (Diagnostic):
    """
    Class to handle interferometry data
    """
    includedFields = ['time', 'scale', 'wavelength', 'shotFileName', 'origin',
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
        #TODO: take the tag names out of this class, declare them as statics in
        # a seperate class, simmilar for diagnostic classes.
        self.filePath = xmlMember.find('filePath').text
        self.name = xmlMember.attrib['name']
        self.description = self._Load(xmlMember, 'description')
        self.diagnostics = { }
        for xmlChild in xmlMember.iter('diagnostic'):
            diagnosticType = xmlChild.attrib['type']
            try:
                diagnostic = self.diagnosticClasses[diagnosticType](xmlChild)
                self.diagnostics[diagnosticType] = diagnostic  
            except KeyError:
                print ("Diagnostic type: " + diagnosticType + " is unknown")

    def _Load(self, xmlMember, tag):
        try:
            return xmlMember.find(tag).text
        except AttributeError:
            return None
    
    def Store(self):
        xmlMember = ET.Element(self.name)
        xmlMember.attrib = {'name': self.name}
        childMember = ET.Element('filePath')
        childMember.text = self.filePath
        xmlMember.append(childMember)
        childMember = ET.Element('description')
        childMember.text = self.description
        xmlMember.append(childMember)
        
        for key, value in self.diagnostics.items():
            childMember = ET.Element('diagnostic') 
            childMember.attrib = {'type': key}
            value.StoreFields(childMember)
            xmlMember.append(childMember)
    
        return xmlMember
                

            