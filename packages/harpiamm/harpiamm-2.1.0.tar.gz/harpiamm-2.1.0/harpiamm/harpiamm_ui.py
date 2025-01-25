#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA Microscopy Module Python library.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2023 Light Conversion
All rights reserved.
www.lightcon.com
"""
from harpiamm.harpiamm_ui_cli import get_report_metainfo_cli

UI_BACKEND = 'cli'  # 'qt' or 'cli'

if UI_BACKEND == 'qt':
    from harpiamm.harpiamm_ui_qt import get_report_metainfo_qt
elif UI_BACKEND == 'cli':
    from harpiamm.harpiamm_ui_cli import get_report_metainfo_cli


def get_report_metainfo():
    """Ask user for HARPIA SN and objective ID using text CLI or Qt GUI."""
    if UI_BACKEND == 'qt':
        return get_report_metainfo_qt()
    if UI_BACKEND == 'cli':
        return get_report_metainfo_cli()


if __name__ == '__main__':
    print(get_report_metainfo())
