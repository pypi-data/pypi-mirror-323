#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pump-probe overlap analysis script.

Generate a pump-probe XYZ overlap report. The report contains three panels
which show the FWHM beam size and the focus X and Y position as a function of
the Z position.

Please specify the objective type and the device serial number

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of HARPIA-MM Microscopy
Extension.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2024 Light Conversion
All rights reserved.
www.lightcon.com
"""
from .dep_check import harpiamm_dep_check
harpiamm_dep_check()

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from harpiamm.overlap_analysis import make_overlap_report

app = QApplication(sys.argv)
widget = QWidget()

data_path = QFileDialog.getExistingDirectory(
    widget, "Select folder containing Pump/Probe focus image data")

# make_overlap_report() will be called next to analyze the pump-probe overlap
# data and produce a report. If the obj_id and device_sn arguments are not set
# a dialog will be shown for user input. Typical arguments are:
#   obj_id='nikon_pf_10x'
#   device_sn="M00000"
# The following objective ids are supported: nikon_pf_4x, nikon_pf_10x
# The device serial number must be in the M00000 format
make_overlap_report(path=data_path)

input("Press any key to close this window")
