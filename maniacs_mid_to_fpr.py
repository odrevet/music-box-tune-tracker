#!/usr/bin/env python3

import sys
import argparse
import os
from mido import MidiFile, tempo2bpm
from record import Record
import const
import math

# About
# Convert .mid file from https://musicboxmaniacs.com to a .fpr file
# The .mid from music box maniacs must be for a song designed for the
# 'Kikkerland 15' music box

# Missing F note
# As the Fisher Price Record Player does not have a F# tone (midi note 77), it is replace
# with a G

# Tone
# The 'Kikkerland 15' is a musical stave below the Fisher Price Record Player, so all the
# note have an offset of 12 midi tone

# Limitations
# To fit on a Fisher Price Record, the conversion will only convert the first 86 beats.
# This converter do not check tempo, when a midi message has a time above zero, it move to
# the next beat

FPR_SEC_BETWEEN_BEATS = 0.25
FPR_BPM = 60 / FPR_SEC_BETWEEN_BEATS

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mid",
    help="mid file to import from musicboxmaniacs.com (Kikkerland 15 only)",
    required=True,
)
parser.add_argument(
    "--fpr",
    help="fpr file to write. When not present, the output file will have the same name as the mid input but with .frp extension",
)
parser.add_argument(
    "--bpm",
    help="set bpm of mid file. When not present, the bmp will be read from the mid file",
)
parser.add_argument(
    "--stdout",
    help="do not save output to a file but print to stdout instead",
    action="store_true",
)

args = parser.parse_args()
filename = args.mid

record = Record(0, const.TRACK_COUNT)
offset = 12
track_index = 0
beat_index = 0
total_time = 0
bpm = float(args.bpm) if args.bpm else None
speed_ratio = 1
if bpm is not None:
    speed_ratio = bpm / FPR_BPM

for msg in MidiFile(filename):
    if msg.type == "set_tempo":
        if bpm is not None:
            continue

        ms_per_beat = msg.tempo
        bpm = tempo2bpm(ms_per_beat)
        speed_ratio = bpm / FPR_BPM

        continue

    if msg.is_meta:
        continue

    total_time += msg.time
    beat_index = math.ceil(total_time / speed_ratio)

    if msg.type == "note_on":
        note = msg.note + offset
        if note == 77:
            note = 76

        # resize partition
        diff_beat = (beat_index - record.beats_count) + 1
        for _ in range(diff_beat):
            record.right_shift(beat_index)

        # find track and set note
        track_index = record.NOTES.index(note)
        record.set_note(beat_index, track_index, True)

if args.fpr:
    record.filename = args.fpr
else:
    record.filename = os.path.splitext(filename)[0] + ".fpr"

basename = os.path.basename(filename)
record.title = os.path.splitext(basename)[0]
record.comment = """Imported from
{}
with a bpm of {}""".format(
    os.path.basename(filename), bpm
)

if args.stdout:
    sys.stdout.write(record.to_fpr())
else:
    record.save()
    print("fpr saved to " + record.filename)
