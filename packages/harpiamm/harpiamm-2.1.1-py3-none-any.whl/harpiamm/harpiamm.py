#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA Microscopy Module Python library.

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
import numpy as np
from lkcom.image import make_gif, load_img, comb_img

def enumerate_overlap_scan_files(path=".", **kwargs):
    """Enumerate pump-probe overlap data files.

    File names are returned sorted by Z positions in um.
    """
    [file_names, zarr] = enum_files(
        path=path, extension="png", preffix="img", **kwargs)
    zarr = zarr*1000
    return [file_names, zarr]

def get_number_of_pixels(sensor):
    """Get the number of camera pixels.

    This helper function is used to make sure the number of camera pixels is
    correct. Physical calibration errors might creep in if the number of pixels
    is hardcoded and especially if the camera sensor is changed.

    The get_camera_pixel_size() function serves a similar purpose.
    """
    if sensor=="ICX445":
        return [1288, 964]

    print("Unknown sensor " + str(sensor))

def get_pixel_size(xarr, yarr):
    """Get mean pixel size of XY coordinate arrays."""
    return np.mean(np.concatenate((np.diff(xarr), np.diff(yarr))))

def gen_combined_focusing_anim(verbose=False):
    """Generate a combined focusing animation showing pump and probe beams.

    TODO: Work in progress.
    """
    path_pu = r"Pump no Cube"
    path_pr = r"Probe no Cube"

    print("Enumerating pump files...")
    [file_names_pu, Z_arr_pu] = enum_files(path=path_pu, extension="dat", preffix="I", files_to_remove=".\\I.dat", prepend_path=True, verbose=verbose)
    print("Enumerating probe files...")
    [file_names_pr, Z_arr_pr] = enum_files(path=path_pr, extension="dat", preffix="I", files_to_remove=".\\I.dat", prepend_path=True, verbose=verbose)

    print("Reading pump images...")
    images_pu = load_img(file_names=file_names_pu)
    print("Reading probe images...")
    images_pr = load_img(file_names=file_names_pr)

    images = comb_img(images_pu, images_pr)

    labels = []
    for Z in Z_arr_pr:
        labels.append("Z={:+d}".format(int(np.round(Z/10)*10)))

    make_gif(images=images, labels=labels, resize=True, verbose=verbose)
