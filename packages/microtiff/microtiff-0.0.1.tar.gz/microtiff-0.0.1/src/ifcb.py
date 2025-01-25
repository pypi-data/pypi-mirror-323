#!/bin/python3

# Copyright 2024, A Baldwin
#
# This file is part of microtiff.
#
# microtiff is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# microtiff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with microtiff.  If not, see <http://www.gnu.org/licenses/>.

'''
ifcb.py

A converter for image data from the IFCB sensor
'''

import argparse
import os
import re
import csv
import struct
import json
from PIL import Image
from PIL.TiffImagePlugin import ImageFileDirectory_v2
import numpy as np

def header_file_to_dict(lines):
    o_dict = {}
    for line in lines:
        m = re.search("^([^:]+):\\s?", line)
        key = m.group(1)
        value = line[len(m.group(0)):]
        o_dict[key] = value.rstrip()
    return o_dict

def extract_ifcb_images(target, no_metadata = False):
    header_lines = ""
    with open(target + ".hdr") as f:
        header_lines = f.readlines()
    metadata = header_file_to_dict(header_lines)

    adc_format_map = list(csv.reader([metadata["ADCFileFormat"]], skipinitialspace=True))[0]
    image_map = []
    outputs = []
    with open(target + ".adc") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=adc_format_map, skipinitialspace=True)
        with open(target + ".roi", "rb") as imagefile:
            for row in reader:
                #print(row)
                imagefile.seek(int(row["start_byte"]))
                height = int(row["ROIheight"])
                width = int(row["ROIwidth"])
                imdata = imagefile.read(height * width)
                if (height * width > 0):
                    imdata_reform = np.reshape(np.frombuffer(imdata, dtype=np.uint8), (height, width))
                    image = Image.fromarray(imdata_reform, "L")
                    image_package = {"metadata": row, "image": image}
                    image_map.append(image_package)
                    im_metadata = {}
                    for col_key in row:
                        sanitised_col_key = re.sub(r"[^A-Za-z0-9_-]", "", col_key)
                        #print(sanitised_col_key)
                        #print(row[col_key])
                        im_metadata[sanitised_col_key] = row[col_key]
                    trigger_number = str(row["trigger#"])
                    if not no_metadata:
                        with open(target + "_TN" + trigger_number + ".json", "w") as f:
                            json.dump(im_metadata, f, ensure_ascii=False)
                    image.save(target + "_TN" + trigger_number + ".tiff", "TIFF")
                    outputs.append(target + "_TN" + trigger_number)
    return outputs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--exclude-metadata", action="store_true", required=False, help="don't add metadata to resulting image files.")
    parser.add_argument("file", nargs='+', help="any number of .adc, .hdr or .roi files")

    args = parser.parse_args()

    in_files = args.file
    targets = []

    for in_file in in_files:
        in_file_s = os.path.splitext(in_file)
        if in_file_s[1] == ".adc" or in_file_s[1] == ".hdr" or in_file_s[1] == ".roi":
            targets.append(in_file_s[0])
        else:
            print("invalid extension \"" + in_file_s[1][1:] + "\" in file \"" + in_file + "\", ignoring")

    # Get rid of duplicates
    targets = list(set(targets))

    for target in targets:
        extract_ifcb_images(target, no_metadata = args.exclude_metadata)

