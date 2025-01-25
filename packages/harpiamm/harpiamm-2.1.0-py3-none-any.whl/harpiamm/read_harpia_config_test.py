#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read HARPIA device config example.

Read and parse HARPIA device config XML file

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
import xml.etree.ElementTree as ET

file_name = "C:/Users/Public/Documents/Light Conversion/HARPIA Service App/Settings/deviceSettings.xml"
file_name = "test_data/deviceSettings.xml"

try:
    xml_data = ET.parse(file_name)
    for section in xml_data.getroot().findall('configSection'):
        if section.get('name') == 'Microscope':
            harpia_cam_sn = section.findall('lastUsedCameraSerialNumber')[0].text
            print(f"HARPIA camera SN {harpia_cam_sn}")
except Exception as excpt:
    print("Could not determine HARPIA camera SN")
    harpia_cam_sn = None
