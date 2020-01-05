# About Fred Record Player

I ported some code from Fred Record Player to create music box tune tracker.
I had to first build Fred Record Player under Linux. Fortunately the source code is
available online and is written in c# which can be compiled with mono.

Here is what I did to compile and launch Fred Record Player under Ubuntu.

# Install mono

```
sudo apt install mono-complete
```

# Build

 ```
xbuild /p:Configuration=Release /p:TargetFrameworkVersion=v4.5 Fred.RecordPlayer.csproj
```

# Run and export to scad

## Windows path separator

The MONO_IOMAP environment variable need to be set to all

```
export MONO_IOMAP="all"
```

Otherwise the software will crash when trying to create a .scad file as it cannot find the "Fred.RecordPlayer/.\Resources\FisherPriceTemplate.scad" file because of Windows path separators.

## Set local

If your computer local set decimal separator to `comma`, then the scad file pin will not have the right format, as dot in float numbers will be exported as commas, messing with the commas use to separate arguments in the pin function calls: `pin(42,0,42,0,42,0,0);` instead of `pin(42.0,42.0,42.0,0);`

a good solution is to set the LC_ALL environement variable to C 

## To sum up

run with

```
LC_ALL=C MONO_IOMAP=all mono bin/Release/Fred.RecordPlayer.exe
```

# Song playback problem

MidiPlayer.cs uses the functions midiOutOpen, midiOutShortMsg, midiOutClose, from winmm.dll.

These are not supported under linux so a replacement library need to be found for the playback.

# Sources

* https://www.mono-project.com/docs/getting-started/application-portability/
* https://www.mono-project.com/docs/gui/winforms/porting-winforms-applications/
