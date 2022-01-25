import os

import mido
from mido import MidiFile

import const

class Midi: 
    program = 10
    portname = None
    port = None

    def __init__(self, program, portname):
        self.program = program
        self.portname = portname

        try:
            self.port = mido.open_output(self.portname)
        except:
            self.port = mido.open_output()

        self.port.send(mido.Message("program_change", program=self.program))


    def export_to_mid(self, record):
        ticks = 480
        mid = mido.MidiFile(type=0, ticks_per_beat=ticks)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        track.append(mido.Message("program_change", program=self.program, time=0))

        for beat_index in range(record.beats_count):
            for track_index in range(record.tracks_count):
                if record.has_note(beat_index, track_index):
                    track.append(
                        mido.Message("note_on", note=record.NOTES[track_index], time=0)
                    )
            track.append(mido.Message("note_off", time=ticks))

        mid.save(record.title + ".mid")


    def import_from_mid(self, record, filename):
        record.filename = os.path.splitext(filename)[0] + ".fpr"
        record.title = os.path.basename(filename)
        record.comment = "Imported from " + os.path.basename(filename)

        beat_index = 0
        track_index = 0

        for msg in MidiFile(filename):
            if not msg.is_meta:
                if msg.type == "note_on":
                    track_index = record.NOTES.index(msg.note)
                    record.set_note(beat_index, track_index, True)
                if msg.time > 0:
                    beat_index += 1
            if beat_index >= const.BEAT_COUNT:
                break
