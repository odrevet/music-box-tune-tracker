import curses
from curses.textpad import rectangle
import const

class Input:
    start_y = 0
    start_x = 0
    tracks_count = const.TRACK_COUNT
    beats_count = 86
    offset_x = 1
    offset_y = 1
    player_start_at = 0
    record = None
    tone_descending = True
    window = None

    display_from = 0

    def __init__(self, record=None, window=None):
        self.record = record
        if record and self.beats_count > record.beats_count:
            self.beats_count = record.beats_count
        self.window = window

    def __draw_tone(self, track_index, tone_str):
        self.window.addstr(self.start_y + self.offset_y + track_index,
                           self.start_x + self.beats_count + self.offset_x + 1,
                           tone_str)

    def draw_beat_index(self):
        for beat_index in range(0, self.beats_count):
            y = self.start_y + self.offset_y + self.tracks_count + 1
            beat_index_str = str(beat_index + 1 + self.display_from)
            for beat_index_str_index in range(len(beat_index_str)):
                self.window.addstr(y + beat_index_str_index,
                                   self.start_x + self.offset_x + beat_index,
                                   beat_index_str[beat_index_str_index])

    def draw_partition(self):
        '''Read parition and populate the screen'''
        # what is displayed
        NOTE_CH = '•'
        EMPTY_CH = '_'

        tracks_range = range(self.tracks_count)
        for track_index in tracks_range:
            for beat_index in range(self.beats_count):
                self.window.move(self.start_y + self.offset_y + track_index,
                            self.start_x + self.offset_x + beat_index)
                attr=None
                ch=None
                if self.tone_descending:
                    track_index = self.tracks_count - 1 - track_index

                if self.record.has_note(self.display_from + beat_index, track_index):
                    attr=curses.color_pair(const.PAIR_NOTE)
                    ch=NOTE_CH
                else:
                    ch=EMPTY_CH
                    pair = None
                    if beat_index % 2 == 0:
                        pair = const.PAIR_INPUT_A
                    else:
                        pair = const.PAIR_INPUT_B
                    attr = curses.color_pair(pair)

                self.window.attron(attr)
                self.window.addch(ch)
                self.window.attroff(attr)

    def draw_player_start_at(self):
        y = self.tracks_count + self.offset_y + self.start_y
        self.window.hline(y, 0, '_', self.beats_count + self.offset_x)

        x = self.player_start_at + self.offset_x - self.display_from
        if x > 0 and x <= self.beats_count:
            self.window.move(y, x)
            self.window.addch('▲')

    def draw(self, cursor_x, cursor_y):
        # draw border
        rectangle(self.window,
                  self.start_y,
                  self.start_x,
                  self.tracks_count + self.offset_y + self.start_y,
                  self.beats_count + self.offset_x + self.start_x)

        #title
        if self.record.title is not None:
            self.window.addstr(self.start_y, self.start_x + 2, self.record.title)

        # draw partition table
        self.draw_partition()
        self.draw_player_start_at()

        self.draw_beat_index()

        # draw tones TODO parametrable tones
        tones = ['G4 Sol',
                 'C5 Do', 'D5 Ré', 'E5 Mi', 'G5 Sol', 'A5 La', 'B5 Si',
                 'C6 Do', 'D6 Ré', 'E6 Mi', 'F6 Fa', 'G6 Sol', 'A6 La', 'B6 Si',
                 'C7 Do', 'D7 Ré']

        if self.tone_descending:
            tones.reverse()

        for track_index in range(0, self.tracks_count):
            if cursor_y - 1 == track_index:
                self.window.attron(curses.color_pair(const.PAIR_HIGHLIGHT))
            self.__draw_tone(track_index, tones[track_index])
            if cursor_y - 1 == track_index:
                self.window.attroff(curses.color_pair(const.PAIR_HIGHLIGHT))

    def can_move(self, y, x):
        return (y > self.start_y
                and x > self.start_x
                and y < self.tracks_count + self.offset_y
                and x < self.beats_count + self.offset_x)

    def player_start_at_value(self, value):
        if value < self.record.beats_count and value >= 0:
            self.window.move(self.tracks_count + self.offset_y + 1,
                        self.player_start_at + self.offset_x)
            self.window.addch(' ')
            self.player_start_at = value

    def player_start_at_inc(self):
        self.player_start_at_value(self.player_start_at + 1)

    def player_start_at_dec(self):
        self.player_start_at_value(self.player_start_at - 1)
