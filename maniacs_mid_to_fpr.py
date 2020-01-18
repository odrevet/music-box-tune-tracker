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

FPR_SEC_BETWEEN_BEATS = 0.4
FPR_TEMPO = 60 / FPR_SEC_BETWEEN_BEATS

parser=argparse.ArgumentParser()
parser.add_argument('--mid',    help='mid file to import from musicboxmaniacs.com (Kikkerland 15 only)')
parser.add_argument('--fpr',    help='fpr file to write')
parser.add_argument('--bmp',    help='set bmp of mid file')
parser.add_argument('--stdout', help='do not save output to a file but print to stdout instead', action='store_true')

args=parser.parse_args()
filename = args.mid

record = Record(const.BEAT_COUNT, const.TRACK_COUNT)
limit = const.BEAT_COUNT  #will stop import when beat count reaches limit
offset = 12
track_index = 0
beat_index = 0
total_time = 0
bmp = float(args.bmp) if args.bmp else None
speed_ratio=1
if bmp is not None:
    speed_ratio = bmp / FPR_TEMPO

for msg in MidiFile(filename):
    if msg.type == 'set_tempo':
        if bmp is not None:
            continue

        ms_per_beat = msg.tempo
        bmp = tempo2bpm(ms_per_beat)
        speed_ratio = bmp / FPR_TEMPO

        continue

    if  msg.is_meta:
       continue

    total_time += msg.time
    beat_index = math.ceil(total_time / speed_ratio)

    if beat_index >= limit:
        break

    if msg.type == 'note_on':
        note = msg.note + offset
        if note == 77:
            note = 76

        track_index = record.NOTES.index(note)
        record.set_note(beat_index, track_index, True)

if args.fpr:
    record.filename = args.fpr
else:
    record.filename = os.path.splitext(filename)[0]+'.fpr'

basename = os.path.basename(filename)
record.title = os.path.splitext(basename)[0]
record.comment = 'Imported from ' + os.path.basename(filename)

if args.stdout:
    sys.stdout.write(record.to_fpr())
else:
    record.save()
    print('fpr saved to ' + record.filename)
