# Tin-Whistle-Helper - _alpha version_
Tin Whistle Helper helps you practice playing your tin whistle in D 
and lets you make and edit the tabs. 

## Practice features
- scrolling cursor (vertical red indicator) shows which note/tab to play
- tabs length show note duration 
- indicators above tabs show decorators
<br />  <br />
- adjustable tempo 
- audible metronome with count-off (CO)
- song can be played in background in scale of tin whistle or low whistle

## Edit features
- add your own songs / tab files
- edit tab notes and lengths directly or edit the .tb/.tbs files
- add decorators
- edit tab color
<br />  <br />
![Figure 1](https://github.com/NardJ/Tin-Whistle-Helper/blob/main/screenshots/MainWindow.png "Screenshot")

## Demo (YouTube)
[![Demo Video](https://img.youtube.com/vi/YW5N0eGlMkk/1.jpg)](https://youtu.be/YW5N0eGlMkk)

</br>

---

## Installation
**Install packages**<br>
For Linux and Windows 64 bit, try the install packages under <a href="https://github.com/NardJ/Tin-Whistle-Helper/releases" target="_blank" >releases</a>.
<br>These have been tested in Windows 10 64-bit and Linux Mint 20.1 64-bit. 
<br><br>
**Run from source**<br>
For OSX, 32-bit, untested systems or if the install packages do not work, you can run Tin Whistle Helper using Python 3:

1) Install Python **3**, pip and tkinter if needed
   * Linux: ```sudo apt-get install python3```
            ```sudo apt-get install python3-tk```
            ```sudo apt-get install python3-pip```
   * Windows: https://www.python.org/downloads/ 

2) Download the source code of Tin-Whistle-Helper in archive format. Unpack to a suitable folder.
  
3) Install pillow and pyscreenshot (For linux replace ```python``` with ```python3```):
   * type ```python -m pip install -U pillow --user```
   * type ```python -m pip install -U pyscreenshot --user```
   
4) You have two options to run Tin-Whistle-Helper:
   * from your file explorer, </br>navigate to the directory where you extracted the zip file and </br>run (double click) ```TWHelper.py```
   * from a dos prompt/linux terminal, </br>navigate to the directory where you extracted the zip file and </br>
   type ```python TWHelper.py``` for windows or ```python3 TWHelper.py``` for linux.

5) If you encounter errors about fluidsynth:
   * Linux: ```apt-get install fluidsynth```
   * Windows: https://github.com/FluidSynth/fluidsynth/releases/tag/v2.2.0 <br>
              (Download, unpack, run setup.py, include in path)
   * ```python -m pip install -U pyFluidSynth --user```


</br>

---



## Manual

### Toolbar
```
[Load ]: Load a tabs file (.tbs or .tb)
[New  ]: Start with clean file and resets beats per minute to 120
[Save ]: Save a tabs file under the name you provide
[<]    : Half number of beats per minute (bpm)
[◀]    : Reduce number of beats per minute by 5
[▶]    : Reduce number of beats per minute by 5
[>]    : Double number of beats per minute 
 ⊠ CO  : Count Off 4 beats after pressing play before starting song
 ⏅     : Sets number of beats for metronome to sound
 ⊠ ♫⚟  : Play the notes of the song
 ⊠ ⮤↴  : Play decorations (experimental)
 ⊠ Low : Play the song one octave lower to resemble a low whistle
[▶]    : Play song from current position of beat cursor
[■]    : If playing, stops song and set beat cursor to starting beat
         If not playing, resets beat cursor to first beat
[▮▮]   : Pause song / Resume song 
[@]    : Unroll repeated parts (needed for linear play)
[⬏]    : Switch from page view (wrapped) to linear view
[⤢]    : Autosize window and zoom level
[↙]    : Reduce zoom level to fit window size
[↗]    : Enlarge window to fit page size
ⴱ / ⴲ : Change zoom level (tab size) of page
(?)    : Show this help
```

### Tab Area

**Mouse - Change View**
```
Left Button     : Set beat cursor to mouse pointer and plays note
Drag / Wheel    : Scroll page
[Ctrl]-Wheel    : Zoom page
Right Button    : Reset page view
```
**Keyboard - Edit Song**
```
Arrow keys      : Move beat cursor and plays note
[Tab]           : Play song from current position of beat cursor
q               : Stop song 
w               : Pause song
r               : Autosize window and zoom level

d,e,f,g,a,b     : Change note to 1st/low-octave d..f#..b
c,D,E,F,G,A,B   : Change note to 2nd/high-octave c#..f#..b
C               : Change note to 3td-octave c#
[Alt]-d,f,g,a,c : Change note to 1st/low-octave d#,f,g#,a#,c
[Alt]-D,F,G,A,C : Change note to 2nd/high-octave d#,f,g#,a#,c
_               : Change note at cursor to rest
1...9           : Change length of note
lt,gt,^,=,@,~   : Add decorator cut ⮤, tap/strike ↴, roll ⮤↴, 
                                slide ⇒, tongue ᳅, vibrato ∿
[Escape]        : Remove decorator
{ , }           : Insert start ┃▏or end │▎for group of notes to repeat
                  Use [Ctrl]/[Alt] for 2x,3x.
[Shift] { , }   : Insert start ┃▏or end │▎after cursor.                  
[Del]           : Remove note or repeat start/end at cursor
[Shift][Del]    : Remove note or repeat start/end after cursor
[Ctrl]-z        : Undo last delete
[Ins]           : Insert note space (rest) before cursor
[Shift][Ins]    : Insert note space (rest) after cursor

[F1]..[F10]     : Change color of tab at beat cursor
[Shift][Fx]     : Change background color of page
[Space],|       : Add space or vertical line
[Backspace]     : Remove space or vertical line if one is found just 
                  before cursor
[Return]        : Break tabs into two lines before cursor
[Shift][Return] : Break tabs into two lines after cursor
[Backspace]     : Join two lines if beat cursor is at first tab of line

p               : Save screenshot of tabs as visible on screen to file  
                  with name of tab file and extension .png
[Shift]-p       : Save screenshot of ALL tabs with name of tab file and 
                  extension .png
```

### Remarks:
```
- When you change a note and the last tab is not a rest, a rest 
  will be appended to ensure you keep enough empty note space 
  to enter new notes.
- Title will be changed when saving the file (to filename)
```

</br>

---

## Tab file format

It is also possible to edit the tbs and tb files directory.
Editing makes some more options available, like multiple texts, 
custom placed and colored. View *tutorial.tb* for 
more instructions.

Example file
```
# tempo in bps
120

# set page color and title text
color: black
back : #FFFFDE

# custom Title, author and a small decoration
text : "Tutorial", 1,1.75, "Times",1.2, "bold"
text : "by NardJ", 1,3.3, "Times",0.4, "normal"
text : "♫", 21,0, "Arial",3, "normal",purple

# tabs
red d d# e f f# g g# a a# b  c c# green D D# E F F# G G# A A# B  C. C# 
blue c.< d.> e.^ f#.= g@ a~ g/ a- b\ 
{2 orange c.  _ d. _. e. f#... | g | a.. }2
``` 
![Figure 2](https://github.com/NardJ/Tin-Whistle-Helper/blob/main/screenshots/Tutorial.png "Screenshot")

---

## Disclaimer

This is an alpha version and for testing purposes only. It is not ready 
for daily use. You will encounter bugs and may loose work.
The functionality of the next version may differ. Tab files you create 
with this version may not load in the next release. 


---

## License

This software is licensed under the Attribution-NonCommercial-ShareAlike 2.0 Generic (CC BY-NC-SA 4.0) license.

You are free to:
* ***Share*** — copy and redistribute the material in any medium or format
* ***Adapt*** — remix, transform, and build upon the material 
    
Under the following terms:
* ***Attribution*** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
* ***NonCommercial*** — You may not use the material for commercial purposes.
* ***ShareAlike*** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original. 

See <a href="https://creativecommons.org/licenses/by-nc-sa/4.0" target="_blank">Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)</a> on Creative Commons for a full description of this license.

