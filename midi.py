import os
from mido import MidiFile, tempo2bpm
import const
import math

import mido

import const


class Midi:
    program = 10
    port = None

    def __init__(self):
        pass

    def open_port(self, portname):
        try:
           self.port = mido.open_output(portname)
        except:
           self.port = mido.open_output()

        self.port.send(mido.Message("program_change", program=self.program))

    def close_port(self):
        self.port.close()

    def set_program(self, program):
        self.program = program

    def play_note(self, note):
        self.port.send(mido.Message("note_on", note=note))

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

        for msg in mido.MidiFile(filename):
            if not msg.is_meta:
                if msg.type == "note_on":
                    track_index = record.NOTES.index(msg.note)
                    record.set_note(beat_index, track_index, True)
                if msg.time > 0:
                    beat_index += 1
            if beat_index >= const.BEAT_COUNT:
                break

    def import_from_mid_maniacs(self, record, filename, bpm):
        FPR_SEC_BETWEEN_BEATS = 0.25
        FPR_BPM = 60 / FPR_SEC_BETWEEN_BEATS
        offset = 12
        track_index = 0
        beat_index = 0
        total_time = 0
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
            # log(f"msg.time={msg.time} beat_index={beat_index} msg.type={msg.type}: ", True)

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
                # if note != msg.note + offset:
                #    log(f"note_on={msg.note+offset}>{note} ", True)
                # else:
                #    log(f"note_on={note} ", True)

                # resize partition
                diff_beat = (beat_index - record.beats_count) + 1
                for _ in range(diff_beat):
                    record.right_shift(beat_index)

                # find track and set note
                track_index = record.NOTES.index(note)
                record.set_note(beat_index, track_index, True)

        record.filename = os.path.splitext(filename)[0] + ".fpr"
        basename = os.path.basename(filename)
        record.title = os.path.splitext(basename)[0]
        record.comment = f"""Imported from
        {os.path.basename(filename)}
        ms_per_beat={ms_per_beat} bpm={bpm} ratio={speed_ratio}"""
