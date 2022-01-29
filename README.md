Music box tune tracker. Create or import a tune and turn it into a record for the Fisher Price Record Player toy

 `Music Box Tune Tracker` uses the same file format (.fpr) from `Fred Record Player` available at https://www.instructables.com/id/3D-printing-records-for-a-Fisher-Price-toy-record-/

For usage, use the `--help` argument. Some arguments are available only if some optional package are installed.

# Screenshot

<img src="https://github.com/odrevet/music-box-tune-tracker/blob/master/screenshot/screenshot.png" width="6400" height="480" />

# Prerequisites

This software uses `Python` with the `Curses` library for the User Interface.

# Optional Dependancies

To preview what your music will sound like on a fisher price record, there are two options:

* `Wav` playback is the more easy and is recommanded.
* `Midi` playback will add extra functionalities but will require a little more configurations.

## WAV audio backend

```
pip install playsound
```

## Midi audio backend and extra functionalities

For more informations about using midi as an audio backend and import/export from midi files, see [midi.md](doc/midi.md).

# music_box_tracker.py

Edit and preview `fpr` files.

## Keys

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

# Convert .scad to .stl

the scad file can be use with [OpenScad](https://www.openscad.org) to create a .stl file to 3D print the record.

Open a scad file then menu Design/Render (F6) then File/Export/Export as STL (F7)

# How to print the name of the song on the disc

The Write.scad and it's dependancies are required to have the title of the tune written on the disc. 

Move the files under writescad (updated version from https://www.thingiverse.com/thing:16193) [where OpenScad can find it](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Libraries).


# Thanks

* [FredMurphy](https://github.com/FredMurphy) to have created and shared "Fred Record Player" source code, it was of a great help, notably to implement the export to scad feature.

More informations on running Fred Record Player under linux are available in the [fred_record_player](doc/fred_record_player.md) file

* Writing functions by HarlanDMii http://www.thingiverse.com/thing:16193

* Contributors
