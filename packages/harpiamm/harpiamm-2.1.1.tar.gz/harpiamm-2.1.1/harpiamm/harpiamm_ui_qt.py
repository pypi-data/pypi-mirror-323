#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HARPIA Microscopy Module Python library.

Contact: lukas.kontenis@lightcon.com, support@lightcon.com

Copyright (c) 2019-2021 Light Conversion
All rights reserved.
www.lightcon.com
"""
import sys

from PySide2.QtWidgets import QApplication, QDialog, QPushButton, QLineEdit, \
    QFormLayout, QComboBox

class ReportMetainfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        e1 = QLineEdit()
        e1.setInputMask("M99999")
        self.sn = e1

        cb = QComboBox()
        cb.addItem("Undefined")
        cb.addItem("Nikon Plan Fluor 4x")
        cb.addItem("Nikon Plan Fluor 10x")
        cb.setCurrentIndex(1)
        self.cb = cb

        button = QPushButton("OK")
        button.clicked.connect(self.ok_press)

        flo = QFormLayout()
        flo.addRow("HARPIA SN", e1)
        flo.addRow("Objective", cb)

        flo.addRow(button)
        self.setLayout(flo)
        self.setWindowTitle("Report Metainfo")

    def ok_press(self):
        device_sn = self.sn.text()
        if len(device_sn) < 6:
            print("Please enter a valid HARPIA serial number in the M00000 "
                  "format")
        else:
            self.close()


def get_report_metainfo_qt():
    app = QApplication(sys.argv)
    win = ReportMetainfoDialog()
    win.exec_()
    device_sn = win.sn.text()
    obj_ids = ['undef', 'nikon_pf_4x', 'nikon_pf_10x']
    obj_ind = win.cb.currentIndex()
    if obj_ind == 0:
        print("WARNING: Undefined objective selected, some overlap "
              "characterization features will not work")
    obj_id = obj_ids[obj_ind]

    return [obj_id, device_sn]


if __name__ == '__main__':
    print(get_report_metainfo_qt())
