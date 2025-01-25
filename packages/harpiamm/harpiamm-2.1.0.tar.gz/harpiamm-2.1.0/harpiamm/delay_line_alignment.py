#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA-TA delay line alignment using a camera.

LEGACY NOTICE: Please use the newer HARPIA Service App delay line alignment
functionality. This file provides older functions that do the same.


This module provides routines for the alignment of the HARPIA-TA delay line.

The delay line is controlled by the HARPIA Service App and the beam position is
observed by a camera using the Camera App. Both HARPIA Service App and the
Camera App need to be running with REST serivce enabled and operational. In
addition, the beam profiling function needs to be enabled on the Camera App.

The script connects to the HARPIA Service App and the Camera App over REST,
and records the probe delay line position and the beam position on the
camera. The graph shows the X and Y beam position as a function of the delay
time, and reports the min/max position variation. The graphs can be cleared by
pressing Reset.

Alignment is performed by enabling delay line oscillation and adjusting the
direction of the beam going into the delay line until the reported beam
position variation is minimized.

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
from tkinter import *
from tkinter import ttk
import threading

import matplotlib.pyplot as plt

from lightcon.harpia import Harpia
from lightcon.camera_app_client import CameraApp

# The clear axes flag serves as a crude interthread communication variable
CLEAR_AXES = False


def measure_func(
        harpia_address='127.0.0.1', harpia_port=20050,
        cam_address='127.0.0.1', cam_port=20080):
    """Delay line alignment function."""
    global CLEAR_AXES
    print("HARPIA Delay Line Alignment Tool")

    try:
        print("Connecting to HARPIA Service App at {:}:{:}...".format(harpia_address, harpia_port))
        H = Harpia(harpia_address, port=harpia_port)
    except Exception as excpt:
        print("Could not connect to HARPIA Service App")
        print("Reason: ", excpt)
        return None

    print("Connected to HARPIA Service App")

    try:
        cam = CameraApp(cam_address, port=cam_port)
        print("Connecting to Camera App at {:}:{:}...".format(cam_address, cam_port))
    except Exception as excpt:
        print("Could not connect to Camera App")
        print("Reason: ", excpt)
        return None

    print("Connected to Camera App")

    H.open_probe_shutter()
    H.close_pump_shutter()

    if not cam.get_beam_profiler_status():
        print("Enabling camera beam profiler...")
        cam.enable_beam_profiler()

    plt.figure(1)
    plt.clf()
    ax_x = plt.subplot(2, 1, 1)
    ax_y = plt.subplot(2, 1, 2)

    min_x = None
    max_x = None

    min_y = None
    max_y = None

    while(1):
        delay = H.delay_line_actual_delay()
        beam_par = cam.get_beam_parameters()
        beam_x = beam_par.get('MeanX')
        beam_y = beam_par.get('MeanY')
        print("Beam position: {:.2f}, {:.2f} mm at  {:.2f} ns".format(beam_x, beam_y, delay/1000))

        if CLEAR_AXES:
            min_x = None
            max_x = None
            min_y = None
            max_y = None

        if min_x is None:
            min_x = beam_x
            max_x = beam_x

        if min_y is None:
            min_y = beam_y
            max_y = beam_y

        if beam_x < min_x:
            min_x = beam_x

        if beam_x > max_x:
            max_x = beam_x

        if beam_y < min_y:
            min_y = beam_y

        if beam_y > max_y:
            max_y = beam_y

        plt.sca(ax_x)
        if CLEAR_AXES:
            plt.cla()
        plt.scatter(delay, beam_x, c='k')
        plt.title("Variation X: {:.1f} um, Y: {:.1f} um".format(
            (max_x - min_x)*1000, (max_y - min_y)*1000))
        plt.sca(ax_y)
        if CLEAR_AXES:
            plt.cla()
        plt.scatter(delay, beam_y, c='k')
        if CLEAR_AXES:
            CLEAR_AXES = False
        plt.pause(0.05)

    H.close_probe_shutter()
    H.close_pump_shutter()

def reset_graph():
    global CLEAR_AXES
    CLEAR_AXES = True
    print("Reset graph")

def delay_line_alignment(**kwargs):
    print("\n=== HARPIA delay line alignment tool ===")
    root = Tk()
    root.title("HARPIA Delay Line Alignment Tool")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ttk.Button(mainframe, text="Reset", command=reset_graph).grid(column=0, row=0, sticky=W)

    root.bind('<Return>', reset_graph)

    x = threading.Thread(target=measure_func, daemon=True, kwargs=kwargs)
    x.start()

    root.mainloop()

    print("All done")
