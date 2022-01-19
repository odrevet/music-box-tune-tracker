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

# Missing notes
# As the Fisher Price Record Player does not have all semi-tones, we search the available
# note range for nearest tone (yes, this will sound bad!)

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
parser.add_argument(
    "--verbose",
    help="show MIDI message information during conversion",
    action="store_true",
)

args = parser.parse_args()
filename = args.mid

def log(msg, nonl=False):
    if args.verbose:
        print(msg, end='' if nonl else '\n')

record = Record(0, const.TRACK_COUNT)
offset = 12
track_index = 0
beat_index = 0
total_time = 0
bpm = float(args.bpm) if args.bpm else None
speed_ratio = 1
if bpm is not None:
    speed_ratio = bpm / FPR_BPM
    log(f"bpm={bpm} ratio={speed_ratio}")

for msg in MidiFile(filename):

    if msg.type == "set_tempo":
        if bpm is not None:
            continue

        ms_per_beat = msg.tempo
        bpm = tempo2bpm(ms_per_beat)
        speed_ratio = bpm / FPR_BPM
        log(f"ms_per_beat={ms_per_beat} bpm={bpm} ratio={speed_ratio}")

        continue

    if msg.is_meta:
        continue

    total_time += msg.time
    beat_index = math.ceil(total_time / speed_ratio)
    log(f"msg.time={msg.time} beat_index={beat_index} msg.type={msg.type}: ", True)

    if msg.type == "note_on":
        note = msg.note + offset
        nabv = note
        nbel = note
        # search for suitable higher/lower note if we don't have the one specified..
        while not note in record.NOTES:
            nabv += 1
            nbel -= 1
            # prefer higher notes than lower?
            if nabv in record.NOTES:
                note = nabv
                break
            elif nbel in record.NOTES:
                note = nbel
                break
        if note != msg.note + offset:
            log(f"note_on={msg.note+offset}>{note} ", True)
        else:
            log(f"note_on={note} ", True)

        # resize partition
        diff_beat = (beat_index - record.beats_count) + 1
        for _ in range(diff_beat):
            record.right_shift(beat_index)

        # find track and set note
        track_index = record.NOTES.index(note)
        record.set_note(beat_index, track_index, True)

    log("")

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
