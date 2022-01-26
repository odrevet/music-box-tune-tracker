#!/usr/bin/env python3

import sys
import argparse
import curses

try:
    import mido
    import rtmidi
    from midi import Midi
except ImportError:
    pass

try:
    from playsound import playsound
except ImportError:
    pass

import const
from record import Record
from ui_curses.display import CursesDisplay
from ui_curses.control import run_curses

if __name__ == "__main__":
    record = Record(0, const.TRACK_COUNT)
    parser = argparse.ArgumentParser()

    # General arguments
    parser.add_argument("--fpr", help=".fpr file to open")
    parser.add_argument("--title", help="set the title of a new tune")
    parser.add_argument(
        "--low", help="display low pitch notes first", action="store_true"
    )
    parser.add_argument(
        "--audio",
        choices=["wav", "midi"],
        help="use wav or midi as audio backend",
    )
    parser.set_defaults(audio="wav")

    # Midi related arguments
    if "mido" in sys.modules:
        parser.add_argument("--port", help="name of the midi port to use")
        parser.add_argument("--program", help="midi instrument code")
        parser.add_argument(
            "--mid", help="import from .mid file created with music box tune tracker"
        )

    args = parser.parse_args()
    if args.fpr:
        record.filename = args.fpr
    if args.title:
        record.title = args.title

    if args.audio == "wav" and "playsound" not in sys.modules:
        sys.exit("Wav backend selected but playsound package not found. ")

    midi = None
    if "mido" in sys.modules and "rtmidi" in sys.modules:
        program = 10
        portname = ""
        if args.program:
            program = int(args.program)
        if args.port:
            portname = args.port

        midi = Midi(program, portname)

    if record.filename:
        record.load()
    elif "mido" in sys.modules and args.mid is not None:
        midi.import_from_mid(record, args.mid)
    else:
        record.filename = record.title + ".fpr"

    input = CursesDisplay(record)
    if args.low:
        input.tone_descending = False

    try:
        curses.wrapper(run_curses, input, midi, args.audio)
    except curses.error:
        sys.exit("Error when drawing to terminal (is the terminal too small ? )")
