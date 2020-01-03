#!/usr/bin/env python3

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
    curses.init_pair(const.PAIR_NOTE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(const.PAIR_INPUT_A, -1, curses.COLOR_BLACK)
    curses.init_pair(const.PAIR_INPUT_B, -1, curses.COLOR_MAGENTA)

    input.draw(stdscr)

    populate_screen(stdscr, document, input)
    stdscr.move(cursor_y, cursor_x)

    thread_player = None   #thread to play music in background

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
            right_shift(partition, cursor_x - 1)
            populate_screen(stdscr, document, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('-'):
            populate_partition(stdscr, partition, input)
            left_shift(partition, cursor_x - 1)
            populate_screen(stdscr, document, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord(' '):
            if chr(stdscr.inch(cursor_y, cursor_x) & curses.A_CHARTEXT) != const.NOTE_CH:
                stdscr.attron(curses.color_pair(const.PAIR_NOTE))
                stdscr.addch(const.NOTE_CH)
                stdscr.attroff(curses.color_pair(const.PAIR_NOTE))
            else:
                pair = None
                if cursor_x % 2 != 0:
                    pair = const.PAIR_INPUT_A
                else:
                    pair = const.PAIR_INPUT_B
                attr = curses.color_pair(pair)
                stdscr.attron(attr)
                stdscr.addch(const.EMPTY_CH)
                stdscr.attroff(attr)

            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('t'):
            port.send(mido.Message('note_on',
                                   note=NOTES[cursor_y - (input.start_y + input.offset_y)]))
        elif ch == ord('c'):
            populate_partition(stdscr, partition, input)
            stdscr.move(cursor_y, cursor_x)
            for partition_y in range(input.length_y):
                if document.has_note(cursor_x - 1, partition_y):
                    port.send(mido.Message('note_on', note=NOTES[partition_y]))
        elif ch == ord('p'):
            if thread_player is not None and thread_player.is_alive():
                thread_player.do_run = False
                thread_player.join()
            else:
                populate_partition(stdscr, partition, input)
                thread_player = threading.Thread(target = play,
                                                 args=(stdscr, port, document, input))
                thread_player.start()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('s'):
            populate_partition(stdscr, partition, input)
            document.save()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('l'):
            document.load()
            populate_screen(stdscr, document, input)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('q'):
            break

    if thread_player is not None and thread_player.is_alive():
        thread_player.do_run = False
        thread_player.join()

    port.close()

def populate_partition(stdscr, partition, input):
    '''Read screen and populate the partition'''
    for screen_y in range(input.start_y, input.length_y):
        for screen_x in range(input.start_x, input.length_x):
            partition[screen_y][screen_x] = chr(stdscr.inch(screen_y + input.offset_y,
                                                        screen_x + input.offset_x)
                                                & curses.A_CHARTEXT) == const.NOTE_CH

def populate_screen(stdscr, document, input):
    '''Read parition and populate the screen'''
    for partition_y in range(input.length_y):
        for partition_x in range(input.length_x):
            stdscr.move(input.start_y + input.offset_y + partition_y,
                        input.start_x + input.offset_x + partition_x)
            attr=None
            ch=None
            if document.has_note(partition_x, partition_y):
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

def play(stdscr, port, document, input):
    t = threading.currentThread()
    SLEEP_DURATION = .45
    PROGRESS_INDICATOR_Y = input.length_y + input.offset_y + 2
    PROGRESS_INDICATOR_CH = '■'

    for partition_x in range(input.player_start_at, input.length_x):
        if getattr(t, "do_run", True) == False:
            stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.length_x)
            return
        for partition_y in range(input.length_y):
            if document.has_note(partition_x, partition_y):
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

    ticks = 480

    track.append(mido.Message('program_change', program=document.program, time=0))

    for partition_x in range(document.length_x):
        for partition_y in range(document.length_y):
            if document.has_note(partition_x, partition_y):
                track.append(mido.Message('note_on', note=NOTES[partition_y], time=0))
        track.append(mido.Message('note_off', time=ticks))

    mid.save(document.title + '.mid')

def left_shift(partition, x):
    for partition_y in range(document.length_y):
        partition[partition_y].pop(x)
        partition[partition_y].append(False)

def right_shift(partition, x):
    for partition_y in range(document.length_y):
        partition[partition_y].insert(x, False)
        partition[partition_y].pop

if __name__=="__main__":
    portname = None
    program = 8
    input = Input()
    document = Document(input.length_x, input.length_y)

    parser=argparse.ArgumentParser()
    parser.add_argument('--port',    help='name of the midi port to use')
    parser.add_argument('--file',    help='fpr file to open')
    parser.add_argument('--program', help='midi instrument code')
    parser.add_argument('--title',   help='set the title of a new tune')
    args=parser.parse_args()
    if args.port : portname = args.port
    if args.file : document.filename = args.file
    elif args.title: document.title = args.title
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
