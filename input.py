import curses
from curses.textpad import rectangle
import const

class Input:
    start_y = 0
    start_x = 0
    length_y = 16
    length_x = 86
    offset_x = 1
    offset_y = 1
    player_start_at = 0
    document = None

    def __draw_tone(self, stdscr, index, tone_str):
        stdscr.addstr(self.start_y + self.offset_y + index,
                      self.start_x + self.length_x + self.offset_x + 1,
                      tone_str)

    def refresh_partition_display(self, stdscr):
        '''Read parition and populate the screen'''
        for partition_y in range(self.length_y):
            for partition_x in range(self.length_x):
                stdscr.move(self.start_y + self.offset_y + partition_y,
                            self.start_x + self.offset_x + partition_x)
                attr=None
                ch=None
                if self.document.has_note(partition_x, partition_y):
                    attr=curses.color_pair(const.PAIR_NOTE)
                    ch=const.NOTE_CH
                else:
                    ch=const.EMPTY_CH
                    pair = None
                    if partition_x % 2 == 0:
                        pair = const.PAIR_INPUT_A
                    else:
                        pair = const.PAIR_INPUT_B
                    attr = curses.color_pair(pair)

                stdscr.attron(attr)
                stdscr.addch(ch)
                stdscr.attroff(attr)

    def draw(self, stdscr, cursor_x, cursor_y):
        # draw border
        rectangle(stdscr,
                  self.start_y,
                  self.start_y,
                  self.length_y + self.offset_y,
                  self.length_x + self.offset_x)

        # draw partition table
        self.refresh_partition_display(stdscr)

        # draw tones
        TONES = ['G4 Sol',
                 'C5 Do', 'D5 Ré', 'E5 Mi', 'G5 Sol', 'A5 La', 'B5 Si',
                 'C6 Do', 'D6 Ré', 'E6 Mi', 'F6 Fa', 'G6 Sol', 'A6 La', 'B6 Si',
                 'C7 Do', 'D7 Ré']

        for i in range(0, self.length_y):
            if cursor_y - 1 == i:
                stdscr.attron(curses.color_pair(const.PAIR_HIGHLIGHT))
            self.__draw_tone(stdscr, i, TONES[i])
            if cursor_y - 1 == i:
                stdscr.attroff(curses.color_pair(const.PAIR_HIGHLIGHT))

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

    def player_start_at_inc(self, stdscr):
        self.player_start_at_value(stdscr, self.player_start_at + 1)

    def player_start_at_dec(self, stdscr):
        self.player_start_at_value(stdscr, self.player_start_at - 1)
