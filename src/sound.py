#!/usr/bin/env python3

import sys
import threading
import time

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

from record import Record

def play_note(note, audio, midi=None):
    if audio == "midi" and "mido" in sys.modules:
        midi.play_note(note)
    elif audio == "wav" and "playsound" in sys.modules:
        threading.Thread(
            target=playsound, args=(f"res/wav/{note}.wav",), daemon=True
        ).start()


def play(audio, midi, record, start_at, on_note_callback):
    t = threading.currentThread()
    FPR_SEC_BETWEEN_BEATS = 0.5

    for beat_index in range(start_at, record.beats_count):
        if getattr(t, "do_run", True) == False:
            return

        for tone_index in range(Record.TONES_COUNT):
            if record.has_note(beat_index, tone_index):
                play_note(record.NOTES[tone_index], audio, midi)
        time.sleep(FPR_SEC_BETWEEN_BEATS)

        on_note_callback(beat_index)
