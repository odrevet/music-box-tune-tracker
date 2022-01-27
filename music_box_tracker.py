#!/usr/bin/env python3

import sys
import argparse
import curses

try:
    import mido
except ImportError:
    pass

try:
    import rtmidi
except ImportError:
    pass

try:
    from playsound import playsound
except ImportError:
    pass

try:
    from midi import Midi
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
        parser.add_argument(
            "--mid", help="import from .mid file created with music box tune tracker"
        )
        parser.add_argument(
            "--maniacs",
            help="import from .mid file exported from musicboxmaniacs.com for Kikkerland 15",
        )
        parser.add_argument(
            "--bpm",
            help="bpm for maniacs midi import",
        )


        if "rtmidi" in sys.modules:
            parser.add_argument("--port", help="name of the midi port to use")
            parser.add_argument("--program", help="midi instrument code")


    args = parser.parse_args()
    if args.fpr:
        record.filename = args.fpr
    if args.title:
        record.title = args.title

    if args.audio == "wav" and "playsound" not in sys.modules:
        sys.exit("Wav audio backend selected but playsound package not found. ")

    if args.audio == "midi" and ("mido" not in sys.modules or "rtmidi" not in sys.modules):
        sys.exit("Midi audio backend selected but mido and rtmidi packages not found. ")

    midi = None
    if "mido" in sys.modules:
        midi = Midi()

        if args.audio == "midi" and "rtmidi" in sys.modules:
            program = 10
            portname = ""
            if args.program:
                program = int(args.program)
            if args.port:
                portname = args.port
            midi.open_port(portname)
            midi.set_program(program)

    if record.filename:
        record.load()
    elif "mido" in sys.modules:
        if args.mid is not None:
            midi.import_from_mid(record, args.mid)
        elif args.maniacs is not None:
            bpm = None
            if args.bpm:
                bpm = int(args.bpm)

            midi.import_from_mid_maniacs(record, args.maniacs, bpm)
    else:
        record.filename = record.title + ".fpr"

    display = CursesDisplay(record)
    if args.low:
        display.tone_descending = False

    try:
        curses.wrapper(run_curses, display, midi, args.audio)
        if args.audio == "midi" and "rtmidi" in sys.modules:
            midi.close_port()
    except curses.error:
        sys.exit("Error when drawing to terminal (terminal too small ? )")
