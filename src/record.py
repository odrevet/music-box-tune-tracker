import os


class Record:
    # what the .fpr format uses
    __NOTE_FPR = "+"
    __EMPTY_FPR = "-"
    NOTES = [67, 72, 74, 76, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98]
    MAX_BEAT = 86
    TONES_COUNT = 16
    TRACKS_COUNT = 22

    def __init__(self, beats_count):
        self.filename = None
        self.title = "Default"
        self.comment = ""

        # list of lists of boolean: [track][beat] True indicates a note
        self._partition = [
            [False for x in range(beats_count)] for y in range(Record.TONES_COUNT)
        ]
        self.beats_count = beats_count

    def has_note(self, beat_index, tone_index):
        return self._partition[tone_index][beat_index]

    def set_note(self, beat_index, tone_index, value):
        self._partition[tone_index][beat_index] = value

    def get_track(self, tone_index):
        return self._partition[tone_index]

    def get_beats(self, beat_index):
        return [tone_index[beat_index] for tone_index in self._partition]

    def reverse_note(self, beat_index, tone_index):
        self._partition[tone_index][beat_index] = not self._partition[tone_index][
            beat_index
        ]

    def left_shift(self, beat_index):
        for tone_index in range(Record.TONES_COUNT):
            self._partition[tone_index].pop(beat_index)
            self._partition[tone_index].append(False)
        self.beats_count -= 1

    def right_shift(self, beat_index):
        for tone_index in range(Record.TONES_COUNT):
            self._partition[tone_index].insert(beat_index, False)
        self.beats_count += 1

    def resize_beats(self, size):
        self.beats_count = size
        for tone_index in range(Record.TONES_COUNT):
            diff_beat = self.beats_count - len(self._partition[tone_index])
            if diff_beat == 0:
                continue

            if diff_beat > 0:
                self._partition[tone_index].extend([False] * diff_beat)
            elif diff_beat < 0:
                self._partition[tone_index] = self._partition[tone_index][:diff_beat]

    def load(self):
        try:
            with open(self.filename) as fp:
                lineno = 0
                max_len_line = 0
                while lineno < Record.TONES_COUNT:
                    line = fp.readline().rstrip()
                    len_line = len(line)
                    if len_line > max_len_line:
                        max_len_line = len_line
                    self._partition[lineno] = [False] * len_line
                    for i in range(len_line):
                        self._partition[lineno][i] = line[i] == self.__NOTE_FPR
                    lineno += 1

                self.resize_beats(max_len_line)

                self.title = fp.readline().rstrip()
                while line:
                    line = fp.readline()
                    self.comment += line
            fp.close()
        except FileNotFoundError as e:
            self.title = os.path.splitext(self.filename)[0]
            pass

    def to_fpr(self):
        output = ""
        for tone_index in range(0, Record.TONES_COUNT):
            for beat_index in range(0, self.beats_count):
                has_note = self.has_note(beat_index, tone_index)
                output += self.__NOTE_FPR if has_note else self.__EMPTY_FPR
            output += "\n"
        output += self.title + "\n"
        output += self.comment
        return output

    def save(self):
        file = open(self.filename, "w")
        file.write(self.to_fpr())
        file.close()
