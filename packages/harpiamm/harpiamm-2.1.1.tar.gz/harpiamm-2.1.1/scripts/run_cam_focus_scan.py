#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pump-probe XYZ overlap images using a sample plane camera.

Acquire pump and probe overlap images using a sample plane camera.

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

from harpiamm.cam_focus_test import cam_focus_test

# Start and end pos are in mm. Camera to use can be specified either by SN or
# index (cam_id) in the list as reported by PySpin GetCameras(). Enumeration by
# SN often fails due to a bug in PySpin, and there is no easy way for the end
# user to find out camera IDs. However, cam_id is useful to simply select the
# "other" camera when the wrong camera is selected and the script does not run.
cam_focus_test(start_pos=-2, end_pos=2, num_steps=50, cam_id=None, cam_sn=None)
