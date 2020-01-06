#!/usr/bin/env python3

import sys
import argparse
import os
from mido import MidiFile
from document import Document

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
parser.add_argument('--mid',    help='file to import. .mid from musicboxmaniacs.com Kikkerland 15')
parser.add_argument('--fpr',    help='fpr file to write')
#parser.add_argument('--start',    help='start import after start in beats')
#parser.add_argument('--nolimit',    help='ignore Fisher Price Record beat limit')
#parser.add_argument('--limit',    help='stop import after limit in beats')

args=parser.parse_args()
filename = args.mid

document = Document(86, 16)
limit = 86
offset = 12

track_index=0
beat_index=0

for msg in MidiFile(filename):
    if not msg.is_meta:
        if msg.type == 'note_on':
            note = msg.note + offset
            if note == 77:
                note = 76

            track_index = document.NOTES.index(note)
            document.set_note(beat_index, track_index, True)

        if msg.time > 0 :
            beat_index += 1

    if beat_index >= limit:
        break

if args.fpr:
    document.filename = args.fpr
else:
    document.filename = os.path.splitext(filename)[0]+'.fpr'

basename = os.path.basename(filename)
document.title = os.path.splitext(basename)[0]
document.comment = 'Imported from ' + os.path.basename(filename)

document.save()

print('fpr saved to ' + document.filename)
