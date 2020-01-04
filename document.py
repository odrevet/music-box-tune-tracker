import mido
import const

class Document:
    filename = None
    title = 'Default'
    comment = ''
    partition = None
    length_x = 0    #length of beats
    length_y = 0    #length of tracks
    program = 8
    NOTES = [67, 72, 74, 76, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98]

    def __init__(self, length_x, length_y):
        self.partition = [[False for x in range(length_x)]
                          for y in range(length_y)]
        self.length_x = length_x
        self.length_y = length_y

    def has_note(self, x, y):
        return self.partition[y][x]

    def load(self):
        input = ''
        with open(self.filename) as fp:
            lineno = 0
            while lineno < self.length_y:
                line = fp.readline().rstrip()
                line = line.ljust(self.length_x, const.EMPTY_FPR)[:self.length_x]
                for i in range(len(line)):
                    self.partition[lineno][i] = line[i] == const.NOTE_FPR
                lineno += 1
            self.title=fp.readline().rstrip()
            while line:
                line=fp.readline()
                self.comment+=line
        fp.close()

    def save(self):
        output = ''
        for partition_y in range(0, self.length_y):
            for partition_x in range(0, self.length_x):
                has_note = self.has_note(partition_x, partition_y)
                output += const.NOTE_FPR if has_note else const.EMPTY_FPR
            output += '\n'
        output += self.title
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

        for partition_x in range(self.length_x):
            for partition_y in range(self.length_y):
                if self.has_note(partition_x, partition_y):
                    track.append(mido.Message('note_on', note=self.NOTES[partition_y], time=0))
            track.append(mido.Message('note_off', time=ticks))

        mid.save(self.title + '.mid')
