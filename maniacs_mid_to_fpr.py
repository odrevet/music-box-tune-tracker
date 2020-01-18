#!/usr/bin/env python3

import sys
import argparse
import os
from mido import MidiFile
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

parser=argparse.ArgumentParser()
parser.add_argument('--mid',      help='mid file to import from musicboxmaniacs.com (Kikkerland 15 only)')
parser.add_argument('--fpr',      help='fpr file to write')
parser.add_argument('--speed-ratio', help='speed ratio (defaults to 0.4)')

args=parser.parse_args()
filename = args.mid

record = Record(const.BEAT_COUNT, const.TRACK_COUNT)
limit = const.BEAT_COUNT  #will stop import when beat count reaches limit
offset = 12
track_index = 0
beat_index = 0
total_time = 0
speed_ratio = float(args.speed_ratio) if args.speed_ratio else 0.4

for msg in MidiFile(filename):
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

record.save()

print('fpr saved to ' + record.filename)
