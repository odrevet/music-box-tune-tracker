#!/usr/bin/env python3

import sys
import os
import argparse
import time
import threading

import mido
from mido import MidiFile
import curses
import curses.textpad
from curses.textpad import rectangle

import const
from record import Record
from input import Input

def export_to_mid(record, program):
    ticks = 480
    mid = mido.MidiFile(type=0, ticks_per_beat=ticks)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.Message('program_change', program=program, time=0))

    for beat_index in range(record.beats_count):
        for track_index in range(record.tracks_count):
            if record.has_note(beat_index, track_index):
                track.append(mido.Message('note_on', note=record.NOTES[track_index], time=0))
        track.append(mido.Message('note_off', time=ticks))

    mid.save(record.title + '.mid')

def import_from_mid(record, filename):
    record.filename = os.path.splitext(filename)[0]+'.fpr'
    record.title = os.path.basename(filename)
    record.comment = 'Imported from ' + os.path.basename(filename)

    beat_index = 0
    track_index = 0

    for msg in MidiFile(filename):
        if not msg.is_meta:
            if msg.type == 'note_on':
                track_index = record.NOTES.index(msg.note)
                record.set_note(beat_index, track_index, True)
            if msg.time > 0 :
                beat_index += 1
        if beat_index >= const.BEAT_COUNT:
            break

def main(stdscr, port, input, program):
    cursor_y = input.start_y + input.offset_x
    cursor_x = input.start_x + input.offset_y

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(const.PAIR_NOTE, curses.COLOR_RED, curses.COLOR_YELLOW)
    curses.init_pair(const.PAIR_INPUT_A, -1, curses.COLOR_CYAN)
    curses.init_pair(const.PAIR_INPUT_B, -1, curses.COLOR_BLACK)
    curses.init_pair(const.PAIR_HIGHLIGHT, curses.COLOR_RED, -1)

    record = input.record
    input.window = stdscr
    input.draw(cursor_x, cursor_y)

    # edit box
    editwin = curses.newwin(1,79, 20,1)
    editwin.addstr(0, 0, record.title)
    rectangle(stdscr, 19,0, 20+1,87)
    box = curses.textpad.Textbox(editwin, insert_mode=True)
    stdscr.move(cursor_y, cursor_x)

    thread_player = None   #thread to play music in background

    while True:
        ch = stdscr.getch()

        if ch == curses.KEY_UP:
            next_y = cursor_y - 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                input.draw(cursor_x, cursor_y)
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_DOWN:
            next_y = cursor_y + 1;
            if(input.can_move(next_y, cursor_x)):
                cursor_y = next_y
                input.draw(cursor_x, cursor_y)
                stdscr.move(cursor_y, cursor_x)
        elif ch == curses.KEY_LEFT:
            next_x = cursor_x - 1;
            if(input.can_move(cursor_y, next_x)):
                cursor_x = next_x
                stdscr.move(cursor_y, cursor_x)
            elif input.display_from > 0:
                input.display_from -= 1
                input.refresh_partition_display()
                input.draw_player_start_at()
        elif ch == curses.KEY_RIGHT:
            next_x = cursor_x + 1;
            if(input.can_move(cursor_y, next_x)):
                cursor_x = next_x
                stdscr.move(cursor_y, cursor_x)
            elif input.display_from + cursor_x < record.beats_count:
                input.display_from += 1
                input.refresh_partition_display()
                input.draw_player_start_at()
        elif ch == ord('x'):
            export_to_mid(record, program)
        elif ch == ord('o'):
            input.player_start_at_value(input.display_from + cursor_x - 1)
            input.draw(cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('u'):
            input.player_start_at_dec()
            input.draw(cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('i'):
            input.player_start_at_inc()
            input.draw(cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('+'):
            record.right_shift(cursor_x - 1)
            input.refresh_partition_display()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('-'):
            record.left_shift(cursor_x - 1)
            input.refresh_partition_display()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('e'):
            box.edit()
            title = box.gather()
            input.record.title = title
            input.draw(cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord(' '):
            x = input.display_from + cursor_x - 1
            y = cursor_y - 1
            if input.tone_descending:
                y = input.tracks_count - 1 - y
            record.reverse_note(x, y)
            input.refresh_partition_display()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('t'):
            track_index = cursor_y - (input.start_y + input.offset_y)
            if input.tone_descending:
                track_index = input.tracks_count - 1 - track_index
            port.send(mido.Message('note_on', note=record.NOTES[track_index]))
        elif ch == ord('r'):
            stdscr.move(cursor_y, cursor_x)
            beats = record.get_beats(cursor_x -1)
            for track_index in range(len(beats)):
                if beats[track_index]:
                    port.send(mido.Message('note_on', note=record.NOTES[track_index]))
        elif ch == ord('p'):
            if thread_player is not None and thread_player.is_alive():
                thread_player.do_run = False
                thread_player.join()
                input.draw(cursor_x, cursor_y)
            else:
                thread_player = threading.Thread(target = play,
                                                 args=(stdscr, port, record, input))
                thread_player.start()
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('s'):
            record.save()
        elif ch == ord('l'):
            record.load()
            input.draw(cursor_x, cursor_y)
            stdscr.move(cursor_y, cursor_x)
        elif ch == ord('q'):
            break

    if thread_player is not None and thread_player.is_alive():
        thread_player.do_run = False
        thread_player.join()

    port.close()

def play(stdscr, port, record, input):
    t = threading.currentThread()
    FPR_SEC_BETWEEN_BEATS = 0.5
    PROGRESS_INDICATOR_Y = input.tracks_count + input.offset_y + 1

    for beat_index in range(input.player_start_at, record.beats_count):
        if getattr(t, "do_run", True) == False:
            stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.beats_count)
            return
        for track_index in range(input.tracks_count):
            if record.has_note(beat_index, track_index):
                port.send(mido.Message('note_on', note=record.NOTES[track_index]))
        time.sleep(FPR_SEC_BETWEEN_BEATS)
        for track_index in range(input.tracks_count):
            if record.has_note(beat_index, track_index):
                port.send(mido.Message('note_off', note=record.NOTES[track_index]))

        #update progress indicator
        progress_indicator_x =  beat_index + input.offset_x - input.display_from
        if progress_indicator_x <= input.beats_count:
            stdscr.move(PROGRESS_INDICATOR_Y, progress_indicator_x)
            stdscr.addch('△')
            stdscr.refresh()
    stdscr.hline(PROGRESS_INDICATOR_Y, 0, ' ', input.beats_count + input.offset_x)

if __name__=="__main__":
    portname = None
    program = 10
    record = Record(0, const.TRACK_COUNT)

    parser=argparse.ArgumentParser()
    parser.add_argument('--port',    help='name of the midi port to use')
    parser.add_argument('--fpr',     help='.fpr file to open')
    parser.add_argument('--mid',     help='import from .mid file created with music box tune tracker')
    parser.add_argument('--program', help='midi instrument code')
    parser.add_argument('--title',   help='set the title of a new tune')
    parser.add_argument('--low',     help='display low pitch notes first', action='store_true')

    args=parser.parse_args()
    if args.port : portname = args.port
    if args.fpr : record.filename = args.fpr
    if args.title: record.title = args.title
    if args.program : program = int(args.program)

    # midi port
    port = None

    if record.filename:
        record.load()
    elif args.mid is not None :
            import_from_mid(record, args.mid)
    else:
        record.filename = record.title + '.fpr'

    if record.beats_count < const.BEAT_COUNT:
        record.resize_beats(const.BEAT_COUNT)

    try:
        port = mido.open_output(portname)
    except:
        port = mido.open_output()

    port.send(mido.Message('program_change', program=program))

    input = Input(record)
    if args.low: input.tone_descending = False

    try:
        curses.wrapper(main, port, input, program)
    except curses.error:
        sys.exit('Error when drawing to terminal (is the terminal too small ? )')
