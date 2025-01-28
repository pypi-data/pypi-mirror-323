#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA Microscopy Module Python library.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2023 Light Conversion
All rights reserved.
www.lightcon.com
"""
def get_report_metainfo_cli():
    """Ask user for HARPIA SN and objective ID using text CLI."""
    while 1:
        prompt = "HARPIA SN: "
        ans = input(prompt).upper()

        if len(ans) == 0 or ans[0] != 'M' or len(ans) != 6:
            print("Serial number must be in the 'M12345' format")
        else:
            device_sn = ans
            break

    while 1:
        prompt = "Objective used (4x/10x): "
        ans = input(prompt).lower()

        valid_input = {'4x': 'nikon_pf_4x',
                       '10x': 'nikon_pf_10x' }

        if ans in valid_input.keys():
            obj_id = valid_input[ans]
            break
        else:
            print("Please enter either '4x' or '10x'")

    return [obj_id, device_sn]


if __name__ == '__main__':
    print(get_report_metainfo_cli())
