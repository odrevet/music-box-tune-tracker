#!/usr/bin/env python3
import os
import sys
import argparse
import datetime
from pathlib import Path
import scad

from record import Record

parser = argparse.ArgumentParser()
parser.add_argument("--fpr", help="name of fpr file", required=True)
parser.add_argument("--fprverso", help="name of fpr file for second side")
parser.add_argument("--scad", help="name of scad file to output")
parser.add_argument(
    "--thickness", help="thickness in mm. Defaults to 3 if one side or 5 if two sides"
)

args = parser.parse_args()

fpr_file = args.fpr
fpr_file_verso = args.fprverso
scad_file = args.scad or os.path.splitext(fpr_file)[0] + ".scad"
thickness = None
if args.thickness:
    thickness = float(args.thickness)
else:
    thickness = 5 if fpr_file_verso else 3

if not Path(fpr_file).is_file():
    print("Cannot find " + fpr_file)
    sys.exit()

record = Record(0)
record.filename = fpr_file
record.load()
record.resize_beats(Record.MAX_BEAT)

record_verso = None
if fpr_file_verso is not None:
    if not Path(fpr_file_verso).is_file():
        print("Cannot find " + fpr_file_verso)
        sys.exit()

    record_verso = Record(0)
    record_verso.filename = fpr_file_verso
    record_verso.load()
    record_verso.resize_beats(Record.MAX_BEAT)


VERSION = "1.0"
date_time = datetime.datetime.now().strftime("%d %b %Y %H:%M")
has_second_side = fpr_file_verso is None

scad_output = scad.to_scad(VERSION, date_time, thickness, record, record_verso)
myfile = open(scad_file, "w")
myfile.write(scad_output)
myfile.close()
