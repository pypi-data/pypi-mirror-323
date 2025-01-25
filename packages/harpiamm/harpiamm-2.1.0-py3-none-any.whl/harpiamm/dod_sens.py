"""HARPIA Microscopy Module Python library.

This module contains functions for testing pump-probe measurement sensitivity
in terms of the minimum resolvable differential optical density (ΔOD or DOD).
These functions were developed as part of the HARPIA Microscopy Module white
light supercontinuum prboe characterization when it is tightly focused using a
microscope objective.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2023 Light Conversion
All rights reserved.
www.lightcon.com
"""
import json

import matplotlib.pyplot as plt
import numpy as np

from lkcom.plot import add_y_marker
from lkcom.util import find_closest


def plot_dod_hist(
        dod_arr=None, wavl=None, wavl_rng=None,
        show_labels=False, show_title=True, ylim=None,
        show_mod_units_in_legend=False, log_hist=True,
        hist_range=[-2, 2]):
    """Plot a DOD histogram."""
    cut_ind = find_closest(wavl, wavl_rng)
    hist_data = np.array(dod_arr)[:, cut_ind[0]:cut_ind[1]].flatten()*1E3
    plt.hist(hist_data, bins=64, range=hist_range, log=log_hist)
    plt.grid()

    plt.xlim(hist_range)
    plt.ylim(ylim)

    if log_hist:
        y_pos_ofs_fac = 0.50
    else:
        y_pos_ofs_fac = 0.10

    xlim = plt.xlim()
    ylim = plt.ylim()
    xpos = xlim[1] - 0.05*(xlim[1]-xlim[0])
    ypos = ylim[1] - y_pos_ofs_fac*(ylim[1]-ylim[0])

    wavl_rng_str = "{:.0f} – {:.0f} nm".format(wavl_rng[0], wavl_rng[1])

    info_str = ''
    if not show_title:
        info_str = wavl_rng_str + '\n'

    if show_mod_units_in_legend:
        unit_str = 'mOD'
    else:
        unit_str = ''

    info_str += \
        'q_50: {:.3f} {:s}\n'.format(
            np.percentile(hist_data, 75) - np.percentile(hist_data, 25),
            unit_str) + \
        'q_90: {:.3f} {:s}'.format(
            np.percentile(hist_data, 95) - np.percentile(hist_data, 5),
            unit_str)

    plt.text(
        xpos, ypos, info_str, ha='right', va='top',
        bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.75})

    if show_title:
        plt.title(wavl_rng_str)

    if show_labels:
        plt.xlabel('Sen1sitivity, mOD')
        plt.ylabel('Counts')


def make_dod_sens_hist_fig(data_dir='./'):
    """Make a DOD sensitivity figure with histograms.

    Make a figure showing DOD sensitivity which contains two panels:
        1) Sample probe spectrum and DOD spectra at different ideal chop rates
        2) DOD histograms at a single chop rate split into wavelength bins
    """
    # === Load configuration ===
    config = json.load(open(data_dir + 'config.xml'))
    timestamp_str = config.get('timestamp_str')
    title_str = config.get('title_str', 'WLSC stability')
    num_acq_spectra = config.get('num_acq_spectra')
    num_spec_px = config.get('num_spec_px', 256)
    spectrum_time = config.get('spectrum_time')

    chop_bins = config.get('chop_bins', [1, 5, 10, 20])

    dod_wavl_arr = config.get(
        'dod_wavl_arr',
        [[510, 600], [600, 700], [700, 800], [800, 900]])

    wavl = np.loadtxt(data_dir + 'wavl.dat')
    spec = np.loadtxt(data_dir + 'spec.dat')
    dod_arr = np.loadtxt(data_dir + 'dod_arr.dat')*1E-3

    # === Parse data ===
    if timestamp_str is not None:
        title_str += ', ' + timestamp_str

    pump_spec = np.ndarray([int(num_acq_spectra/2), num_spec_px])
    unpump_spec = np.ndarray([int(num_acq_spectra/2), num_spec_px])

    legend_str = []
    for chop_bin in chop_bins:
        legend_str.append("{:.0f} Hz".format(np.round(1/(spectrum_time*chop_bin))))

    fig = plt.figure(figsize=[10, 3.5])
    gs = fig.add_gridspec(4, 2)
    ax_dod_spec_at_chop = plt.subplot(gs[:, 0])

    # === DOD spectra at several chop rates ===
    #
    # Ideal chopping is when the acquired spectra are sliced into blocks of N
    # spectra, i.e. the slices are always of the same size and there are no
    # pumped/unpumped spectra uncertainty.
    plt.subplot(ax_dod_spec_at_chop)
    plt.cla()
    chop_freq = 1/(np.array(chop_bins)*spectrum_time*2)
    legend_str = []
    for ind_chop, chop_bin in enumerate(chop_bins):
        for ind in np.arange(0, num_acq_spectra, chop_bin*2):
            hind = int(ind/2)
            pump_spec[hind:hind+chop_bin, :] = spec[ind:ind+chop_bin, :]
            unpump_spec[hind:hind+chop_bin, :] = spec[ind+chop_bin:ind+2*chop_bin, :]

        dod = np.log10(np.mean(unpump_spec, 0)/np.mean(pump_spec, 0))

        plt.plot(wavl, dod*1E3)
        legend_str.append("{:.0f} Hz".format(chop_freq[ind_chop]))

    avg_probe = np.mean(spec, 0)
    avg_probe = 4*(avg_probe/10 - 0.5)
    plt.plot(wavl, avg_probe, '-k')

    plt.ylim(-2, 2)
    plt.xlim([wavl[0], wavl[-1]])
    plt.grid('on')

    add_y_marker(0)

    plt.ylabel('mOD')
    plt.xlabel('Wavelength, nm')
    plt.title('Probe and sample DOD spectra')
    plt.legend(legend_str)

    # === DOD stability histograms ===
    for ind, wavl_rng in enumerate(dod_wavl_arr):
        plt.subplot(gs[ind, 1])
        plt.cla()
        plot_dod_hist(dod_arr, wavl, dod_wavl_arr[ind], ylim=[1, 2000],
                      show_title=False)

        plt.grid('on', which='both', axis='y')
        plt.gca().set_yticklabels([])
        if ind != len(dod_wavl_arr) - 1:
            plt.gca().set_xticklabels([])
        if ind == 0:
            plt.title('DOD histograms (log)')

    plt.xlabel('mOD')

    gs.update(hspace=0)
    plt.tight_layout()
    plt.draw()
    plt.pause(0.001)

    plt.tight_layout()
    # plt.suptitle(title_str)
    plt.savefig(timestamp_str + '-dod_hist.png')

    plt.draw()
    plt.pause(0.001)

    # Print percentile ranges
    print("Percentile ranges: ")
    for ind, wavl_rng in enumerate(dod_wavl_arr):
        cut_ind = find_closest(wavl, wavl_rng)
        hist_data = np.array(dod_arr)[:, cut_ind[0]:cut_ind[1]].flatten()*1E3
        q_50_str = "{:.3f}".format(
            np.percentile(hist_data, 75) - np.percentile(hist_data, 25))
        q_90_str = "{:.3f}".format(
            np.percentile(hist_data, 95) - np.percentile(hist_data, 5))
        print(q_50_str + ', ', q_90_str + ',  ', end='')
    print('\n')

    print("Close figure to exit")
    plt.show()
