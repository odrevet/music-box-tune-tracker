# Import/Export songs from midi files

With the `mido` package installed: 

```
pip install mido
```

More command line functions and shortcuts will be available: 


## Extra Shortcut
`x` key to export to .mid


## Extra Command line arguments
```
--mid Import song from midi file exported by music box tune tracker
--maniacs Import song from midi files exported from musicboxmaniacs.com
--bpm set bpm
--program change instruments
```

# Play sounds using a Midi software synthesize

To use Midi as an audio backend you will need two extra packages: 

```
pip install mido python-rtmidi
```

And a midi synthesizer: Timidity is a great option, which can be installed under Linux Ubuntu with :

```
 sudo apt install libasound2-dev libjack-dev timidity
```

and then run with:

```
timidity -iA -B2,8 -Os1l -s 11100
```

## List Midi ports

Under Linux, midi 'Port name' can be listed with

```
aplaymidi -l

 Port    Client name                      Port name
 14:0    Midi Through                     Midi Through Port-0
128:0    TiMidity                         TiMidity port 0
128:1    TiMidity                         TiMidity port 1
128:2    TiMidity                         TiMidity port 2
128:3    TiMidity                         TiMidity port 3
```

## Example

```
python music_box_tracker.py --port 'TiMidity port 0'
```
