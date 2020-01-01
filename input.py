from curses.textpad import rectangle

class Input:
    start_y = 0
    start_x = 0
    length_y = 16
    length_x = 86
    offset_x = 1
    offset_y = 1
    player_start_at = 0

    def __draw_tone(self, stdscr, index, tone_str):
        stdscr.addstr(self.start_y + self.offset_y + index,
                      self.start_x + self.length_x + self.offset_x + 1,
                      tone_str)

    def draw(self, stdscr):
        # draw border
        rectangle(stdscr,
                  self.start_y,
                  self.start_y,
                  self.length_y + self.offset_y,
                  self.length_x + self.offset_x)

        # draw tones
        tones = ['G4',
                 'C5', 'D5', 'E5', 'G5', 'A5', 'B5',
                 'C6', 'D6', 'E6', 'F6', 'G6', 'A6', 'B6',
                 'C7', 'D7']

        for i in range(0, self.length_y):
            self.__draw_tone(stdscr, i, tones[i])

        #draw player start at
        stdscr.move(self.length_y + self.offset_y + 1, self.player_start_at + self.offset_x)
        stdscr.addch('|')

    def can_move(self, y, x):
        return (y > self.start_y
                and x > self.start_x
                and y < self.length_y + self.offset_y
                and x < self.length_x + self.offset_x)

    def player_start_at_value(self, stdscr, value):
        if value < self.length_x and value >= 0:
            stdscr.move(self.length_y + self.offset_y + 1,
                        self.player_start_at + self.offset_x)
            stdscr.addch(' ')
            self.player_start_at = value
            self.draw(stdscr)

    def player_start_at_inc(self, stdscr):
        self.player_start_at_value(stdscr, self.player_start_at + 1)

    def player_start_at_dec(self, stdscr):
        self.player_start_at_value(stdscr, self.player_start_at - 1)
