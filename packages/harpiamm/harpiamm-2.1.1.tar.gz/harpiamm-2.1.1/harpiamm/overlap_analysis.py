#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pump-probe XYZ overlap analysis.

Generate a pump-probe XYZ overlap report from data obtained using the
run_cam_focus_can.py script. The overlap data is obtained by moving a camera
through the focus using a sample. The report contains three panels which show
the FWHM beam size and the focus X and Y position as a function of the Z
position.

Please specify the objective type and the device serial number when prompted.

 - A note on pinhole overlap scan -
The HARPIA Microscopy Module was first aligned using a pinhole transmission
scan in which the transmitted power of pump and probe beams through a pinhole
was recorded as the pinhole was scanned around. A faster camera-based method
was developed later and the pinhole method was no longer used. The analysis
script diverged with limited support for pinhole scans in several places by
using the mode='pinhole' argument. Actual pinhole scan data analysis was not
tested in some time and likely got broken somewhere along the way. Furthermore,
a better version of the pinhole scan was developed for spectral PSF spectral
analysis, making the pinhole scan mode for this code deprecated.

Since the pinhole overlap scan method was developed first, it is often referred
to as 'OverlapScan', 'CalibrationScan', or 'XYZScan' with no reference of it
being specific to the pinhole scan only.

Code relating to pinhole scan analysis was removed from this module on
November 2023. It can still be found in the harpiamm code repo if needed.


This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of the HARPIA-MM extension
of the HARPIA spectroscopy system.

support@lightcon.com
www.lightcon.com
All rights reserved.
© 2019-2024 Light Conversion
"""
import os
import time
from warnings import warn
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage.measurements import center_of_mass
from PIL import Image

from lkcom.util import cut_by_x_range, get_common_range, isnone, \
     find_closest, get_color, get_exception_info_str, LogPrinter
from lkcom.standard_func import poly_2
from lkcom.string import join_paths
from lkcom.dataio import enum_files, check_file_exists
from lkcom.image import make_gif
from lkcom.plot import add_x_marker, add_y_marker, export_figure

from lkfit.gaussian_fit import fit_gaussian_2d
from lkfit.poly import fit_poly_2, get_poly_2_max_x

from harpiamm.harpiamm_ui import get_report_metainfo


def get_default_camera_sensor():
    """Get default camera sensor name."""
    return 'ICX445'

def get_camera_pixel_size(sensor=get_default_camera_sensor()):
    """Get the physical size of camera pixels.

    This helper function is used to make sure the camera pixel size is correct.
    Physical calibration errors might creep in if the pixel size is hardcoded
    and especially if the camera sensor is changed.

    The get_number_of_pixels() function serves a similar purpose.
    """
    if sensor=="ICX445":
        return 3.8

    print("Unknown sensor " + sensor)
    return None

def get_default_overlap_fit_result_filename():
    """Get default file name for overlap fit results."""
    return "fit_arr.txt"


def get_beam_parameters_from_img(
        img=None, file_name=None, pxsz=None, fit_image_title_str=None,
        fit_crop_area=None, fig_file_name=None, plot_fit_result=True,
        show_fit_result=False, save_fit_result_fig=False):
    """Get beam position and size parameters from a single image."""
    if img is None and file_name is None:
        raise RuntimeError("image or file name must be given")
    if pxsz is None:
        print("Camera pixel size not given, using default")
        pxsz = get_camera_pixel_size()

    if img is None:
        img = np.array(Image.open(file_name))
    imgsz = img.shape
    xarr = np.arange(0, imgsz[1])*pxsz
    yarr = np.arange(0, imgsz[0])*pxsz

    # Select the R channel in RGB images
    if len(imgsz)>2 and imgsz[2] > 1:
        img = img[:, : ,0]

    # Determine maximum intensity
    ampl = np.max(img)

    # Find center of mass
    center = center_of_mass(img)

    # TODO: Use ampl and center values as guesses

    if plot_fit_result:
        plt.figure()

    try:
        fit_result = fit_xy_profile(
            img, X=xarr, Y=yarr, pxsz=pxsz, crop_area=fit_crop_area,
            plot=plot_fit_result, suptitle_str=fit_image_title_str, fit_crop_area=fit_crop_area)
    except Exception as excpt:
        print(f"Error while fitting {excpt.__cause__}")
        return {
            'ampl': np.nan,
            'center': [np.nan, np.nan],
            'width': [np.nan, np.nan],
            'fit_result': None}

    if plot_fit_result:
        plt.draw()
        if show_fit_result:
            plt.show()

    if save_fit_result_fig:
        export_figure(fig_file_name)
        plt.close()

    beam_par = {
        'ampl': fit_result[0],
        'center': np.array(fit_result[1:3])*pxsz,
        'width': np.array(fit_result[3:5])*pxsz,
        'fit_result': fit_result}

    # Center position used to be rewritten at the end like so for unknown
    # reasons.
    # TODO: This is likely stale debugging code and can be removed
    # center[:, 0] = center[:, 0]*pxsz
    # center[:, 1] = center[:, 1]*pxsz
    # center = fit_arr[:, 2:4]

    return beam_par


def get_beam_parameters_from_zstack_dir(
        file_names, zarr=None, pxsz=None, fit_crop_area=None):
    """Get beam position and size parameters from image z-stack."""
    numf = len(file_names)

    beam_par = {
        'ampl': np.ndarray(numf),
        'center': np.ndarray([numf, 2]),
        'width': np.ndarray([numf, 2])}

    beam_par['ampl'].fill(np.nan)
    beam_par['center'].fill(np.nan)
    beam_par['width'].fill(np.nan)

    fit_arr = np.ndarray([len(file_names), 8])
    fit_arr.fill(np.nan)

    for ind, file_name in enumerate(file_names):
        try:
            print("Processing file {:d} {:s}".format(ind, file_name))
            fit_image_title_str = f"XY Profile at Z={zarr[ind]:.2f}"
            fig_file_name = "XY_profile_{:.2f}.png".format(zarr[ind])

            beam_par1 = get_beam_parameters_from_img(
                file_name=file_name, pxsz=pxsz,
                fit_image_title_str=fit_image_title_str,
                fit_crop_area=fit_crop_area,
                fig_file_name=fig_file_name,
                plot_fit_result=True,
                save_fit_result_fig=True)

            fit_arr[ind, 0] = zarr[ind]
            fit_arr[ind, 1:] = beam_par1['fit_result']

            np.savetxt(get_default_overlap_fit_result_filename(), fit_arr)

            beam_par['ampl'][ind] = beam_par1['ampl']
            beam_par['center'][ind, :] = beam_par1['center']
            beam_par['width'][ind, :] = beam_par1['width']

        except RuntimeWarning:
            msg = "A runtime warning occurred"
            if file_name is not None:
                msg += f" when processing file {file_name}"
            print(msg)
        except Exception as excpt:
            msg = "Could not fit"
            if file_name is not None:
                msg += f" file {file_name}"
            print(msg)
            print("Reason: ", excpt)

    return beam_par


def get_xyz_overlap_parameters(path='.', verbose=False, **kwargs):
    """Get XYZ overlap parameters.

    The retrieved parameters for every XY image are: Z position, controid
    locations, beam widths and maximum intensity.
    """
    cam_sensor = kwargs.get('cam_sensor')
    if cam_sensor is None:
        cam_sensor = get_default_camera_sensor()
        print("WARNING: camera sensor not defined, assuming {}".format(
            cam_sensor))

    # Load stored fit parameters, if available
    fit_arr_filename = join_paths(
        path, get_default_overlap_fit_result_filename())

    if check_file_exists(fit_arr_filename):
        fit_arr = np.loadtxt(fit_arr_filename)
        zarr = fit_arr[:, 0]
        ampl = fit_arr[:, 1]
        center = fit_arr[:, 2:4]
        width = fit_arr[:, 4:6]
        print("Loading stored fit parameters")
        return [zarr, ampl, center, width]

    # If no stored parameters found, enumerate, load and fit every image
    [file_names, zarr] = enum_files(
        path=path, extension="png", preffix="img", prepend_path=False,
        verbose=verbose, neg_inds=False)

    # Sort data so that Z position is increasing
    sort_order = np.argsort(zarr)
    zarr = zarr[sort_order]
    file_names = [file_names[i] for i in sort_order]

    pxsz = get_camera_pixel_size(cam_sensor)

    orig_path = os.getcwd()
    try:
        os.chdir(path)

        # Pump-probe overlap images from a sample plane camera capture way more
        # area than is needed for overlap characterization. Focused beams are
        # just a few pixels across, so it makes sense to crop the image to
        # a smaller size to increase fitting speed. The cropped image size is
        # determined from the estimated std. dev. of the 2D gaussian fit so
        # there are many ways this may not work...
        # TODO: cropping is likely done elsewhere
        crop_to_fit_region = True

        # Find the center of mass of the image closest to Z=0 and use it to
        # center the fit crop area for all images.
        z_zero_ind = find_closest(zarr, 0)
        img = np.array(Image.open(file_names[z_zero_ind]))

        # If the image is RGB, use the red channel
        # TODO: probably grayscale would be better
        imgsz = img.shape
        if len(imgsz) > 2 and img.shape[2] > 1:
            img = img[:, :, 0]

        # Background illumination can skew the center of mass of the image.
        # Set pixels at half the maximum intensity to zero to avoid that.
        # This might seem overzealous, but we are only masking here for center
        # of mass estimation, fitting will use all pixels and estimate the
        # background properly.
        img[img < np.max(img)/2] = 0
        fit_area_center = center_of_mass(img)

        # TODO: fit area is hardcoded, works well for ICX445, but perhaps not
        # for other sensors.
        fit_area_sz = [100, 100]
        fit_crop_area = np.round([
            fit_area_center[1] - fit_area_sz[1]/2,
            fit_area_center[1] + fit_area_sz[1]/2,
            fit_area_center[0] - fit_area_sz[0]/2,
            fit_area_center[0] + fit_area_sz[0]/2]).astype('int')

        beam_par = get_beam_parameters_from_zstack_dir(
            file_names=file_names, zarr=zarr, pxsz=pxsz, fit_crop_area=fit_crop_area)

        os.chdir(orig_path)

        # Center position used to be rewritten at the end like so for unknown
        # reasons.
        # TODO: This is likely stale debugging code and can be removed
        # center[:, 0] = center[:, 0]*pxsz
        # center[:, 1] = center[:, 1]*pxsz
        # center = fit_arr[:, 2:4]

    except Exception as excpt:
        os.chdir(orig_path)
        raise RuntimeError("Could not get overlap parameters") from excpt

    return [zarr, beam_par['ampl'], beam_par['center'], beam_par['width']]

def fit_xy_profile(data, **kwargs):
    """Fit a 2D gaussian to an XY profile."""
    return fit_gaussian_2d(data, **kwargs, return_fwhm=True)

def find_focus_position(
        zarr=None, ampl=None, color=None, yl=None, focus_fit_range=600,
        mode='max', fit_focus_curve=True, show_focus_marker=False, plot=True):
    """Find focus position.

    The function starts with a Z position estimate based on the maximum (or
    minimum) focus curve value. The focus curve is then fit with a parabola
    around the estimated position for a more precise result.

    Mode can be switched from 'max' to 'min' to facilitate cases where the
    signal is maximized and minimized at focus.
    """
    if mode=='max':
        z_focus_est = zarr[np.argmax(ampl)]
    elif mode=='min':
        z_focus_est = zarr[np.argmin(ampl)]

    # print.info("Estimated Z focus position: {:.1f} mm".format(z_focus_est))

    if z_focus_est > np.max(zarr) or z_focus_est < np.min(zarr):
        # TODO: Can this ever be true when using max/min functions above?
        zarr_focus = zarr
        ampl_focus = ampl
    else:
        [zarr_focus, ampl_focus] = cut_by_x_range(
            zarr, ampl,
            rng_fr=z_focus_est - focus_fit_range/2,
            rng_to=z_focus_est + focus_fit_range/2)

    if len(zarr_focus) < 3:
        print("Warning: not enough points (N<3) to find focal position")

    if fit_focus_curve:
        try:
            popt = fit_poly_2(
                X=zarr_focus,Y=ampl_focus, plot_fit=False, color=color)[0]
            z_focus = get_poly_2_max_x(popt)

            if plot:
                zarr_fmod = np.linspace(zarr.min(), zarr.max(), 100)
                plt.plot(
                    zarr_fmod, poly_2(zarr_fmod, *popt), color=color,ls='--')
                if show_focus_marker:
                    plt.plot([z_focus, z_focus], yl, color=color,ls='--')
        except Exception:
            print("Failed to fit the focus curve, using rought estimate as the"
                  " focus position")
            z_focus = z_focus_est
    else:
        z_focus = z_focus_est

    return z_focus

def report_num_failed_pts(fail_mask, message):
    """Print mask check result.

    Report the number of failed elements in an a mask check array.
    """
    num_failed = np.nansum(fail_mask)
    num_pts = len(fail_mask)
    if num_failed > 0:
        print("WARNING: {:d} out of {:d} ".format(num_failed, num_pts),
              message)

    # TODO: Might be useful to report the failed z positions too

def validate_profile_fit_results(par):
    """Validate beam profile fit results.

    Check whether the beam profile fit values are within the expected range.
    """
    # The maximum fit amplitude can be larger than 255 even though the 8-bit
    # data is capped at 255. Gaussian fits with narrow widths can spike well
    # above this value and still be valid. The 300 value is an educated guess.
    min_ampl = 10
    max_ampl = 300

    if par is None:
        return None

    name = par['name']

    ampl_fail = np.logical_or(par['ampl'] > max_ampl, par['ampl'] < min_ampl)
    report_num_failed_pts(ampl_fail, name + " fit amplitudes are "
                       "outside of the valid range")

    # Count the number of failed fits
    failed_pts = np.logical_or(np.logical_or(
            np.isnan(par['zpos']), np.isnan(par['width'][:, 0])), ampl_fail)

    if failed_pts.all():
        print("ERROR: All " + name + " fit values failed, there is no valid "
                    "data")
        return None
    if failed_pts.any():
        report_num_failed_pts(failed_pts, name + " fits failed, removing...")
        par['zpos'] = par['zpos'][np.logical_not(failed_pts)]
        par['ampl'] = par['ampl'][np.logical_not(failed_pts)]
        par['xypos'] = par['xypos'][np.logical_not(failed_pts), :]
        par['width'] = par['width'][np.logical_not(failed_pts), :]

    return par

def calc_plot_limits(par):
    """Calculate plot ranges for XYZ positions and XY widths."""
    zpos = par['zpos']
    xypos = par['xypos']
    width = par['width']

    # Determine XY position spans
    xspan = np.max(xypos[:,0]) - np.min(xypos[:,0])
    yspan = np.max(xypos[:,1]) - np.min(xypos[:,1])

    # Determine avg. width span
    width_avg = np.mean(width, 1)
    wspan = np.max(width_avg) - np.min(width_avg)

    # Calculate plot ranges for XYZ positions anx XY widths
    plot_xl = [np.min(xypos[:,0]) - xspan*0.1, np.max(xypos[:,0]) + xspan*0.1]
    plot_yl = [np.min(xypos[:,1]) - yspan*0.1, np.max(xypos[:,1]) + yspan*0.1]
    plot_zl = [np.min(zpos), np.max(zpos)]
    plot_wl = [ np.min(width_avg) - wspan*0.1, np.max(width_avg) + wspan*0.1 ]

    return [plot_xl, plot_yl, plot_zl, plot_wl]

def plot_overlap_scan_results(**kwargs):
    """Wrapper for old function name.

    TODO: Deprecate after 2025 Jan.
    """
    warn("Use plot_overlap_results() instead", DeprecationWarning)
    return plot_overlap_results(**kwargs)

def plot_overlap_results(
    zarr=None, ampl=None, center=None, width=None, width_metric='mean', show_focus_marker=True,
    ref_focus=None, z_axes=None, x_axes=None, y_axes=None, xy_axes=None,
    w_axes=None, xl=None, yl=None, zl=None, wl=None, color=None, show_fill=True, fill_color=None,
    with_titles=True, show_x_label=True, z_axes_ylabel_preffix=None, ampl_units=None,
    **kwargs):
    """Plot overlap analysis result figure.

    The figure contains three panels in which two curves show the overlap
    between pump and probe beams. Pump is blue, probe is red. The first panel
    shows the width of the beams as they go through focus. The second and third
    panels show the X and Y distances between the pump and probe beams as a
    function of Z.
    """
    if ref_focus is not None:
        focus_marker_color = get_color('dr')
    else:
        focus_marker_color = color

    xpos = center[:, 0]
    ypos = center[:, 1]


    ## === Plot width panel ===

    plt.sca(w_axes)

    # Plotting two (XY) curves for both beams makes the panel too cluttered.
    # Reduce the XY curves to one per beam using a given width metric for
    # better legibility.
    if width_metric not in ['mean', 'min', 'max']:
        warn('Undefined width mean metric, using mean')
        width_metric = 'mean'
    if width_metric == 'mean':
        width_plot = np.mean(width, 1)
    elif width_metric == 'min':
        width_plot = np.min(width, 1)
    elif width_metric == 'max':
        width_plot = np.max(width, 1)

    if show_fill:
        # Show width metric curve together with a fill to indicate the XY value
        # range which is useful for beam ellipticity
        plt.fill_between(zarr, width[:,0], width[:,1], color=fill_color)

    plt.plot(zarr, width_plot, c=color, linestyle='solid', marker='.')

    # Find the Z focus position from the width data
    z_focus = find_focus_position(
        zarr=zarr, ampl=width_plot, color=color, yl=[0,1.1], mode='min',
        focus_fit_range=2000, plot=False, **kwargs)

    # If no reference focus position is given, use the Z focus
    if ref_focus is None:
        ref_focus = z_focus

    # Show focus marker for reference
    if show_focus_marker:
        plt.plot([ref_focus, ref_focus], wl, c=focus_marker_color, ls='--')

    # Determine the average beam width at the reference focus position
    w_at_focus = np.interp(ref_focus, zarr, width_plot)
    plt.plot(zl, [w_at_focus, w_at_focus], c=color, ls='--')
    if with_titles:
        plt.title('FWHM={:.1f} µm'.format(w_at_focus))

    if show_x_label:
        plt.xlabel('Z position, µm')
    plt.ylabel('FWHM, µm ')
    plt.xlim(zl)
    plt.ylim(wl)
    plt.grid('on')
    add_x_marker(0, ls='-')
    plt.draw()


    ## === Plot X position panel ===

    plt.sca(x_axes)
    plt.plot(zarr, xpos, c=color, marker='.')

    # Mark the reference focus position
    plt.plot([ref_focus, ref_focus], xl, c=focus_marker_color,ls='--')

    # Determine the X position at the reference focus
    x_at_focus = np.interp(ref_focus, zarr, xpos)
    plt.plot(zl, [x_at_focus, x_at_focus], c=color, ls='--')
    if with_titles:
        plt.title('Focus position at X={:.1f} µm'.format(x_at_focus))

    if show_x_label:
        plt.xlabel('Z position, µm')
    plt.ylabel('X position, µm ')
    plt.xlim(zl)
    plt.ylim(xl)
    plt.grid('on')
    add_x_marker(0, ls='-')
    add_y_marker(0, ls='-')
    plt.draw()


    ## === Plot Y position panel ===

    plt.sca(y_axes)
    plt.plot(zarr, ypos, c=color, marker='.')

    # Mark the reference focus position
    plt.plot([ref_focus, ref_focus], yl, c=focus_marker_color, ls='--')

    # Determine the Y position at the reference focus
    y_at_focus = np.interp(ref_focus, zarr, ypos)
    plt.plot(zl,[y_at_focus,y_at_focus],c=color,ls='--')
    if with_titles:
        plt.title('Focus position at Y={:.1f} µm'.format(y_at_focus))

    if show_x_label:
        plt.xlabel('Z position, µm')
    plt.ylabel('Y position, µm ')
    plt.xlim(zl)
    plt.ylim(yl)
    plt.grid('on')
    add_x_marker(0, ls='-')
    add_y_marker(0, ls='-')
    plt.draw()

    return [z_focus, w_at_focus, x_at_focus, y_at_focus]

def make_xy_profile_gif(path='.', output_name="XYProfiles.gif", verbose=False):
    """Make a GIF of XY profile fit figures ordered by Z position."""
    output_path = join_paths(path, output_name)
    if check_file_exists(output_path):
        print("{:} already exists, assuming it is up to date and skipping GIF "
              "generation".format(output_path))
        return

    file_names = enum_files(
        path=path, extension="png", preffix="XY_profile", verbose=verbose,
        prepend_path=True)[0]

    if verbose:
        print("Found {:d} files".format(len(file_names)))
        print("Making GIF...")

    make_gif(file_names=file_names, output_name=output_path)

    if verbose:
        print("Done")

def make_overlap_report(**kwargs):
    """Wrapper for generating pump-probe overlap report with logging to file."""
    with LogPrinter():
        _make_overlap_report(**kwargs)

def _make_overlap_report(
        path=r'./', width_metric='mean', xy_pos_rel_to_z0=True,
        fig_style='whole_range', subplot_rows=1, subplot_row=0,
        plot_wl=None, suptitle_str=None, obj_id=None,
        device_sn=None, date_str=None):
    """Analyze beam overlap, make a report figure and animations."""
    print("\n=== Overlap report generator ===")
    if obj_id is None or device_sn is None:
        obj_id, device_sn = get_report_metainfo()

    # Number of overlap-related warnings
    overlap_warn = 0

    # Is the overlap result within specification
    overlap_in_spec = True

    # Supported objectives
    supported_obj = ['nikon_pf_4x', 'nikon_pf_10x']
    if obj_id not in supported_obj:
        warn("Objective '" + obj_id + "' is not supported, not all beam size "
             "checks will be performed")
        overlap_warn += 1
        obj_ind = 0
    else:
        for ind, name in enumerate(supported_obj):
            if name == obj_id:
                obj_ind = ind + 1
                break

    # Expected pump and probe beam size ranges
    # Objective indices: unknown, Plan Fluor 4x, Plan Fluor 10x
    min_probe_focus_sz = [0.1, 7, 3][obj_ind]
    max_probe_focus_sz = [50, 12, 12][obj_ind]
    max_probe_sz = [500, 100, 100][obj_ind]
    min_probe_focus_z = [-2, -0.1, -0.1][obj_ind]
    max_probe_focus_z = [2, 0.1, 0.1][obj_ind]

    min_pump_focus_sz = [0.1, 5, 3][obj_ind]
    max_pump_focus_sz = [50, 25, 25][obj_ind]
    max_pump_sz = [500, 100, 100][obj_ind]
    min_pump_focus_z = [-2, -0.5, -0.5][obj_ind]
    max_pump_focus_z = [2, 0.5, 0.5][obj_ind]

    # Allowed pump-probe focus lateral mismatch
    max_pp_xy_r = [50, 5, 4][obj_ind]

    # Allowed pump-probe focal spot size ratio
    min_overlap_ratio = 1.4
    max_overlap_ratio = 2.1

    path = Path(path)
    path_pu = path / 'Pump'
    path_pr = path / 'Probe'

    if os.path.isdir(path):
        print(f"Working directory: {path}")
    else:
        raise RuntimeError(f"Invalid data directory '{path}'")

    try:
        print("Getting pump focus parameters...")
        [zarr_pu, ampl_pu, xypos_pu, width_pu] = \
            get_xyz_overlap_parameters(path=path_pu)
        par_pu = {'name': 'pump', 'zpos': zarr_pu, 'ampl': ampl_pu,
                  'xypos': xypos_pu, 'width': width_pu}
    except Exception as excpt:
        warn("Could not read pump data, pump metrics will be skipped. "
             f"Reason: {excpt.__cause__}")
        overlap_in_spec = False
        par_pu = None

    try:
        print("Getting probe focus parameters...")
        [zarr_pr, ampl_pr, xypos_pr, width_pr] = \
            get_xyz_overlap_parameters(path=path_pr)
        par_pr = {'name': 'probe', 'zpos': zarr_pr, 'ampl': ampl_pr,
                  'xypos': xypos_pr, 'width': width_pr}
    except Exception as excpt:
        warn("Could not read probe data, probe metrics will be skipped. "
             f"Reason: {excpt.__cause__}")
        overlap_in_spec = False
        par_pr = None

    # Make sure either pump or probe data is available
    if par_pu is None and par_pr is None:
        raise RuntimeError("Neither pump nor probe data is available")

    if par_pu is not None and par_pr is not None:
        len_pu = len(par_pu['zpos'])
        len_pr = len(par_pr['zpos'])
        if len_pu != len_pr:
            raise RuntimeError("The number of pump ({:d})".format(len_pu) +
                  " and probe ({:d}) imges is not equal".format(len_pr))
    elif par_pu is not None:
        num_pts = len(par_pu['zpos'])
    else:
        num_pts = len(par_pr['zpos'])

    par_pu = validate_profile_fit_results(par_pu)
    par_pr = validate_profile_fit_results(par_pr)

    if par_pr is not None:
        beam_sz_pr = np.sqrt(np.mean(par_pr['width']**2, 1))

        probe_focus_sz = np.min(beam_sz_pr)
        if probe_focus_sz < min_probe_focus_sz:
            print("WARNING: Probe focus size is too small " +
                  "(<{:.1f} µm)".format(min_probe_focus_sz))
            overlap_warn += 1
        if probe_focus_sz > max_probe_focus_sz:
            print("WARNING: Probe focus size is too large " +
                  "(>{:.0f} µm)".format(max_probe_focus_sz))
            overlap_warn += 1

        probe_sz_max = np.max(beam_sz_pr)
        if probe_sz_max > max_probe_sz:
            print("WARNING: Maximum probe beam size is too large " +
                  "(>{:.0f} µm)".format(max_probe_sz))
            overlap_warn += 1

        probe_focus_ind = np.argmin(beam_sz_pr)
        probe_focus_x = xypos_pr[probe_focus_ind, 0]
        probe_focus_y = xypos_pr[probe_focus_ind, 1]

        probe_focus_z = zarr_pr[probe_focus_ind]
        if probe_focus_z < min_probe_focus_z:
            print("WARNING: Probe focus Z position is too close " +
                  "(<{:.1f} mm)".format(min_probe_focus_z))
            overlap_warn += 1
        if probe_focus_z > max_probe_focus_z:
            print("WARNING: Probe focus Z position is too far " +
                  "(>{:.1f} mm)".format(max_probe_focus_z))
            overlap_warn += 1

        print("Probe focus size is {:.1f} µm FWHM at Z = {:.2f} mm".format(
            probe_focus_sz, probe_focus_z))

    if par_pu is not None:
        beam_sz_pu = np.sqrt(np.mean(width_pu**2, 1))

        pump_focus_sz = np.min(beam_sz_pu)
        if pump_focus_sz < min_pump_focus_sz:
            print("WARNING: Pump focus size is too small " +
                  "(<{:.1f} µm)".format(min_pump_focus_sz))
            overlap_warn += 1
        if pump_focus_sz > max_pump_focus_sz:
            print("WARNING: Pump focus size is too large " +
                  "(>{:.0f} µm)".format(max_pump_focus_sz))
            overlap_warn += 1
            overlap_in_spec = False

        pump_sz_max = np.max(beam_sz_pu)
        if pump_sz_max > max_pump_sz:
            print("WARNING: Maximum pump beam size is too large " +
                  "(>{:.0f} µm)".format(max_pump_sz))
            overlap_warn += 1

        pump_focus_ind = np.argmin(beam_sz_pu)
        pump_focus_x = xypos_pu[pump_focus_ind, 0]
        pump_focus_y = xypos_pu[pump_focus_ind, 1]

        pump_focus_z = zarr_pu[pump_focus_ind]
        if pump_focus_z < min_pump_focus_z:
            print("WARNING: Pump focus Z position is too close " +
                  "(<{:.1f} mm)".format(min_pump_focus_z))
            overlap_warn += 1
        if pump_focus_z > max_pump_focus_z:
            print("WARNING: Pump focus Z position is too far " +
                  "(>{:.1f} mm)".format(max_pump_focus_z))
            overlap_warn += 1

        print("Pump focus size is {:.1f} µm FWHM at Z = {:.2f} mm".format(
            pump_focus_sz, pump_focus_z))

    # Calculate XY position with respect to probe focus
    if xy_pos_rel_to_z0 and par_pr is not None:
        par_pr['xypos'][:, 0] = par_pr['xypos'][:, 0] - probe_focus_x
        par_pr['xypos'][:, 1] = par_pr['xypos'][:, 1] - probe_focus_y

        if par_pu is not None:
            par_pu['xypos'][:, 0] = par_pu['xypos'][:, 0] - probe_focus_x
            par_pu['xypos'][:, 1] = par_pu['xypos'][:, 1] - probe_focus_y
            pump_focus_x -= probe_focus_x
            pump_focus_y -= probe_focus_y

        probe_focus_x = 0
        probe_focus_y = 0

    if par_pr is not None and par_pu is not None:
        pp_xy_r = np.sqrt((pump_focus_x - probe_focus_x)**2 + (pump_focus_y - probe_focus_y)**2)
        print("XY distance between pump and probe is {:.1f} µm".format(pp_xy_r))
        if pp_xy_r > max_pp_xy_r:
            print("WARNING: XY distance between pump and probe focus is too large " +
                  "(>{:.1f} µm)".format(max_pp_xy_r))
            overlap_warn += 1
            overlap_in_spec = False

    focus_region_size = 0.5
    if fig_style == 'at_focus':
        focus_rng = [probe_focus_z - focus_region_size/2, probe_focus_z + focus_region_size/2]
        if par_pr is not None:
            zpos = par_pr['zpos']
            par_pr['ampl'] = cut_by_x_range(zpos, par_pr['ampl'], rng=focus_rng)[1]
            par_pr['xypos'] = cut_by_x_range(zpos, par_pr['xypos'], rng=focus_rng)[1]
            par_pr['zpos'], par_pr['width'] = cut_by_x_range(zpos, par_pr['width'], rng=focus_rng)
        if par_pu is not None:
            zpos = par_pu['zpos']
            par_pu['ampl'] = cut_by_x_range(zpos, par_pu['ampl'], rng=focus_rng)[1]
            par_pu['xypos'] = cut_by_x_range(zpos, par_pu['xypos'], rng=focus_rng)[1]
            par_pu['zpos'], par_pu['width'] = cut_by_x_range(zpos, par_pu['width'], rng=focus_rng)

    if par_pu is not None:
        [plot_xl1, plot_yl1, plot_zl1, plot_wl1] = calc_plot_limits(par_pu)

    if par_pr is not None:
        [plot_xl2, plot_yl2, plot_zl2, plot_wl2] = calc_plot_limits(par_pr)

    if par_pu is not None:
        max_ampl_pu = np.max(par_pu['ampl'])
        par_pu['ampl'] = par_pu['ampl']/max_ampl_pu

    if par_pr is not None:
        max_ampl_pr = np.max(par_pr['ampl'])
        par_pr['ampl'] = par_pr['ampl']/max_ampl_pr

    ampl_units = 'a.u.'

    if par_pu is not None and par_pr is not None:
        xlims = [plot_xl1, plot_xl2]
        ylims = [plot_yl1, plot_yl2]
        zlims = [plot_zl1, plot_zl2]
        wlims = [plot_wl1, plot_wl2]
    elif par_pu is not None:
        xlims = [plot_xl1]
        ylims = [plot_yl1]
        zlims = [plot_zl1]
        wlims = [plot_wl1]
    elif par_pr is not None:
        xlims = [plot_xl2]
        ylims = [plot_yl2]
        zlims = [plot_zl2]
        wlims = [plot_wl2]

    plot_xl = get_common_range(xlims, mode='bound', expand_frac=0.1)
    plot_yl = get_common_range(ylims, mode='bound', expand_frac=0.1)
    if isnone(plot_wl):
        plot_wl = [0, 75]
        print("WARNING: Setting width axis range " +
                    "from {:.0f} µm ".format(plot_wl[0]) +
                    "to {:.0f} µm".format(plot_wl[1]))

        #plot_wl = get_common_range(wlims, mode='bound', expand_frac=0.1)
    plot_zl = get_common_range(zlims, mode='bound')

    plt.figure(figsize=[10, 8])
    subplot_col = 1
    subplot_cols = 3
    z_ax = None
    showxlabel=True

    w_ax = plt.subplot(subplot_rows, subplot_cols, subplot_col+subplot_row*subplot_cols)
    subplot_col = subplot_col+1
    x_ax = plt.subplot(subplot_rows, subplot_cols, subplot_col+subplot_row*subplot_cols)
    subplot_col = subplot_col+1
    y_ax = plt.subplot(subplot_rows, subplot_cols, subplot_col+subplot_row*subplot_cols)
    subplot_col = subplot_col+1

    # pump, probe
    colors = [get_color('db'), get_color('dr')]
    fill_colors = [get_color('b'), get_color('r')]

    if par_pr is not None:
        [z_focus_pr, w_at_focus_pr, x_at_focus_pr, y_at_focus_pr] = plot_overlap_results(par_pr['zpos'], par_pr['ampl'], par_pr['xypos'], par_pr['width'], \
            fit_focus_curve=False, \
            z_axes=z_ax, w_axes=w_ax, x_axes=x_ax, y_axes=y_ax, xl=plot_xl, yl=plot_yl, zl=plot_zl, wl=plot_wl,
            color=colors[1], fill_color=fill_colors[1],
            with_titles=False, show_x_label=showxlabel, ampl_units=ampl_units, width_metric=width_metric)
    if par_pu is not None:
        [z_focus_pu, w_at_focus_pu, x_at_focus_pu, y_at_focus_pu] = plot_overlap_results(par_pu['zpos'], par_pu['ampl'], par_pu['xypos'], par_pu['width'], \
            ref_focus=z_focus_pr, show_focus_marker=False, z_axes=z_ax, w_axes=w_ax, x_axes=x_ax, y_axes=y_ax, xl=plot_xl, yl=plot_yl, zl=plot_zl, wl=plot_wl,
            color=colors[0], fill_color=fill_colors[0],
            with_titles=False, show_x_label=showxlabel, ampl_units=ampl_units, width_metric=width_metric)

    if par_pu is not None and par_pr is not None:
        overlap_ratio = w_at_focus_pu/w_at_focus_pr

        if overlap_ratio < min_overlap_ratio:
            print("WARNING: Overlap ratio is too small, increase pump focus size")
            overlap_warn += 1
            overlap_in_spec = False
        if overlap_ratio > max_overlap_ratio:
            print("WARNING: Overlap ratio is too large, decrease pump focus size")
            overlap_warn += 1
            overlap_in_spec = False

    plt.sca(w_ax)
    overlap_str = ''
    if par_pu is not None and par_pr is not None:
        overlap_str += 'Pu/Pr FWHM overlap {:.1f}\n'.format(overlap_ratio)
    if par_pu is not None:
        overlap_str += 'Pump: {:.1f} µm'.format(w_at_focus_pu)
    if par_pr is not None:
        overlap_str += ' Probe: {:.1f} µm'.format(w_at_focus_pr)
    if not par_pu is not None or not par_pr is not None:
        overlap_str += ' FHWM'
    plt.title(overlap_str)

    plt.sca(x_ax)
    xofs_str = ''
    if par_pu is not None and par_pr is not None:
        xofs_str += 'X offset {:.1f} µm\n'.format(x_at_focus_pr - x_at_focus_pu)
    if par_pu is not None:
        xofs_str += 'Pump at {:.1f} µm'.format(x_at_focus_pu)
    if par_pr is not None:
        xofs_str += ' Probe at {:.1f} µm'.format(x_at_focus_pr)
    plt.title(xofs_str)

    plt.sca(y_ax)
    yofs_str = ''
    if par_pu is not None and par_pr is not None:
        yofs_str += 'Y offset {:.1f} µm\n'.format(y_at_focus_pr - y_at_focus_pu)
    if par_pu is not None:
        yofs_str += 'Pump at {:.1f} µm'.format(y_at_focus_pu)
    if par_pr is not None:
        yofs_str += ' Probe at {:.1f} µm'.format(y_at_focus_pr)
    plt.title(yofs_str)

    if suptitle_str is None:
        suptitle_str = "Overlap report"

    if device_sn is not None:
        suptitle_str += ", " + device_sn

    if obj_ind is not None:
        objective_str = ['unspecified objective', 'Nikon Plan Fluor 4x/0.13', 'Nikon Plan Fluor 10x/0.3'][obj_ind]
        suptitle_str += ", " + objective_str

    if date_str is None:
        date_str = time.strftime("%Y-%m-%d %H:%M")

    suptitle_str += ", " + date_str

    if overlap_in_spec:
        suptitle_str += "\n"
        suptitle_str += "Overlap is in spec"
    else:
        suptitle_str += "\n"
        suptitle_str += "Overlap is NOT IN SPEC, number of overlap-related warnings: {:d}".format(overlap_warn)

    plt.suptitle(suptitle_str)

    plt.gcf().set_size_inches(17, 5*subplot_rows + 1)
    if fig_style == 'whole_range':
        fig_name = 'Overlap_whole.pdf'
    if fig_style == 'at_focus':
        fig_name = 'Overlap_focus.pdf'

    plt.gcf().tight_layout(pad=3)

    export_figure(path / fig_name)

    print("Generating GIFs...")
    if par_pu is not None:
        try:
            make_xy_profile_gif(path=path_pu)
        except Exception:
            print("WARNING: Could not generate pump overlap GIF. " + get_exception_info_str())

    if par_pr is not None:
        try:
            make_xy_profile_gif(path=path_pr)
        except Exception:
            print("WARNING: Could not generate probe overlap GIF. " + get_exception_info_str())

    print("Showing report figure")

    plt.show()
