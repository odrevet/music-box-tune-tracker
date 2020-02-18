import os

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

    def to_fpr(self):
        output = ''
        for track_index in range(0, self.tracks_count):
            for beat_index in range(0, self.beats_count):
                has_note = self.has_note(beat_index, track_index)
                output += self.__NOTE_FPR if has_note else self.__EMPTY_FPR
            output += '\n'
        output += self.title + '\n'
        output += self.comment
        return output

    def save(self):
        file = open(self.filename, 'w')
        file.write(self.to_fpr())
        file.close()
