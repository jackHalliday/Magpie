# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 18:30:32 2016

@author: Jack
"""
import MAGPIExml
import xml.etree.ElementTree as ET
xmlFileName = "example.xml"


xmlData = ET.parse(xmlFileName)
root = xmlData.getroot()
xmlShot = root.getchildren()[0]

shot = MAGPIExml.Shot(xmlShot)
interferometry = shot.diagnostics['interferometry']

xmlShot2 = shot.Store()
shot2 = MAGPIExml.Shot(xmlShot2)