Music box tune tracker. Create or import a tune and turn it into a record for the Fisher Price Record Player toy

music box tune tracker use the same file format (.fpr) from "Fred Record Player" available at https://www.instructables.com/id/3D-printing-records-for-a-Fisher-Price-toy-record-/

# Screenshot

<img src="https://github.com/odrevet/music-box-tune-tracker/blob/master/screenshot/screenshot.png" width="6400" height="480" />

# Prerequisites

This software uses `Python` with the `Curses` library for the User Interface. 

# Optional Dependancies 

To play music and preview what your music will sound like on a fisher price record, there are two options: 

* `Wav` playback is the more easy and is recommanded.
* `Midi` playback will add extra functionalities but will require a little more configurations.  

## WAV playback

```
pip install playsound
```

## Midi playback and extra functionalities

For more informations about using midi as an audio backend using the `mido` package, see `midi.md`. 

# Command line usage

```
optional arguments:
  -h, --help         show this help message and exit
  --fpr FPR          .fpr file to open
  --title TITLE      set the title of a new tune
  --low              display low pitch notes first
```


Opions only available if the `mido` package is installed:

```
  --port PORT        name of the midi port to use
  --mid MID          import from .mid file created with music box tune tracker
  --program PROGRAM  midi instrument code
```

# Using music box tune tracker

* Arrow key: Move the cursor
* Space: add/remove a note at cursor
* p: play/stop
* t: play the tone at cursor
* r: play the column of tones at cursor
* s: save
* l: load
* x: export to .mid (available only if the `mido` package is installed)
* e: edit title
* q: quit
* o: move the playing start location to cursor
* i: move the playing start location to the right
* u: move the playing start location to the left
* +: right shift the partition
* -: left shift the partition

# Convert .fpr to .scad

.fpr file can be converted to .scad file by using the `fpr_to_scad.py` script


```
usage: fpr_to_scad.py [-h] [--fpr FPR] [--fprbis FPRBIS] [--scad SCAD]
                      [--thickness THICKNESS]

optional arguments:
  -h, --help            show this help message and exit
  --fpr FPR             name of fpr file
  --fprbis FPRBIS       name of fpr file for second side
  --scad SCAD           name of scad file to output
  --thickness THICKNESS
                        thickness in mm. Defaults to 3 if one
                        side or 5 if two sides
```

## How to print the name of the song on the disc

The Write.scad and other files are required to have the title of the tune written on the disc

Head to https://www.thingiverse.com/thing:16193 and clic "DOWNLOAD ALL FILES". Extract the content of Writescad.zip [where OpenScad can find it](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Libraries).

Note: the ' are rendered as ", so in the scad file I replace all ' by ` before rendering.

# Convert .scad to .stl

the scad file can be use with [OpenScad](https://www.openscad.org) to create a .stl file to 3D print the record.

Open a scad file then menu Design/Render (F6) then File/Export/Export as STL (F7)

# Convert .mid from musicboxmaniacs to .fpr

The `maniacs_mid_to_fpr.py` program can convert .mid file from https://musicboxmaniacs.com/

It can only convert .mid designed for the `Kikkerland 15 music box`

```
usage: maniacs_mid_to_fpr.py [-h] [--mid MID] [--fpr FPR]

optional arguments:
  -h, --help  show this help message and exit
  --mid MID   file to import. .mid from musicboxmaniacs.com Kikkerland 15
  --fpr FPR   fpr file to write
```

# Thanks

Thanks to [FredMurphy](https://github.com/FredMurphy) to have created and shared "Fred Record Player" source code, it was of a great help, notably to implement the export to scad feature.

More informations on running Fred Record Player under linux are available in the [fred_record_player](fred_record_player.md) file
