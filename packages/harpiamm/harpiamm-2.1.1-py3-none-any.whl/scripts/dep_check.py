#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA-MM Python library dependency checker.

Programmatically check whether the dependencies required to run harpiamm
scripts are satisfied. This is particularly useful when running scripts from
the LC Launcher App and for the FLIR spinnaker-python/PySpin library which is
not available from PyPi.

This script is a part of the HARPIA Microscopy Kit, which is a set of tools for
the alignment, characterization and troubleshooting of HARPIA-MM Microscopy
Extension.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2024 Light Conversion
All rights reserved.
www.lightcon.com
"""
from packaging import version
from importlib import import_module, metadata
from pathlib import Path
import json
import os
import requests

import subprocess
import sys

def install(package_name, min_ver=None, custom_url=None):
    if custom_url is not None:
        package_str = custom_url
    else:
        package_str = package_name
        if min_ver is not None:
            package_str += '>=' + min_ver.public
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_str])

def check_dependency(package_name, min_ver, import_name=None, custom_url=None):
    if import_name is None:
        import_name = package_name

    try:
        package = import_module(import_name)
    except ModuleNotFoundError:
        print(f"Package {package_name} not found")
        package = None
    min_ver = version.parse(min_ver)
    if package is None or version.parse(metadata.version(package_name)) < min_ver:
        print(f"This script requires {package_name} {min_ver} or newer")
        print(f"Installing...")
        install(package_name, min_ver, custom_url=custom_url)

        package = import_module(import_name)
        if version.parse(metadata.version(package_name)) < min_ver:
            raise RuntimeError(f"This example requires {package.__name__} {min_ver}, but it was not found and could not be installed automatically")

    print("Dependency check completed")

def check_applet(package_name):
    manifest_path = Path("../manifest.json")
    if Path(manifest_path).is_file():
        manifest_json = json.load(open(manifest_path))
        current_version = version.parse(manifest_json.get('version'))
        response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
        latest_version = version.parse(response.json()['info']['version'])
    else:
        print("Cannot locate manifest.json, applet version will not be checked")
        return

    if current_version == latest_version:
        print("Applet version is current")
    elif current_version > latest_version:
        raise RuntimeError("Applet version is greater than repo, this should not happen")
    else:
        print("UPDATE NEEDED: There is a newer version of this applet.")

def harpiamm_dep_check():
    check_dependency("spinnaker-python", "4.0.0.0", import_name="PySpin", custom_url="//konversija/kleja/TOPAS/SOFTWARE/FLIR/spinnaker_python-4.0.0.116-cp38-cp38-win_amd64.whl")
    check_dependency("harpiamm", "2.0.3")
    check_applet("harpiamm")

if __name__ == "__main__":
    harpiamm_dep_check()
