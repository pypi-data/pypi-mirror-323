#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""List Teledyne/FLIR cameras.

This script lists FLIR cameras to check whether everything is working.

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
import pkg_resources

spinnaker_ver = None
try:
    spinnaker_ver = pkg_resources.get_distribution('spinnaker-python').version
except pkg_resources.DistributionNotFound:
    print("Spinnaker API not installed")

if spinnaker_ver is not None:
    print("Loading Spinnaker API {:s}...".format(spinnaker_ver),
          end='', flush=True)
    import PySpin
    print('OK')

    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()

    if len(cam_list) > 0:
        print("Camera list:")
        for ind, cam in enumerate(cam_list):
            # GetUniqueID is supposed to return camera serial number, but
            # returns VID/PID instead. It can be used without initializing the
            # camera, which is supposed to work on cameras that might be
            # initialized in other apps.
            # However, it seems to be fine to use cam.Init() and then querry
            # DeviceSerialNumber() to get the serial number reliably.
            unique_id = cam.GetUniqueID()
            cam.Init()
            model_str = cam.DeviceModelName.GetValue()
            sn_str = cam.DeviceSerialNumber.GetValue()
            cam.DeInit()
            print(f"Camera {ind}, model: {model_str}, SN: {sn_str}, unique_id {unique_id}")
    else:
        print("No cameras found")
