import sys
import argparse
import time
import threading

import mido
import curses

import const
from document import Document
from input import Input

NOTES = [67, 72, 74, 76, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98]

def main(stdscr, port, document, input):
    cursor_y = input.start_y + input.offset_x
    cursor_x = input.start_x + input.offset_y
    partition = document.partition

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(const.PAIR_NOTE, curses.COLOR_RED, -1)

    input.draw(stdscr)

    populate_screen(stdscr, partition, input)
    stdscr.move(cursor_y, cursor_x)

    t_player = threading.Thread(target = play,
                                args=(stdscr, port, partition, input))

    while True:
        ch = stdscr.getch()

        if ch == curses.KEY_UP:
            next_y = cursor_y - 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_DOWN:
            next_y = cursor_y + 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_LEFT:
            next_x = cursor_x - 1;
            if(input.can_move(cursor_y, next_x)):
                cursor_x = next_x
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_RIGHT:
            next_x = cursor_x + 1;
            if(input.can_move(cursor_y, next_x)):
                cursor_x = next_x
                stdscr.move(cursor_y, cursor_x)
        elif ch == ord('x'):
            populate_partition(stdscr, partition, input)
            export_to_mid(document)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('o'):
            input.player_start_at_value(stdscr, cursor_x - 1)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('u'):
            input.player_start_at_dec(stdscr)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('i'):
            input.player_start_at_inc(stdscr)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('+'):
            populate_partition(stdscr, partition, input)
            right_shift(partition, cursor_x)
            populate_screen(stdscr, partition, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('-'):
            populate_partition(stdscr, partition, input)
            left_shift(partition, cursor_x)
            populate_screen(stdscr, partition, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord(' '):
            if chr(stdscr.inch(cursor_y, cursor_x) & curses.A_CHARTEXT) != const.NOTE_CH:
                stdscr.attron(curses.color_pair(const.PAIR_NOTE))
                stdscr.addch(const.NOTE_CH)
                stdscr.attroff(curses.color_pair(const.PAIR_NOTE))
            else:
                stdscr.addch(const.EMPTY_CH)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('t'):
            port.send(mido.Message('note_on',
                                   note=NOTES[cursor_y - (input.start_y + input.offset_y)]))
        elif ch == ord('c'):
            populate_partition(stdscr, partition, input)
            stdscr.move(cursor_y, cursor_x)
            for partition_y in range(0, input.length_y):
                ch = chr(partition[partition_y][cursor_x - 1])
                if ch == const.NOTE_CH:
                    port.send(mido.Message('note_on', note=NOTES[partition_y]))
        elif ch == ord('p'):
            if t_player.is_alive():
                t_player.do_run = False
                t_player.join()
            else:
                populate_partition(stdscr, partition, input)
                t_player = threading.Thread(target = play,
                                            args=(stdscr, port, partition, input))
                t_player.start()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('s'):
            populate_partition(stdscr, partition, input)
            document.save()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('l'):
            document.load()
            populate_screen(stdscr, partition, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('q'):
            break

    if t_player.is_alive():
        t_player.do_run = False
        t_player.join()

    port.close()

def populate_partition(stdscr, partition, input):
    '''Read screen and populate the partition'''
    for screen_y in range(input.start_y, input.length_y):
        for screen_x in range(input.start_x, input.length_x):
            partition[screen_y][screen_x] = stdscr.inch(screen_y + 1, screen_x + 1) & curses.A_CHARTEXT

def populate_screen(stdscr, partition, input):
    '''Read parition and populate the screen'''
    for partition_y in range(0, input.length_y):
        for partition_x in range(0, input.length_x):
            stdscr.move(input.start_y + input.offset_y + partition_y,
                        input.start_x + input.offset_x + partition_x)
            if partition[partition_y][partition_x] == const.NOTE_CH:
                stdscr.attron(curses.color_pair(const.PAIR_NOTE))
            stdscr.addch(partition[partition_y][partition_x])
            if partition[partition_y][partition_x] == const.NOTE_CH:
                stdscr.attroff(curses.color_pair(const.PAIR_NOTE))

def play(stdscr, port, partition, input):
    t = threading.currentThread()
    SLEEP_DURATION = 0.45
    PROGRESS_INDICATOR_Y = input.length_y + input.offset_y + 2
    PROGRESS_INDICATOR_CH = '■'

    for partition_x in range(input.player_start_at, input.length_x):
        if getattr(t, "do_run", True) == False:
            stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.length_x)
            return
        for partition_y in range(0, input.length_y):
            ch = chr(partition[partition_y][partition_x])
            if ch == const.NOTE_CH:
                port.send(mido.Message('note_on', note=NOTES[partition_y]))
        time.sleep(SLEEP_DURATION)
        #update progress indicator
        stdscr.move(PROGRESS_INDICATOR_Y, partition_x + input.offset_x)
        stdscr.addch(PROGRESS_INDICATOR_CH)
        stdscr.refresh()
    stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.length_x + input.offset_x)

def export_to_mid(document):
    mid = mido.MidiFile(type=0, ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.Message('program_change', program=document.program, time=0))

    for partition_x in range(0, document.length_x):
        for partition_y in range(0, document.length_y):
            ch = chr(document.partition[partition_y][partition_x])
            if ch == const.NOTE_CH:
                track.append(mido.Message('note_on', note=NOTES[partition_y], velocity=95, time=10))
                track.append(mido.Message('note_off', note=NOTES[partition_y], velocity=95, time=10))
    mid.save(document.title + '.mid')

def left_shift(partition, x):
    for partition_y in range(0, document.length_y):
        partition[partition_y].pop(x-1)
        partition[partition_y].append(const.EMPTY_CH)

def right_shift(partition, x):
    for partition_y in range(0, document.length_y):
        partition[partition_y].insert(x-1, const.EMPTY_CH)
        partition[partition_y].pop

if __name__=="__main__":
    portname = None
    program = 8
    input = Input()
    document = Document(input.length_x, input.length_y)

    parser=argparse.ArgumentParser()
    parser.add_argument('--port', help='name of the midi port to use')
    parser.add_argument('--file', help='fpr file to open')
    parser.add_argument('--program', help='midi instrument code')
    args=parser.parse_args()
    if args.port : portname = args.port
    if args.file : document.filename = args.file
    if args.program : program = int(args.program)

    # midi port
    port = None

    if document.filename:
        document.load()
    else:
        document.filename = document.title + '.fpr'

    try:
        port = mido.open_output(portname)
    except:
        port = mido.open_output()

    port.send(mido.Message('program_change', program=program))
    document.program = program

    curses.wrapper(main, port, document, input)
