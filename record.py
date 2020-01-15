import os
import mido
from mido import MidiFile
import const

class Record:
    # what the .fpr format uses
    __NOTE_FPR = '+'
    __EMPTY_FPR = '-'

    filename = None
    title = 'Default'
    comment = ''
    _partition = None  #list of lists of boolean: [track][beat] True indicates a note
    tracks_count = 0
    beats_count = 0
    program = 8
    NOTES = [67, 72, 74, 76, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98]

    def __init__(self, beats_count, tracks_count):
        self._partition = [[False for x in range(beats_count)]
                          for y in range(tracks_count)]
        self.beats_count = beats_count
        self.tracks_count = tracks_count

    def has_note(self, beat_index, track_index):
        return self._partition[track_index][beat_index]

    def set_note(self, beat_index, track_index, value):
        self._partition[track_index][beat_index] = value

    def get_track(self, track_index):
        return self._partition[track_index]

    def get_beats(self, beat_index):
        return [track_index[beat_index] for track_index in self._partition]

    def reverse_note(self, beat_index, track_index):
        self._partition[track_index][beat_index] = not self._partition[track_index][beat_index]

    def left_shift(self, beat_index):
        for track_index in range(self.tracks_count):
            self._partition[track_index].pop(beat_index)
            self._partition[track_index].append(False)

    def right_shift(self, beat_index):
        for track_index in range(self.tracks_count):
            self._partition[track_index].insert(beat_index, False)
            self._partition[track_index].pop

    def load(self):
        try:
            input = ''
            with open(self.filename) as fp:
                lineno = 0
                while lineno < self.tracks_count:
                    line = fp.readline().rstrip()
                    line = line.ljust(self.beats_count, self.__EMPTY_FPR)[:self.beats_count]
                    for i in range(len(line)):
                        self._partition[lineno][i] = line[i] == self.__NOTE_FPR
                    lineno += 1
                self.title=fp.readline().rstrip()
                while line:
                    line=fp.readline()
                    self.comment+=line
            fp.close()
        except FileNotFoundError as e:
            self.title = os.path.splitext(self.filename)[0]
            pass

    def save(self):
        output = ''
        for track_index in range(0, self.tracks_count):
            for beat_index in range(0, self.beats_count):
                has_note = self.has_note(beat_index, track_index)
                output += self.__NOTE_FPR if has_note else self.__EMPTY_FPR
            output += '\n'
        output += self.title + '\n'
        output += self.comment

        file = open(self.filename, 'w')
        file.write(output)
        file.close()

    def export_to_mid(self):
        mid = mido.MidiFile(type=0, ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        ticks = 480

        track.append(mido.Message('program_change', program=self.program, time=0))

        for beat_index in range(self.beats_count):
            for track_index in range(self.tracks_count):
                if self.has_note(beat_index, track_index):
                    track.append(mido.Message('note_on', note=self.NOTES[track_index], time=0))
            track.append(mido.Message('note_off', time=ticks))

        mid.save(self.title + '.mid')

    def import_from_mid(self, filename):
        self.filename = os.path.splitext(filename)[0]+'.fpr'
        self.title = os.path.basename(filename)
        self.comment = 'Imported from ' + os.path.basename(filename)

        beat_index = 0
        track_index = 0

        for msg in MidiFile(filename):
            if not msg.is_meta:
                if msg.type == 'note_on':
                    track_index = self.NOTES.index(msg.note)
                    self.set_note(beat_index, track_index, True)
                if msg.time > 0 :
                    beat_index += 1
            if beat_index >= 86:
                break
