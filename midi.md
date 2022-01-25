With the `mido` library and it's dependancy installed: 

```
pip install mido python-rtmidi
```

Music Box Tune Tracker has extra functionalities: 

* Import / Export songs to midi
* Use midi as an audio backend

# Play sounds using a Midi software synthesize

Timidity is a great option, which can be installed under Linux Ubuntu with :

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