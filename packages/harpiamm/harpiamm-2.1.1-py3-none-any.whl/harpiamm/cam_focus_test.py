#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA-MM pump-probe XYZ overlap characterization using a camera.

This module provides routines for the characterization of the pump and probe
beam focus and overlap using a camera placed at the sample plane. Images are
acquired as the camera is moved though the focus by the sample stage. The
camera is controlled via the FLIR/Teledyne Spinnaker API, and the stage is
controlled using HARPIA API.

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
import time
import os
import json
import datetime
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import PySpin
import xml.etree.ElementTree as ET

from lightcon.harpia import Harpia


def read_setup(par_name=None, file_name='setup.xml'):
    """Read setup XML file."""
    try:
        with open(file_name, encoding="utf-8") as file:
            setup = json.load(file)
            return setup.get(par_name, None)
    except Exception:
        return None

def get_image_with_ae(cam, img_mask=None):
    """Get camera image with autoexposure."""

    # Make sure that the camera exposure is set in us
    exposure_units = cam.ExposureTime.GetUnit()
    if exposure_units == 'us':
        exposure_fac = 1E-6
    else:
        raise ValueError("Unsupported exposure time units '{:s}'".format(
            exposure_units))

    max_exposure = cam.ExposureTime.GetMax()
    min_exposure = cam.ExposureTime.GetMin()
    exposure = cam.ExposureTime.GetValue()

    while True:
        # First image in an acquisition can be stale. Make sure to clear it
        # before calculating autoexposure.
        cam.AcquisitionStart()
        image_result = cam.GetNextImage()
        image_result.Release()

        cam.AcquisitionStart()
        image_result = cam.GetNextImage()
        img = image_result.GetData()

        img = img.reshape(image_result.GetHeight(), image_result.GetWidth())
        img = np.array(img)
        if img_mask is not None:
            if img.shape == img_mask.shape:
                img[img_mask] = 0
            else:
                print("Incorrect mask size. Clearing mask")
                img_mask = None

        max_val = img.max()
        if max_val >= 255:
            new_exposure = exposure*0.9
            if new_exposure < min_exposure:
                print("Max image value: {:}. Minimum exposure reached, cannot "
                      "decrease.".format(max_val))
                return img

            exposure = new_exposure
            print("Max image value: {:}. Decreasing exposure "
                  "to: {:.2f} ms".format(max_val, exposure*exposure_fac*1E3))
            cam.ExposureTime.SetValue(exposure)
        elif max_val < 100:
            new_exposure = exposure*1.1
            if new_exposure > max_exposure:
                print("Max image value: {:}. Maximum exposure reached, cannot "
                      "increase.".format(max_val))
                return img

            exposure = new_exposure
            print("Max image value: {:}. Increasing exposure "
                  "to: {:.2f} ms".format(max_val, exposure*exposure_fac*1E3))
            cam.ExposureTime.SetValue(exposure)
        else:
            return img


def cam_focus_test(
        start_pos=-2, end_pos=2, num_steps=50,
        meas_seq='bmb',
        cam_id=None, cam_sn=None, show_img=False,
        measure_pump=True, measure_probe=True,
        use_cam=True, use_shutters=True, dry_run=False):
    """Scan HARPIA XYZ sample stage Z axis and take an image at each step.

    The scan extent is configured by '''start_pos''', and '''end_pos''' and
    '''num_steps'''. Start and stop positions are given in mm.

    Measurement sequence is determined by '''meas_seq'''.
    In beam-move-beam ('bmb') sequence, the probe shutter is open, images are
    acquired for each stage position, and the probe shutter is closed. The
    procedure is then repeated for the pump beam.

    In move-beam-beam ('mbb') sequence, the stage is stepped over measurement
    positions, and at each position two images are taken for the pump and the
    probe beams by opening and closing each shutter.

    The 'bmb' sequence is recommended because it has fewer shutter open and
    close events and is thus faster than 'mbb'.

    In 'mbb' sequence the pump and probe images are acquired one after the
    other without moving the sample stage, resulting in a lower time delay
    between the images. In some setups the probe beam needs time to stabilize,
    so the 'mbb' sequence becomes slow or prone to systemic errors if the probe
    beam measurement is taken too soon after the shutter is opened.

    The sample stage camera can be selected by ID as enumerated by the camera
    driver using '''cam_id''', or serial number using '''cam_sn'''.

    By default the script measures both pump and probe beams unless
    '''measure_pump''' or '''measure_probe''' are set to false.

    The use of a camera or shutters can be disabled for debugging via
    '''use_cam''' and '''use_shutters''', although this will likely produce
    unusable data.

    The script can also be run in dry mode using '''dry_run''' to make sure the
    measurement sequence works as intended without moving any motors.
    """
    print("\n=== HARPIA pump-probe XYZ overlap camera scan ===")

    # Wait after shutter is open for the beam to stabilize
    probe_on_delay_s = 2
    pump_on_delay_s = 0.5

    print("Scan configuration: from {:.2f} mm, to {:.2f} mm, "
          "num_steps {:d}".format(start_pos, end_pos, num_steps))

    # Make sure that the data directory exists
    try:
        os.mkdir(r".//data")
    except FileExistsError:
        pass
    except Exception as excpt:
        raise RuntimeError("Cannot create data folder") from excpt

    # Make sure the script has write access to the data directory
    try:
        tmp_file_name = r".//data/test.tmp"
        np.savetxt(tmp_file_name, [123])
    except PermissionError as excpt:
        raise RuntimeError("Write access to the data folder is denied. Run the"
                           " script from a folder where the current user has "
                           "write access.") from excpt
    os.remove(tmp_file_name)

    # Create a timestsamped folder for the current scan
    timestamp = datetime.datetime.now()
    timestamp_str = timestamp.strftime('%Y-%m-%d %H%M%S')
    data_dir = 'data/' + timestamp_str + ' - Overlap scan/'
    os.mkdir(data_dir)

    # Create pump and probe subdirs
    pump_dir = data_dir + "Pump/"
    probe_dir = data_dir + "Probe/"
    os.mkdir(pump_dir)
    os.mkdir(probe_dir)

    # Determine HARPIA camera SN to not touch it
    try:
        file_name = "C:/Users/Public/Documents/Light Conversion/HARPIA Service App/Settings/deviceSettings.xml"
        xml_data = ET.parse(file_name)
        for section in xml_data.getroot().findall('configSection'):
            if section.get('name') == 'Microscope':
                harpia_cam_sn = section.findall('lastUsedCameraSerialNumber')[0].text
                print(f"HARPIA camera SN {harpia_cam_sn}")
    except Exception as excpt:
        print("Could not determine HARPIA camera SN")
        harpia_cam_sn = None

    # TODO: It would be better to abstract specific camera API or CameraApp
    # REST on a separate abstact camera layer (MSD-2228)
    if use_cam:
        # Init camera
        print("Listing cameras...")
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()

        if len(cam_list) == 0:
            print("No cameras found, cannot continue")
            return
        else:
            print(f"Number of cameras detected: {len(cam_list)}")
            cam_sn_list = []
            for ind, cam2 in enumerate(cam_list):
                # It should be safe to Init and DeInit cameras that are in use.
                # cam.GetUniqueID() can be used without Init, but it returns
                # VID/PID instead of SN.
                cam2.Init()
                cam_sn_list.append(cam2.DeviceSerialNumber.GetValue())
                cam2.DeInit()
                print(f"\t{ind}: {cam_sn_list[-1]}")

        # Automatically determine camera to be used based on cam_id and cam_sn
        cam = None
        if cam_id is None and cam_sn is None:
            # If neither cam_id nor cam_sn is supplied use the first available
            # camera that is not HARPIA Brightfield
            if harpia_cam_sn is None:
                cam_id = 0
            else:
                for ind, cam_sn1 in enumerate(cam_sn_list):
                    if cam_sn1 != harpia_cam_sn:
                        cam_id = ind
                        cam_sn = cam_sn_list[ind]
                        break
        elif cam_id is not None:
            # If cam_id is supplied, check that it's not used by HARPIA and use
            # it
            if harpia_cam_sn and cam_sn_list[cam_id] == harpia_cam_sn:
                print(f"cam_id {cam_id} corresponds to HARPIA camera, select a different camera")
                return
            cam_sn = cam_list[cam_id]
        elif cam_sn is not None:
            # If cam_sn is supplied, check that it's not used by HARPIA and use
            # it
            if harpia_cam_sn and cam_sn == harpia_cam_sn:
                print(f"cam_sn {cam_sn} corresponds to HARPIA camera, select a different camera")
                return
            for ind, cam_sn1 in enumerate(cam_sn_list):
                if cam_sn1 == cam_sn:
                    cam_id = ind
                if cam_id == None:
                    print(f"Camera SN {cam_sn} not found")
        else:
            raise RuntimeError("Internal error while parsing camera list")

        if cam_id is None:
            raise RuntimeError("Could not identify camera to use")

        cam_sn = cam_sn_list[cam_id]
        cam = cam_list[cam_id]

        # Sample plane cameras get damaged often resulting in stuck pixels
        # that mess up autoexposure and beam shape fitting. An image mask
        # is used to suppress unwanted pixels by setting them to zero.
        img_mask = None
        mask_file_name = 'img_mask.png'
        if Path(mask_file_name).is_file():
            print("Loading image mask from '{:s}'".format(mask_file_name))
            mask_data = Image.open(mask_file_name)
            print("Mask image size is {:d}x{:d}, mode: {:s}".format(
                mask_data.size[0], mask_data.size[1], mask_data.mode))
            if mask_data.mode != '1':
                # The image mask is supposed to be binary, but sometimes it is
                # useful to just crop and save an acquired image. If the mask
                # is not binary, convert it to binary and save it.
                print("Converting mask to binary")
                mask_data.convert('1')
                mask_data.save(mask_file_name)
            img_mask = np.array(mask_data) != 0

    # Init completed, now the actual scan

    try:
        start_t = time.time()
        if use_cam:
            print("Initalizing camera...")
            cam.Init()

            model_str = cam.DeviceModelName.GetValue()
            sn_str = cam.DeviceSerialNumber.GetValue()
            print("Connected to " + model_str + ', SN: ' + sn_str)

            # Set acquisition mode to single frame
            # NOTE: Continuous might sound better, but there are some strange
            # buffering issues, which result in old images being returned as
            # the sample stage is moved.
            nodemap = cam.GetNodeMap()
            node_acquisition_mode = PySpin.CEnumerationPtr(
                nodemap.GetNode('AcquisitionMode'))

            node_acquisition_mode_singleframe = \
                node_acquisition_mode.GetEntryByName('SingleFrame')

            acq_mode_singleframe = node_acquisition_mode_singleframe.GetValue()
            node_acquisition_mode.SetIntValue(acq_mode_singleframe)


            # Turn off auto exposure and auto gain
            # TODO: We probably want to reset these parameters to what they
            # were after the script is completed
            cam.ExposureAuto.SetValue(0)
            cam.GainAuto.SetValue(0)

            cam.BeginAcquisition()

        pos_arr = np.linspace(start_pos, end_pos, num_steps)

        # Connect to a local HARPIA
        harpia_ip = '127.0.0.1'
        print("Connecting to HARPIA Service App at " + harpia_ip)
        try:
            harpia = Harpia(harpia_ip)
        except Exception as excpt:
            print("HARPIA Service App connection was refused. Check if app is running and REST is enabled.")
            return

        if use_shutters:
            if measure_probe and not dry_run:
                harpia.close_probe_shutter()
            if measure_pump and not dry_run:
                harpia.close_pump_shutter()

        if show_img:
            plt.figure(1)
            plt.clf()

        if measure_probe and measure_pump:
            probe_ax = plt.subplot(1, 2, 1)
            pump_ax = plt.subplot(1, 2, 2)
        else:
            if measure_probe:
                probe_ax = plt.gca()
            if measure_pump:
                pump_ax = plt.gca()

        default_exp = 8000

        if use_cam:
            cam.ExposureTime.SetValue(default_exp)

        pump_exp = default_exp
        probe_exp = default_exp

        if meas_seq == 'mbb':
            # MBB strategy: move, measure probe and pump, then move
            for ind,pos in enumerate(pos_arr):
                print("Step {:} of {:}, pos={:.2f} mm".format(
                    ind+1, num_steps, pos))
                if not dry_run:
                    harpia.microscope_set_sample_stage_position_Z(pos*1000)

                if measure_probe:
                    # Measure probe beam
                    if use_shutters and not dry_run:
                        harpia.open_probe_shutter()
                        time.sleep(probe_on_delay_s)

                    if use_cam:
                        cam.ExposureTime.SetValue(probe_exp)

                        print("Acquiring probe image...")
                        img = get_image_with_ae(cam, img_mask=img_mask)
                        print("Done. Image val range [{:d}, {:d}]".format(
                            np.min(img), np.max(img)))
                        probe_exp = cam.ExposureTime.GetValue()
                    if use_shutters and not dry_run:
                        harpia.close_probe_shutter()

                    if use_cam:
                        plt.imsave(probe_dir + "img_{:.2f}.png".format(
                            pos_arr[ind]), img, cmap='gray', vmin=0, vmax=255)

                    if show_img:
                        plt.sca(probe_ax)
                        plt.imshow(img)

                if measure_pump:
                    # Measure pump beam
                    if use_shutters and not dry_run:
                        harpia.open_pump_shutter()
                        time.sleep(pump_on_delay_s)

                    if use_cam:
                        cam.ExposureTime.SetValue(pump_exp)
                        print("Acquiring pump image...")
                        img = get_image_with_ae(cam, img_mask=img_mask)
                        print("Done. Image val range [{:d}, {:d}]".format(
                            np.min(img), np.max(img)))
                        pump_exp = cam.ExposureTime.GetValue()

                    if use_shutters and not dry_run:
                        harpia.close_pump_shutter()

                    if use_cam:
                        plt.imsave(pump_dir + "img_{:.2f}.png".format(
                            pos_arr[ind]), img, cmap='gray', vmin=0, vmax=255)

                    if show_img:
                        plt.sca(pump_ax)
                        plt.imshow(img)

                if show_img:
                    plt.pause(0.05)

        elif meas_seq == 'bmb':
            # BMB strategy: move and measure all probe positions, then pump
            if measure_probe:
                # Measure probe beam
                if use_shutters and not dry_run:
                    harpia.open_probe_shutter()
                    time.sleep(probe_on_delay_s)

                for ind, pos in enumerate(pos_arr):
                    print("Step {:} of {:}, pos={:.2f} mm".format(
                        ind+1, num_steps, pos))
                    if not dry_run:
                        harpia.microscope_set_sample_stage_position_Z(pos*1000)

                    if use_cam:
                        cam.ExposureTime.SetValue(probe_exp)
                        print("Acquiring image...")
                        img = get_image_with_ae(cam, img_mask=img_mask)
                        print("Done. Image val range [{:d}, {:d}]".format(
                            np.min(img), np.max(img)))
                        probe_exp = cam.ExposureTime.GetValue()
                        plt.imsave(probe_dir + "img_{:.2f}.png".format(
                            pos_arr[ind]), img, cmap='gray', vmin=0, vmax=255)

                    if show_img:
                        plt.sca(probe_ax)
                        plt.imshow(img)
                        plt.pause(0.05)

            if measure_pump:
                # Measure pump beam
                if use_shutters and not dry_run:
                    harpia.close_probe_shutter()
                    harpia.open_pump_shutter()
                    time.sleep(pump_on_delay_s)

                for ind,pos in enumerate(pos_arr):
                    print("Step {:} of {:}, pos={:.2f} mm".format(
                        ind+1, num_steps, pos))
                    if not dry_run:
                        harpia.microscope_set_sample_stage_position_Z(pos*1000)
                    print("Move completed")

                    if use_cam:
                        cam.ExposureTime.SetValue(pump_exp)
                        print("Acquiring image...")
                        img = get_image_with_ae(cam, img_mask=img_mask)
                        print("Done. Image val range [{:d}, {:d}]".format(
                            np.min(img), np.max(img)))
                        pump_exp = cam.ExposureTime.GetValue()
                        plt.imsave(pump_dir + "img_{:.2f}.png".format(
                            pos_arr[ind]), img, cmap='gray', vmin=0, vmax=255)

                    if show_img:
                        plt.sca(pump_ax)
                        plt.imshow(img)
                        plt.pause(0.05)

        if use_shutters and not dry_run:
            if measure_probe:
                harpia.close_probe_shutter()
            if measure_pump:
                harpia.close_pump_shutter()

        print("Moving to starting position: {:.2f} mm".format(pos_arr[0]))
        if not dry_run:
            harpia.microscope_set_sample_stage_position_Z(pos_arr[0]*1000)

        if use_cam:
            cam.EndAcquisition()
            cam.DeInit()
            del cam

        print("All done")
    except Exception as excpt:
        raise RuntimeError("Scanning failed") from excpt

    print("Total time elapsed: {:.1f} s".format(time.time() - start_t))


if __name__ == '__main__':
    cam_focus_test()
