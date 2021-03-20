# Tin-Whistle-Helper
For playing along with scrolling tabs on D Tin whistle / Penny Whistle / Low Whistle.

## Features
- scrolling cursor (vertical red indicator) shows which note/tab to play
- tabs length show note duration 
- indicators above tabs show decorators
<br />  <br />
- add your own tab files
<br />  <br />
- adjustable tempo 
- audible metronome 
- song can be played in background in scale of tin whistle or low whistle

![Figure 1](https://github.com/NardJ/Tin-Whistle-Helper/blob/main/screenshots/MainWindow.png "Screenshot")
 
## Tab file format

### General format
- Lines starting with # are ignored (`# this is a comment`)
- Empty lines are ignored and can be used to separate blocks
- First line should contain number for tempo (beats per minute) (`120`)
- Following lines should contain note (`d,4,^`) or a new color to draw next tabs (`yellow`) 
  
### Note format
A note consists of a note id, the duration in beats and decoration. These should be separated with spaces 
```
   notes:      firstoctave  : c,d,e,f#,g,a,b,
               secondoctave : C,D,E,F#,G,A,B
               rests        : _
               bar separator: [space] or |
   duration:   whole beats .e.g. 1,2,3,4,5,6,7,8
   play style: (see: https://en.wikipedia.org/wiki/Tin_whistle)
               normal       :
               tap/strike   : ^
               cut          : >
               slide        : =
               roll(cut+tap): >^ 
               tonguing     : @
               vibrato      : ~
               join notes in one breath
                              /: start
                              -: continue
                              \: end
```

See tutorial.tbs for an example file using all options.

![Figure 2](https://github.com/NardJ/Tin-Whistle-Helper/blob/main/screenshots/Tutorial.tbs.png "Tutorial.tbs")

```
# tempo in bps
120

# start with some rests to count off
_,1,
_,1,
_,1,
_,1,

# next notes to play
red
d , 1,
e , 1,
f#, 1,
g , 1,
a , 1,
b , 1,
c , 1,

D , 1,
E , 1,
F , 1,
G,  1,
A , 1,
B , 1,
C , 1,

_ , 2, 
green
C , 2,^
D , 2,>
E , 2,>^
F#, 2,=
E , 2,@
F#, 2,~
G , 1,/
A , 1,-
B , 1,\

  , 0, 
blue
c , 1,
d , 1,
e , 1,
f#, 1,

| , 0, 

g , 4,

```

 
