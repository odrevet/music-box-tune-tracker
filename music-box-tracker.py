#!/usr/bin/env python3

import sys
import argparse
import time
import threading

import mido
import curses
import curses.textpad
from curses.textpad import rectangle

import const
from document import Document
from input import Input

def main(stdscr, port, document, input):
    cursor_y = input.start_y + input.offset_x
    cursor_x = input.start_x + input.offset_y

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(const.PAIR_NOTE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(const.PAIR_INPUT_A, -1, curses.COLOR_CYAN)
    curses.init_pair(const.PAIR_INPUT_B, -1, curses.COLOR_BLACK)
    curses.init_pair(const.PAIR_HIGHLIGHT, curses.COLOR_RED, -1)

    input.document = document
    input.draw(stdscr, cursor_x, cursor_y)

    # edit box
    editwin = curses.newwin(1,79, 20,1)
    rectangle(stdscr, 19,0, 20+1,87)
    box = curses.textpad.Textbox(editwin)
    editwin.addstr(0, 0, document.title)
    stdscr.move(cursor_y, cursor_x)

    thread_player = None   #thread to play music in background

    while True:
        ch = stdscr.getch()

        if ch == curses.KEY_UP:
            next_y = cursor_y - 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                input.draw(stdscr, cursor_x, cursor_y)
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_DOWN:
            next_y = cursor_y + 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                input.draw(stdscr, cursor_x, cursor_y)
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
            document.export_to_mid()
        elif ch == ord('o'):
            input.player_start_at_value(stdscr, cursor_x - 1)
            input.draw(stdscr, cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('u'):
            input.player_start_at_dec(stdscr)
            input.draw(stdscr, cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('i'):
            input.player_start_at_inc(stdscr)
            input.draw(stdscr, cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('+'):
            document.right_shift(cursor_x - 1)
            input.refresh_partition_display(stdscr)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('-'):
            document.left_shift(cursor_x - 1)
            input.refresh_partition_display(stdscr)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('e'):
            box.edit()
            title = box.gather()
            input.document.title = title
            input.draw(stdscr, cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)

        elif ch == ord(' '):
            x = cursor_x - 1
            y = cursor_y - 1
            if input.tone_descending:
                y = input.tracks_count - 1 - y

            document.reverse_note(x, y)
            input.refresh_partition_display(stdscr)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('t'):
            port.send(mido.Message('note_on',
                                   note=document.NOTES[cursor_y - (input.start_y + input.offset_y)]))
        elif ch == ord('r'):
            stdscr.move(cursor_y, cursor_x)
            for track_index in range(input.tracks_count):
                if document.has_note(cursor_x - 1, track_index):
                    port.send(mido.Message('note_on', note=document.NOTES[track_index]))
        elif ch == ord('p'):
            if thread_player is not None and thread_player.is_alive():
                thread_player.do_run = False
                thread_player.join()
            else:
                thread_player = threading.Thread(target = play,
                                                 args=(stdscr, port, document, input))
                thread_player.start()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('s'):
            document.save()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('l'):
            document.load()
            input.draw(stdscr, cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('q'):
            break

    if thread_player is not None and thread_player.is_alive():
        thread_player.do_run = False
        thread_player.join()

    port.close()

def play(stdscr, port, document, input):
    t = threading.currentThread()
    SLEEP_DURATION = .45
    PROGRESS_INDICATOR_Y = input.tracks_count + input.offset_y + 2
    PROGRESS_INDICATOR_CH = '■'

    for beat_index in range(input.player_start_at, input.beats_count):
        if getattr(t, "do_run", True) == False:
            stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.beats_count)
            return
        for track_index in range(input.tracks_count):
            if document.has_note(beat_index, track_index):
                port.send(mido.Message('note_on', note=document.NOTES[track_index]))
        time.sleep(SLEEP_DURATION)
        #update progress indicator
        stdscr.move(PROGRESS_INDICATOR_Y, beat_index + input.offset_x)
        stdscr.addch(PROGRESS_INDICATOR_CH)
        stdscr.refresh()
    stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.beats_count + input.offset_x)

if __name__=="__main__":
    portname = None
    program = 8
    input = Input()
    document = Document(input.beats_count, input.tracks_count)

    parser=argparse.ArgumentParser()
    parser.add_argument('--port',    help='name of the midi port to use')
    parser.add_argument('--file',    help='fpr file to open')
    parser.add_argument('--program', help='midi instrument code')
    parser.add_argument('--title',   help='set the title of a new tune')
    parser.add_argument('--low',     help='display low pitch notes first', action='store_true')

    args=parser.parse_args()
    if args.port : portname = args.port
    if args.file : document.filename = args.file
    elif args.title: document.title = args.title
    if args.program : program = int(args.program)
    if args.low: input.tone_descending = False

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
