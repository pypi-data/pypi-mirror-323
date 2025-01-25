#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA probe delay line alignment script.

Test and align the HARPIA-TA probe delay line by moving the stage back and
forth and monitoring the beam profile position using camera app.

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

from harpiamm.delay_line_alignment import delay_line_alignment

delay_line_alignment(cam_port='20042')
