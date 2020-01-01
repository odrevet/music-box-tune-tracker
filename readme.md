This is a minimal music box editor compatible with Fred Record Player,
available at https://www.instructables.com/id/3D-printing-records-for-a-Fisher-Price-toy-record-/

Fred Record Player can be uses to open fpr which can be converted to SCAD file, which can be 3D printed into
real records to uses with the original Fisher Price Record Player.

# Prerequisites

This software uses Python with the Curses library for the interface and the Mido library for sound. 
You will also need a Midi backend, I use timidity, which can be installed under Linux Ubuntu with :

```
 sudo apt install libasound2-dev libjack-dev timidity
```

The python dependencies can be installed with pip:

```
pip install mido python-rtmidi
```

Then run timidity with:

```
timidity -iA -B2,8 -Os1l -s 44100
```

# Run

## List Midi ports

Under Linux, midi ports can be listed with

```
aplaymidi -l
```

```
 Port    Client name                      Port name
 14:0    Midi Through                     Midi Through Port-0
128:0    TiMidity                         TiMidity port 0
128:1    TiMidity                         TiMidity port 1
128:2    TiMidity                         TiMidity port 2
128:3    TiMidity                         TiMidity port 3
```

## Command line usage

```
usage: music-box-tracker.py [-h] [--port PORT] [--file FILE]
                            [--program PROGRAM]

optional arguments:
  -h, --help         show this help message and exit
  --port PORT        name of the midi port to use
  --file FILE        fpr file to open
  --program PROGRAM  midi instrument code
```

### Example 

``` 
python music-box-tracker.py --port 'TiMidity port 0'
```

## Using music box tracker

* Arrow key: Move the cursor
* Space: add/remove a note at cursor
* p: play/stop
* t: play the tone at cursor
* c: play the column of tones at cursor
* s: save
* l: load
* q: quit
* o: move the playing start location to cursor
* i: move the playing start location to the right
* u: move the playing start location to the left

# BUG

* The terminal must be at least 88x19 or else the software will crash

# TODO

* left and right shift the partition
* set title and comment
* export to scad
* colors
