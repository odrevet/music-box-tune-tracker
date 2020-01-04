# About Fred Record Player

I ported some code from Fred Record Player to create music box tune tracker.
I had to first build Fred Record Player under Linux. Fortunately the source code is
avaiable online and is written in c# which can be compiled with mono.

Here is what I did to compile and launch Fred Record Player under Ubuntu.

# Install mono

```
sudo apt install mono-complete
```

# Build

 xbuild /p:Configuration=Release /p:TargetFrameworkVersion=v4.5 Fred.RecordPlayer.csproj

# Run

## Windows path separator

The MONO_IOMAP need to be set to all

```
export MONO_IOMAP="all"
```

Otherwise the software will crash when trying to create a .scad file as it cannot find the "Fred.RecordPlayer/.\Resources\FisherPriceTemplate.scad" file because of Windows path separators.

# Replacement for winmm.dl

MidiPlayer.cs uses the functions midiOutOpen, midiOutShortMsg, midiOutClose, from winmm.dll.

These are not supported under linux so a replacement library need to be found for the playback.

## Set local to export to scad

If your computer has local that set decimal separator to a comma, then the scad file pin will not have the write format, as dot in float numbers will be commas: `pin(42,0,42,0,42,0,0);` instead of `pin(42.0,42.0,42.0,0);`

## To sum up

run with

```
LC_ALL=C MONO_IOMAP=all mono bin/Release/Fred.RecordPlayer.exe
```

# Sources

* https://www.mono-project.com/docs/getting-started/application-portability/
* https://www.mono-project.com/docs/gui/winforms/porting-winforms-applications/
