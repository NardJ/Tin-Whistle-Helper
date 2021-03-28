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
 ⊠ Low : Play the song one octave lower to resemble a low whistle
[■]    : If playing, stops song and set beat cursor to starting beat
         If not playing, resets beat cursor to first beat
[▶]    : Play song from current position of beat cursor
[▮▮]   : Pause song / Resume song 
[⬏]    : Switch from page view (wrapped) to linear view
[⤢]    : Autosize window and zoom level
[↙]    : Reduce zoom level to fit window size
[↗]    : Enlarge window to fit page size
ⴱ /ⴲ  : Change zoom level (tab size) of page
(?)    : Show this help
```

### Tab Area

**Mouse - Change View**
```
Left Button : Set beat cursor to mouse pointer and plays note
Drag        : Scroll page
Scroll Wheel: Scroll page
Right Button: Reset page view
```
**Keyboard - Edit Song**
```
Arrow keys  : Move beat cursor and plays note
a...g       : Change (low-octave) note at current cursor 
A...G       : Change (low-octave) note at current cursor
_           : Change note at cursor to rest
1...9       : Change length of note
^,>,=,@,~   : Add decorator tap, cut, slide, tongue, vibrato
[Escape]    : Remove decorator

[Del]       : Remove note at cursor
[Ctrl]-z    : Undo last delete
[Ins]       : Insert note space (rest) before cursor
[Shift][Ins]: Insert note space (rest) after cursor
+           : Append note space (rest) to song if last tab selected

[F1]..[F10] : Change color of tab at beat cursor
[Shift][Fx] : Change background color of page
[Space],|   : Add space or vertical line
[Backspace] : Remove space or vertical line if one is found just 
              before cursor
[Return]    : Break tabs into two lines
[Backspace] : Join two lines if beat cursor is at first tab of line
p           : Save screenshot of tabs as visible on screen using name 
              of tab file with extension .png
```

### Remarks:
```
- 'f' keypress will be translated to f#. Likewise for F
- [Ctrl]-'c' keypress will be translated to c#. Without [ctrl] to c.
- When you change a note and the last tab is not a rest, a rest 
  will be appended to ensure you keep enough empty note space 
  to enter new notes.
- Title will be changed when saving the file (to filename)
```

</br>

---

## Tab file format

It is also possible to edit the tbs and tb files directory.
Editng makes some more options available, like multiple texts, 
custom placed and colored.View tutorial.tb and tutorial.tbs for 
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
red d e f# g a b c c#  green D E F# G A B C#  
blue c.^ d.> e.>^ f#.= g/ a- b\ 
orange c. _ d. _. e. f#... | g | a..
``` 

## Disclaimer

This is an alpha version and for testing purposes only. It is not ready 
for daily use. You will encounter bugs and may loose work.
The functionality of the next version may differ. Tab files you create 
with this version may not load in the next release. 

