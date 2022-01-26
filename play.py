#!/usr/bin/env python3

import sys
import threading

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

def play_note(note, audio, midi=None):
    if audio == "midi" and "mido" in sys.modules:
        midi.play_note(note)
    elif audio == "wav" and "playsound" in sys.modules:
        threading.Thread(
            target=playsound, args=(f"wav/{note}.wav",), daemon=True
        ).start()