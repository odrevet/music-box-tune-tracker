import const

class Document:
    filename = None
    title = 'Default'
    comment = ''
    partition = None
    length_x = 0
    length_y = 0
    program = 8

    def __init__(self, length_x, length_y):
        self.partition = [[const.EMPTY_CH for x in range(length_x)]
                          for y in range(length_y)]
        self.length_x = length_x
        self.length_y = length_y

    def load(self):
        input = ''
        with open(self.filename) as fp:
            lineno = 0
            while lineno < self.length_y:
                line = fp.readline().rstrip()
                line = line.replace(const.EMPTY_FPR, const.EMPTY_CH)
                line = line.replace(const.NOTE_FPR, const.NOTE_CH)
                line = line.ljust(self.length_x, const.EMPTY_CH)[:self.length_x]
                self.partition[lineno] = list(line)
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
                ch = chr(self.partition[partition_y][partition_x])
                output += const.NOTE_FPR if ch == const.NOTE_CH else const.EMPTY_FPR
            output += '\n'
        output += self.title
        output += self.comment

        file = open(self.filename, 'w')
        file.write(output)
        file.close()
