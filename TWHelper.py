#!/usr/bin/env python3 

# TEST: Implement abcnotation, possibly as tab format
#       https://abcnotation.com/qtunes#early
#       http://www.nigelgatherer.com/tunes/abc/abc1.html
#       https://abcnotation.com/blog/2010/01/31/how-to-understand-abc-the-basics/

# TODO: should we use repeats if possible (will lengthen rows)
# TODO: reauthor tabs for max 60 or 72 beats
# TODO: finish WIP tunes 

# BUG:  not sure is still present: if play is disabled in songlistWin but song is playing, the new song will also play for remaining duration

# TODO: remove lineair tabs?
# TODO: Check ornaments as played on YT by TeamRecorder https://www.youtube.com/watch?v=vydCZ-HosQc
# TODO: Check if 'delay=delay2beatUpdate(beatUpdate)' serves a purpose in 'def setBeatUpdate()'
# BUG : Repeats in abc (e.g. 55.abc) not processed correctly
# BUG : Sometimes playing lets TWHelper believe we edited.... should we make a play only mode (disabling all editing)? 
# TODO: replace .tb extension with .tab extension

# BUG:  Cannot enter f# in MS Windows

# TODO  README.md > does double click in windows on py file really start
# TODO: Make mobile e.g. using Kivy (https://kivy.org/)
# TODO: Make new linux distributable
# TODO: Make windows installer

# DONE: Toggle key to make cursor advance after new note is entered of stay (added indicator to cursor)
# DONE: play note on entering new / editing existing note
# DONE: using keyboard moving one row below, wil play all notes from 0 to new note instead of only new note under cursor
# DONE: cursor does not reset to beat 0 on load
# DONE: songlistWin is always on top, instead it follows window order of TWHelper itself
# DONE: load from full visible list of all available tb and abc files
#       seperator between abc and tab files
# DONE: load at % of toolbar (so users can set zoom once at startup to accomodate for their screen width) 
# DONE: make vertical ruler at 4*3*5=60 beats? (48/60/72 are dividable by 3 and 4)
# DONE: help/shortcut dock at right like songlist
# DONE: key down does not navigate songlistWin - to getting this to working
# DONE: Click note not only plays flute but also another instrument
#       fixed in def initTabScroll(fromBeat=0) by changing prevCursorPlay=-1 to prevCursorPlay=fromBeat-1
# DONE: printscreen icon
# DONE: tab should also stop/pause play
# DONE: make last part of repeatable section skipable on last repeat
# DONE: Make tongue decorator also play as such
# DONE: Play triplets
#       Implemented with decorator [alt-3] to shorten note 
# DONE: Load abc files
#       Implemented with warnings for unsupported features 
# DONE: if abc repeats across multiple lines remove the line endings between 
# DONE: implemented attribution fields (composer, transcriver) and signature to tab files 
#       to be displayed in footer
# DONE: replace bpm value as first line of tb file with 'bpm:'-field
# DONE: Display tabs/tune with
#       - key
#       - bpm https://www.musictheoryacademy.com/how-to-read-sheet-music/tempo/
#       - time signatures: not needed e.g. 3/4 which denotes that quarter notes gets beat and there are 3 beats per measure
#       Implemented in footer
# DONE: Closure of tune/page / mark last note to play
#       Not needed, footer only below last tab line: 
# DONE: Custom text fields on page right/bottom aligned 
#       by using negative x and y values in tab file 
# DONE: Accents: staccato (. short/detached), tenuto (-, long attached) 
#       iImplemented as decorations
# DONO: hide splash on user action (mouse/key)

# NODO: Ornaments: Should we (be able to) switch between classical symbols for ornaments/decorations and my symbols?
#       https://hellomusictheory.com/learn/ornaments/   (most important ones)
#       https://en.wikipedia.org/wiki/List_of_ornaments (full list)
#       https://www.tradschool.com/en/about-irish-music/ornamentation-in-irish-music/ (tin whistle)
# NODO: Accents: staccato (. short/detached), accent (> hard), marcato (^ stac+acc), tenuto (-, long attached)
#       Can be implemented like decorations    
#       Should both, accent and decoration, be possible for each note?
# NODO: Should we be able to download abc from internet?


# FOR EACH RELEASE
# TODO: pip3 freeze >requirements.txt
# TODO: make packages  
#        1) 'pyinstaller TWHelper.py'       see https://pyinstaller.readthedocs.io/en/stable/usage.html#using-pyinstaller
#        2) copy resources/screenshots/tabs folder to dist folder
#        3) copy libfluidsynth.so.* and libfluidsynth64.dll to dist folder


import traceback
import os
from sys import platform
import re

from datetime import datetime
import time
import copy

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import Message
from pyscreenshot import grab
from PIL import Image

from tooltip import CreateToolTip
import splash

#GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)
tabdir    = os.path.join(scriptdir,"tabs")
abcdir    = os.path.join(scriptdir,"abc")
icondir   = os.path.join(scriptdir,"resources/icons")
sf2dir    = os.path.join(scriptdir,"resources/sf2")
screenshotdir=os.path.join(scriptdir,"screenshots")
helpdir   = os.path.join(scriptdir,"resources")
lastdir   = tabdir
lasttype  = ".tb"

# check for fluidsynth
fluidsynthLoaded=False
fs=None
try:
    import fluidsynth #pip3 install pyFluidSynth
    fluidsynthLoaded=True
    fs=fluidsynth.Synth()
except Exception as e:
    print (f"Error on import fluidsynth:{e}")
    traceback.print_exc()

import helpWin
import infoDialog
import songlistWin

# Show experimental message
expShown=False # works because we only have 1 experimental feature (play decos)
def experimental():
    global expShown
    if expShown: return
    infoDialog.show(win,title= "Experimental",
                        message="This feature is experimental and \nprobably will not work properly.",
                        timeout=2000)
    expShown=True

# Show splash screen on startup
def showSplash():
    # Calc some values to center splash on screen
    mw=win.winfo_width()
    mh=win.winfo_height()
    sw=700
    sh=400
    sx=win.winfo_x()+int((mw-sw)/2)
    sy=win.winfo_y()+int((mh-sh)/2)
    dims=f"{sw}x{sh}+{sx}+{sy}"
    # Show splash
    splash.show(win,"Tin Whistle Helper",
    #"___________________________________________________________________________________\n"+
    #"\n"+
    "Version   : alpha version\n"+
    "Homepage  : https://github.com/NardJ/Tin-Whistle-Helper\n"+
    "License   : Attribution-NonCommercial-ShareAlike 2.0 Generic (CC BY-NC-SA 4.0)\n"+
    "___________________________________________________________________________________\n"+
    "\n"+
    "Made using:\n"+
    "           Python3      (https://www.python.org/downloads/)\n"+
    "           PyScreenshot (https://github.com/ponty/pyscreenshot)\n"+
    "           Pillow       (https://github.com/python-pillow/Pillow)\n"+
    "           PyFluidSynth (https://github.com/nwhitehead/pyfluidsynth)\n"+
    "           FluidSynth   (https://github.com/FluidSynth/fluitsynth)\n"+
    "___________________________________________________________________________________\n"+
    "\n"+
    "Disclaimer: \n"+
    "            This is an alpha version and for testing purposes only.\n"+
    "            It is not ready for daily use. You will encounter bugs and may \n"+ 
    "            loose work. The functionality of the next version may differ.\n"+ 
    "            Tab files created with this version may not load in the next release.",
                 dims,5000)

# vars for fluidsynth
sfFlute=None
sfMetro=None
chnFlute=None
chnMetro=None
# setup fluidsynth with whistle and metro sound
def initPlayer():
    #https://www.fluidsynth.org/api/LoadingSoundfonts.html
    #https://github.com/nwhitehead/pyfluidsynth
    global sfFlute, sfMetro,chnFlute,chnMetro
    # check if fluidsynth could be loaded
    if not fluidsynthLoaded: return
    # select appropriate driver
    if "linux" in platform:
        fs.start(driver="alsa")
    if platform=="win32":
        fs.start(driver="dsound")
    if platform=="darwin":#OS X
        print ("OS X is not yet supported. Please contact me (https://github.com/NardJ/Tin-Whistle-Helper) to add support.")
        quit()

    # load instruments
    #soundfontpath = os.path.join(scriptdir,"SynthThik.sf2")
    soundfontpath = os.path.join(sf2dir,"198-WSA percussion kit.SF2")
    sfMetro = fs.sfload(soundfontpath)
    chnMetro= 1
    fs.program_select(chnMetro, sfMetro, 0, 0)

    soundfontpath = os.path.join(sf2dir,"Tin_Whistle_AIR.sf2")
    sfFlute = fs.sfload(soundfontpath)
    chnFlute= 0
    fs.program_select(chnFlute, sfFlute, 0, 0)

# define notes, decos, seperators which can be used in tabs
octL=5
octM=6
octH=7
noteNrsHigh= {'d':octM*12+2,'d#':octM*12+3,'e':octM*12+4,'f':octM*12+5,'f#':octM*12+6,'g':octM*12+7,'g#':octM*12+8,'a':octM*12+9,'a#':octM*12+10,'b':octM*12+11,'c':octM*12+12,'c#':octM*12+13, 
              'D':octH*12+2,'D#':octH*12+3,'E':octH*12+4,'F':octH*12+5,'F#':octH*12+6,'G':octH*12+7,'G#':octH*12+8,'A':octH*12+9,'A#':octH*12+10,'B':octH*12+11,'C':octH*12+12,'C#':octH*12+13,}
noteNrsLow = {'d':octL*12+2,'d#':octL*12+3,'e':octL*12+4,'f':octL*12+5,'f#':octL*12+6,'g':octL*12+7,'g#':octL*12+8,'a':octL*12+9,'a#':octL*12+10,'b':octL*12+11,'c':octL*12+12,'c#':octL*12+13, 
              'D':octM*12+2,'D#':octM*12+3,'E':octM*12+4,'F':octM*12+5,'F#':octM*12+6,'G':octM*12+7,'G#':octM*12+8,'A':octM*12+9,'A#':octM*12+10,'B':octM*12+11,'C':octM*12+12,'C#':octM*12+13,}
noteNrs    = noteNrsHigh 
oldNoteNr  = 0

noteIDs = ['d','d#','e','f','f#','g','g#','a','a#','b','c','c#','D','D#','E','E#','F','F#','G','G#','A','A#','B','C','C#']
eot     = 'eot'
sepIDs  = ['|',',',eot]
restIDs = ['_']
decoIDs = ['<','^', '>', '=', '@', '~', '\\','/','-','*',':','t']
repID   = 'rep'

# define colors for foreground (tabs and text) and background
colors=['blue', 'purple3', '#00BBED','red','DeepPink3','magenta','orange','gold','brown','green','gray39','black',]
backcolors=['#7BDAFF','#FFC6F4','#CeF1Fd','#ffC0C0','#F7A8Db','#f1Bbf1','#FeE59a','#FFFFDE','#D3B4B4','#A0FdA0','#D4D4D4','#FFFFFF']

# vars to store tabs page
win=None
tabs=[]
title=""
footer=""
textColor='black'
backColor='#FFFFDE'
texts=[]

# file vars for current tabs page 
filename=None
filepath=None

# set some vars needed for drawing tabs
notes={ 'd' :(1,1,1,1,1,1,''),
        'e' :(1,1,1,1,1,0,''),
        'f#':(1,1,1,1,0,0,''),
        'g' :(1,1,1,0,0,0,''),
        'a' :(1,1,0,0,0,0,''), 
        'b' :(1,0,0,0,0,0,''),
        'c#':(0,0,0,0,0,0,''),
        'D' :(0,1,1,1,1,1,'+'),
        'E' :(1,1,1,1,1,0,'+'),
        'F#':(1,1,1,1,0,0,'+'),
        'G' :(1,1,1,0,0,0,'+'),
        'A' :(1,1,0,0,0,0,'+'), 
        'B' :(1,0,0,0,0,0,'+'),
        'C#':(0,1,1,0,0,0,'+'),
        '_' :(0,0,0,0,0,0,''),#rest

        'd#':(1,1,1,1,1,2,''),
        'f' :(1,1,1,1,2,0,''),
        'g#':(1,1,2,0,0,0,''),
        'a#':(1,0,1,1,1,1,''),
        'c' :(0,1,1,0,0,0,''),
        'D#':(1,1,1,1,1,2,'+'),
        'F' :(1,1,1,1,2,0,'+'),
        'G#':(1,1,0,1,1,0,'+'),#not sure if we need harder blow '+'
        'A#':(1,0,1,0,0,0,'+'),#not sure if we need harder blow '+'
        'C' :(2,0,0,0,0,0,''),
        }
minBeatsize=10
maxBeatsize=60
DEFBEATSIZE=16
beatsize=DEFBEATSIZE
barInterval=1.2*beatsize
holeInterval=1.5*beatsize
xOffset=beatsize
yOffset=beatsize
beatCursor=0
titleHeight=40
winDims=[1118+26+15+16,800]
tabDims=[0,0]


# switch between high and low D-whistle octaves
def setLowHigh():
    global noteNrs
    if playing: 
        win.varLow.set(noteNrs==noteNrsLow)
        return
    noteNrs=noteNrsLow if win.varLow.get() else noteNrsHigh

# play a note
normalVol=96
def startNote(noteId):    
    if not fluidsynthLoaded: return
    global oldNoteNr
    if noteId in noteNrs:
        noteNr=noteNrs[noteId]
        fs.noteon(0, noteNr,normalVol)
        oldNoteNr=noteNr
    #print (f"On : {noteId}")

# stop a playing note
def endNote(noteId=None):
    if not fluidsynthLoaded: return    
    noteNr=oldNoteNr if noteId==None else noteNrs[noteId]
    fs.noteoff(0, noteNr)
    #print (f"Off: {noteId}")

# play the metronome tick sound
def startTick():
    if not fluidsynthLoaded: return
    noteNr=12*9+2
    fs.noteoff(1, noteNr)
    fs.noteon(1, noteNr,127)

# destroy fluidsynth instance on closing this program
def closePlayer():
    if not fluidsynthLoaded: return
    fs.delete()

# helper to capatilize each word in title
def capTitle():
    global title
    title=" ".join([word.capitalize() for word in title.split(" ")])

# discard all tabs and start with a new tabs file
def newFile():
    global beatCursor,tabs,bpm,title,backColor,filename
    if len(oldTabs)>0:
        ret=messagebox.askyesno("Discard changes?","You have unsaved changes.\nDiscard and start new file?")
        if ret==False:return
    bpm=120
    win.bpm.set(f"{bpm:3}")
    title="New File"
    filename=f"{title}.tb"
    tabs.clear()
    texts.clear()
    beatCursor=0
    tabColor=colors[2]
    backColor='#FFFFDE'
    beat=0
    for i in range (4):
        tabs.append([beat,'_',1,'','green',beat,0,beat])                        
        beat+=1
    tabs.append([beat,',',0,'','green',beat,0,beat])                        
    beat+=1
    for i  in range (4):
        tabs.append([beat,'_',1,'','green',beat,0,beat])                        
        beat+=1

    win.title(f"Tin Whistle Helper - {title}")
    calcTabDims()
    recalcBeats()
    drawBars(True)

# calc the beat to play the note and to display the note also the col (tabCol), row (tabRow) and linear pos (tabLin)  
def recalcBeats():
    beat,tabRow,tabCol,tabLin=0,0,0,0
    for idx,tab in enumerate(tabs):
        #[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab
        [_,name,dur,style,tabColor,_,_,_]=tab
        #print (f"{idx:2}> ({tabCol},{tabRow}) {tab}")
        tabs[idx]=[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]
        #print (f"{'  '}> {tabs[idx]}")
        #calc new beat, col, row and lin
        if name==eot:
            tabRow+=1
            tabCol=0
        else:
            beat+=dur
            tabCol+=max(1,dur)
            tabLin+=max(1,dur)
   
# return nr rows in this tabs file
def nrTabRows():
    if len(tabs)==0: return 0
    return tabs[-1][6]+1
# return idx of first tab in tabs[] on specified row
def rowStart(rowNr):
    for idx in range(len(tabs)):
        if tabs[idx][6]==rowNr: return idx
# return idx of last tab in tabs[] on specified row
def rowEnd(rowNr):
    for idx in range(len(tabs)-1,-1,-1):
        if tabs[idx][6]==rowNr: return idx
# remove seperators (| or blank space) on row
# which may get introduces on reformatting page (insert or delete row end) we may
def stripSeps():
    #strips all seps at beginning of each row
    for rowNr in range(nrTabRows()):
        firstRowIdx=rowStart(rowNr)
        if firstRowIdx!=None: # if row is present
            firstRowTab=tabs[firstRowIdx]
            if firstRowTab[1] in sepIDs: tabs.pop(firstRowIdx)
    #strips all seps at end of each row
    for rowNr in range(nrTabRows()):
        lastRowIdx=rowEnd(rowNr)
        if lastRowIdx!=None: # if row is present
            lastRowIdx-=1 # last is eot, we want to strip seps just before eot
            lastRowTab=tabs[lastRowIdx]
            if lastRowTab[1] in sepIDs and lastRowTab[1]!=eot: tabs.pop(lastRowIdx)
# return if a repeat symbol if found between two positions in tabs[]
def hasRepeats(fromIdx=0,toIdx=-1):
    if toIdx==-1: toIdx=len(tabs)
    for idx in range(fromIdx,toIdx):
        if tabs[idx][1][0]=='}': return True
    return False
# return (first) repeat start ('{'-symbol) between two positions in tabs[]
def firstRepeat(fromIdx=0,toIdx=-1):
    if toIdx==-1: toIdx=len(tabs)
    for idx in range(fromIdx,toIdx):
        if tabs[idx][1][0]=='{': return idx
# return repeat closure('}'-symbol) between two positions in tabs[]
def getRepeatMatchIdx(fromIdx,toIdx=-1):
    m=tabs[fromIdx][1][0]
    if m=='{':
        if toIdx==-1: toIdx=len(tabs)
        level=1
        for idx in range(fromIdx+1,toIdx):
            if tabs[idx][1][0]=='{': level+=1
            if tabs[idx][1][0]=='}':
                level-=1
                if level==0: return idx
    elif m=='}':
        if toIdx==-1: toIdx=-1
        level=1
        for idx in range(fromIdx-1,toIdx,-1):
            if tabs[idx][1][0]=='}': level+=1
            if tabs[idx][1][0]=='{':
                level-=1
                if level==0: return idx
# unroll repeated section with
def unrollRepeats(fromIdx=0,toIdx=-1):
    global tabs
    if toIdx==-1: toIdx=len(tabs)
    #find first repeat
    startIdx=firstRepeat(fromIdx,toIdx)
    #proceed if repeats found
    if not startIdx: return
    oldTabs.append(copy.deepcopy(tabs))
    endIdx=getRepeatMatchIdx(startIdx,toIdx)
    # first remove all child repeats
    subIdx=firstRepeat(startIdx+1,toIdx)
    #print (f"start:{startIdx} end:{endIdx} sub:{subIdx} {subIdx!=None}")
    while subIdx!=None:
        unrollRepeats(subIdx)
        subIdx=firstRepeat(startIdx+1,toIdx)
    # next unroll repeat
    nrRepeats=int(tabs[startIdx][1][1])
    newTabs=tabs[:startIdx]
    postTabs=tabs[endIdx+1:] if endIdx+1<len(tabs) else []
    unrollTabs=tabs[startIdx+1:endIdx]
    for i in range(nrRepeats):
        newTabs+=unrollTabs
    newTabs+=postTabs
    tabs=newTabs
    # redraw
    recalcBeats()
    drawBars(True)
# return previous tab which has duration / can be played (so note or rest)
def gotoPrevBeat(idx):
    global beatCursor
    if idx>len(tabs):idx=len(tabs)
    pidx=idx
    pdur=0
    beat=beatCursor
    while pdur==0 and idx>0:
        pidx-=1
        beat,_,pdur,_,_,_,_,_=tabs[pidx]
    beatCursor=beat
    return pidx

# load file with extension .tb (internal file format)
def loadFileTab(tfilename=None,tfilepath=None):
    global tabs,bpm,title,footer,filename,filepath
    global textColor,backColor,texts   

    # if we received only filename we build filepath
    if tfilepath==None:
        tfilepath=os.path.join(tabdir,tfilename)        
    if not os.path.isfile(tfilepath): return

    # start fresh tabs page
    tabs.clear()
    initBars()#20)
    tabColor=colors[2]
    backColor='#FFFFDE'
    beat,tabRow,tabCol,tabLin=0,0,0,0 #just placeholders, real values will be calculated after loading by recalcBeats
    #print (f"filename:{filename}|")

    # read file
    filepath=tfilepath
    filename=os.path.basename(tfilepath)
    with open(tfilepath,'r',encoding='utf-8') as reader:
        lines=reader.readlines()

    #remove comments and empty lines
    for idx in range(len(lines)-1,-1,-1):            
        line=lines[idx].strip()
        if len(line)==0: lines=lines[:idx]+lines[idx+1:]
        elif line[0]=='#':lines=lines[:idx]+lines[idx+1:]

    #read bpm
    bpm=120
    try:
        bpm=int(lines[0])
        lines=lines[1:]
        print (f"Old format...bpm {bpm} found on first line")
    except Exception as e:
        print ("Assume new format.")
            
    #process all lines
    signature=""
    transcriber=""
    composer=""
    texts.clear()
    for line in lines:      # go line by line
        line=line.strip()   # remove leading and trailing spaces and eol chars
        if len(line)>0:     # ignore empty lines
            # process metadata of tune
            if ':' in line: # read colors and text to display
                colIdx=line.index(':')
                cmd=line[:colIdx]
                val=line[colIdx+1:]
                #cmd,val=line.split(':')
                cmd=cmd.strip()
                if cmd=='bpm': 
                    bpm=int(val)
                    print (f"New format... bpm {bpm} found.")
                if cmd=="signature"  :signature=val
                if cmd=="transcriber":transcriber=val
                if cmd=="composer"   :composer=val
                vals=val.split(",")
                for idx in range(len(vals)): vals[idx]=vals[idx].strip()
                if cmd=='color': textColor=vals[0]
                if cmd=='back' : backColor=vals[0]
                if cmd=='text' : texts.append(vals)
            
            # process note data of tune
            else:                           
                line=line.replace('   ',' , , ') # tripple space is visual space between tabs
                line=line.replace('  ',' , ')    # double space is visual space between tabs
                while '  ' in line:
                    line=line.replace('  ','')   # more spaces are removed visual space between tabs
                notes=line.split(" ")
                notesfound=False
                firstIdx=len(tabs)
                tabCol=0
                #print (f"line:'{line}\'")
                for note in notes:  
                    if note in colors:         
                        tabColor=note
                    else:   
                        #print (f"note:'{note}'")
                        name=note[0]
                        if len(note)>1: 
                            if note[1]=='#': name+='#'
                        dur=1+note.count('.')
                        style=''
                        if len(note)>1:
                            if note[-1] in decoIDs:#'^>=@~/\\-':
                                style = note[-1] 
                        if name in (noteIDs+restIDs+sepIDs) or name in ('{','}','?'):#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_','|',',']:
                            if name in sepIDs: dur=0 #('|',','): dur=0
                            if name in ('{','}','?'): name,dur=note,0
                            tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])
                            #print (tabs) 
                            notesfound=True
                        else:
                            print (f"Rejected: [{note}] {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
                if notesfound: # ignore lines with only color
                    name=eot
                    dur=0
                    style=''
                    tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
    
    # set title of window, footer
    win.title(f"Tin Whistle Helper - {os.path.basename(tfilepath).split('.')[0]}")
    title=os.path.basename(tfilepath).split('.')[0].replace("_"," ")
    capTitle()
    footer=f"Key: D   BPM: {bpm}"
    if signature: footer+= f"   Signature: {signature}"
    if composer: footer+=  f"   Composer: {composer}"
    if transcriber:footer+=f"   Transcriber: {transcriber}"

    # set bpm
    win.bpm.set(f"{bpm:3}")
    maxMetroMult()
    # calculate play order of tabs and display positions on page
    recalcBeats()
    # calculate size of page
    calcTabDims()

# load file with extension .abc (common text file format for traditional music)
def loadFileABC(tfilename=None,tfilepath=None):
    # Reference Guide to ABC: https://abcnotation.com/wiki/abc:standard:v2.1
    # http://www.lesession.co.uk/abc/abc_notation.htm
    # http://www.lesession.co.uk/abc/abc_notation_part2.htm
    # https://editor.drawthedots.com/
    # http://www.nigelgatherer.com/tunes/abc/abc4.html
    global tabs,bpm,title,filename,filepath,footer
    global textColor,backColor,texts  

    # if we received only filename we build filepath
    if tfilepath==None:
        tfilepath=os.path.join(abcdir,tfilename)        
    if not os.path.isfile(tfilepath): return

    # start fresh tabs page
    tabs.clear()
    texts.clear()
    initBars()#20)
    tabColor=colors[2]
    backColor='#FFFFDE'
    beat,tabRow,tabCol,tabLin=0,0,0,0 #just placeholders, real values will be calculated after loading by recalcBeats

    # read file
    filepath=tfilepath
    filename=os.path.basename(tfilepath)
    
    # set default title
    title=os.path.basename(tfilepath).split('.')[0].replace("_"," ")
    capTitle()

    #read file
    with open(tfilepath,'r',encoding='utf-8') as reader:
        lines=reader.readlines()

    #remove comments and empty lines
    for idx in range(len(lines)-1,-1,-1):            
        line=lines[idx].strip()
        if len(line)==0: lines=lines[:idx]+lines[idx+1:]
        elif line[0]=='%':lines=lines[:idx]+lines[idx+1:]

    #join lines ending in \
    nlines=[]
    currline='\\'
    for line in lines:
        if currline[-1:]=='\\':
            currline=currline[:-1]+line.strip()
        if currline[-1:]!='\\':
            nlines.append(currline)
            currline='\\'
    lines=nlines        

    #split in header and content
    for idx,line in enumerate(lines):
        if line[0:2]=='K:':
            header=lines[:idx+1]
            body=lines[idx+1:]
            exit

    #read header
    headeritems=['X:','T:','C:','L:','M:','K:','R:']
    baseNoteLength=''
    notesForBeat=''
    signature=''
    composer=''
    transcriber=''
    bpm=240
    for line in header:      # go line by line
        line=line.strip()   # remove leading and trailing spaces and eol chars
        colIdx=line.index(':')
        cmd=line[:colIdx]
        val=line[colIdx+1:]
        #cmd,val=line.split(':')
        cmd=cmd.strip()
        val=val.strip()
        # each tune should start with an X: field, followed by a T: field and the header then ends at the K: field.
        if cmd=='X' : pass        # reference number (song part in file)
        if cmd=='T' : title=val   # title of song
        if cmd=='C' : composer=val# composer of song
        if cmd=='Z' : transcriber=val# composer of song
        if cmd=='Q' : 
                      if '/' in val: bpm=240
                      elif '=' in val: bpm=240
                      elif int(val)>60: bpm=int(val)
        if cmd=='L' :             # length of note without elongation or shortening e.g. 'c'  
                      baseNoteLength=int(val[2])
        if cmd=='M' :             # Meter of song e.g. 6/8 or C for common time
                                  # 3/4 denotes that quarter notes gets beat and
                                  # there are 3 beats per measure
                                  # measures are seperated with | 'note' and not automatically
                      if val=='C': val='4/4'
                      if val=='C|': val='2/2'
                      signature=val
                      noteForBeat=int(val[2])
        if cmd=='R' : pass #val  # Rythm of song e.g. Jig,Reel,Waltz
                        #print {"Jig":6/8,"Reel":4/4,"Waltz":3/4}[val]  
        if cmd=='K' :             # Key of song
                    if val!='D':   
                        contImport=tk.messagebox.askokcancel("Wrong key",
                                                    "Tune not of key D. Do you want to ignore and continue import?",
                                                    default='ok',icon='warning')
                        if not contImport:
                            newFile()
                            return
        #ignore rest
        
    #replace / without number by /2
    for idx1,line in enumerate(body):
        ln=len(line)
        idx2=0
        while idx2<ln:
        #for idx2,char in enumerate(line):
            char=line[idx2]
            if char=='/' and line[idx2+1] not in ['0','1','2','3','4','5','6','7','8','9']:
                print (f"oldline:{line}")
                line=line[:idx2+1]+"2"+line[idx2+1:]
                ln+=1
                print (f"newline:{line}")
                body[idx1]=line
            idx2+=1

    #check max divisor to get minimal note length to display
    maxdiv=1
    for line in body:
        for idx,char in enumerate(line):
            if char=='/':
                div=int(line[idx+1])
                if div>maxdiv: maxdiv=div

    # set bpm
    if baseNoteLength!='' and notesForBeat!='':
        bpm=bpm*(baseNoteLength/noteForBeat)
    win.bpm.set(f"{bpm:3}")
    maxMetroMult()
    #win.metromult.set(f"")

    # build footer
    footer=f"Key: D   BPM: {bpm}"
    if signature: footer+= f"   Signature: {signature}"
    if composer: footer+=  f"   Composer: {composer}"
    if transcriber:footer+=f"   Transcriber: {transcriber}"

    #prelimenary refactoring of body
    #0) remove strings between tunes
    nbody=[]
    for line in body:
        l=""
        intext=False
        for c in line:
            if c=='"': intext= not intext
            elif not intext: l+=c
        nbody.append(l)
    body=nbody
    #1) remove line endings between repeated sections 
    #   (for automatic page scrolling repeats should be 1 row)
    nbody=[]
    inrep=False
    l=""
    for line in body:
        o='' # hold previous char
        for c in line:
            if (o+c)=='|:': inrep= True
            if (o+c)==':|': inrep= False
            o=c # store previous char
            l+=c #add prev char to l
        if not inrep: 
            nbody.append(l)
            l=""
    body=nbody
    #2) replace '::' abreviation by ':||:'
    body=[line.replace('::',':| |:') for line in body]
    #3) check for unsupported section indicators e.g. '[1'
    if any('[' in line for line in body):
        contImport=tk.messagebox.askokcancel("Ignore unsupported feature?",
                                  "Repeated sections found. Do you want to ignore and continue import?",
                                  default='ok',icon='warning')
        if contImport:
            body=[re.sub('\[\d','',line) for line in body]
            #print (body)
        else:
            return
    #4) check for unsupported tune property changes and lyrics e.g. Q,L,M,R,K and w:
    nbody=[]
    fndU=False
    for line in body:
        if line[:2] in ['Q:','L:','M:','R:','K:']:
            fndU=True
        else:
            nbody.append(line)
    if fndU:
        contImport=tk.messagebox.askokcancel("Ignore unsupported feature?",
                                    "Mid-tune change of property (Q/L/M/R/K) found. Do you want to ignore and continue import?",
                                    default='ok',icon='warning')
        if contImport:
            body=nbody
        else:
            newFile()
            return
    #5) check for unsupported triplets
    if any('(3' in line for line in body) or any('(2' in line for line in body) or any('(4' in line for line in body):
        contImport=tk.messagebox.askokcancel("Ignore unsupported feature?",
                                  "Duplets/Triplets/Quads found. Do you want to ignore and continue import?",
                                  default='ok',icon='warning')
        if contImport:
            body=[line.replace('(3','') for line in body]
            body=[line.replace('(2','') for line in body]
            body=[line.replace('(4','') for line in body]
        else:
            newFile()
            return
    #6) remove notes between {}
    if any('{' in line for line in body) or any('}' in line for line in body):
        contImport=tk.messagebox.askokcancel("Ignore sub note groups?",
                                  "Ornaments / grace note groups found. Do you want to ignore and continue import?",
                                  default='ok',icon='warning')
        if contImport:
            body=[re.sub('\{.*?\}','',line) for line in body]
        else:
            newFile()
            return
    #7) check for note elongation indicators e.g. '<' and '>'
    if any('<' in line for line in body) or any('>' in line for line in body):
        contImport=tk.messagebox.askokcancel("Ignore unsupported feature?",
                                  "Note elongation/shortening found. Do you want to ignore and continue import?",
                                  default='ok',icon='warning')
        if contImport:
            #body=[line.replace('<','') for line in body]
            #body=[line.replace('>','') for line in body]
            pass # we can now handle this after processing tabs
        else:
            newFile()
            return
    #8) remove lyrics
    nbody=[]
    fndU=False
    for line in body:
        if line[:2] != 'w:':
            nbody.append(line)
    body=nbody
    #9) replace double spaces, ending ']'/'||' and strip leading/trailing spaces and /r/n
    for idx,line in enumerate(body):
        while '  ' in line:
            line=line.replace('  ',' ')
        line=line.replace(']','')
        line=line.replace('||','')
        body[idx]=line.strip()
    #10) replace / without number by /2
    body=[re.sub('/(\D)',r'/2\1',line) for line in body]
    #print ("---")
    #print ("Refactored:")
    #for line in body:
    #    print (body)
    #print ("---")
    #quit()

    #read body/notes
    noteitems=['c','d','e','f','g','a','b','C','D','E','F','G','A','B','z','Z']
    groupitems=['|:',':|','|',':','{','}','?']
    decos=['.'] # . staccato
    preitems=['^', '=', '_','~']+decos
    postitems=['/','1','2','3','4','5','6','7','8', ]
    #no spaces between adjecent pre and note , note and post  
    for line in body:      
        line=line.strip()
        #print (f"{line=}")
        
        # extract valid items from refactored body
        nline=[]
        idx=0
        while idx<len(line):
            fnd=False
            for item in (preitems+noteitems+postitems+groupitems+['>','<']):
                if line[idx:idx+len(item)]==item:
                    nline.append(item)
                    idx+=len(item)
                    fnd=True
                    exit
            if not fnd: idx+=1

        #print (f"{nline=}")
        notes=[]
        # groups items in note groups of note itself,pre and post indicators
        for idx in range(len(nline)):
            if nline[idx] not in (preitems+noteitems+postitems+['>','<']):
                notes.append([nline[idx]])
            #group notes with pre and post items
            if nline[idx] in (noteitems+['>','<']):
                mgroup=[]
                mgroup.append(nline[idx])
                #find start of group
                groupFrom=idx
                for jdx in range(idx-1,-1,-1):
                    if nline[jdx] not in preitems: break
                    mgroup.append(nline[jdx])    
                #find end of group
                groupTo=idx+1
                for jdx in range(idx+1,len(nline)):
                    if nline[jdx] not in postitems: break
                    mgroup.append(nline[jdx])
                notes.append(mgroup)                    
        
        #print (f"{notes=}")
        # replace some info
        for gdx,group in enumerate(notes):
            for idx,note in enumerate(group):
                # replace c and f by c# and f#
                if note in "cCfF":
                    group.append('^') 
                # replace abc notation for sharp/flat by internal indicators
                note=note.replace('^','#')
                note=note.replace('=','')
                if note == '_': return # not supported
                if note.isupper(): 
                    note=note[0].lower()
                elif note.islower() and note!='c': 
                    note=note.upper()
                # replace |: by {2 and :| by }2
                note=note.replace('|:','{2')
                note=note.replace(':|','}2')
                notes[gdx][idx]=note

        # turn note info into tabs
        notesfound=False
        firstIdx=len(tabs)
        tabCol=0
        for notegroup in notes:
            #print (f"note:'{note}'")
            name=notegroup[0]
            if name=='Z': name='_'
            if '#' in notegroup: name=name+'#'
            # make duration
            multdur=1
            for i in range(10):
                if f"{i}" in notegroup:
                    multdur=i
                    break
            if '/' in notegroup: dur=maxdiv/int(multdur)
            else:                dur=maxdiv*int(multdur)    
            if name in groupitems: dur=0
            # decos
            style=''
            if name in decos:
                # ornnaments are not encouraged in abc: http://trillian.mit.edu/~jc/music/abc/ABC-FAQ.html
                # if present they are included as notes and not as ornament type indicators
                pass
            # store notes
            if name=='_':
                #print ('rest')
                pass
            if name in (noteIDs+restIDs+sepIDs) or name[0] in ('{','}','?') or name in ['>','<']:#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_','|',',']:
                tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]) 
                notesfound=True
            else:
                print (f"Rejected: [{note}] {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
        if notesfound: # ignore lines with only color
            name=eot
            dur=0
            style=''
            tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
    
        # process note elongation and shortening '>','<'
        #print (f"{tabs=}")
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
            if name == '<':
                tabs[idx-1][2]=tabs[idx-1][2]/2
                tabs[idx+1][2]=tabs[idx+1][2]*1.5
                tabs.pop(idx)
            if name == '>':
                tabs[idx-1][2]=tabs[idx-1][2]*1.5
                tabs[idx+1][2]=tabs[idx+1][2]/2
                tabs.pop(idx)

        #print (f"{tabs=}")
        #quit()
    # set title
    win.title(f"Tin Whistle Helper - {os.path.basename(tfilepath).split('.')[0]}")

    # calculate play order of tabs and display positions on page
    recalcBeats()
    # calculate size of page
    calcTabDims()

# save file to internal .tb format
def saveFileTab(tfilename=None,tfilepath=None):
    global title,filename,filepath
    if tfilepath==None:
        tfilepath=os.path.join(tabdir,tfilename)        
    if not os.path.isfile(tfilepath): return

    # save tfilepath to global var filename
    filepath=tfilepath
    filename=os.path.basename(tfilepath)
    
    # retreive title from file name
    title=os.path.basename(tfilepath).split('.')[0].replace("_"," ")
    capTitle()
    
    # save tabs page to file 
    drawBars(True)
    eol='\n'
    try:
        with open(tfilepath,'w',encoding='utf-8') as writer:   
            writer.write(f"# {title}{eol}")
            writer.write(f"#   made with TWHelper{eol}")
            writer.write(f"#   see https://github.com/NardJ/Tin-Whistle-Helper{eol}")
            writer.write(f"{eol}")
            writer.write(f"# Beats per Minute (bpm){eol}")
            writer.write(f"bpm  :{bpm}{eol}")
            writer.write(f"{eol}")
            writer.write(f"# Colors{eol}")
            writer.write(f"color:{textColor}{eol}")
            writer.write(f"back :{backColor}{eol}")
            writer.write(f"{eol}")
            writer.write(f"# Text{eol}")
            for text in texts:
                writer.write(f"text:{','.join(text)}{eol}")
            writer.write(f"{eol}")
            currColor=''
            currRow=0
            writer.write(f"# Tabs{eol}")
            for tab in tabs:
                [beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab
                if tabRow!=currRow:
                    writer.write(eol)
                    currRow=tabRow
                if currColor!=tabColor: 
                    writer.write(f"{tabColor} ")
                    currColor=tabColor
                if name in (noteIDs+restIDs):#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_']:
                    nlen=(dur-1)*'.'
                    writer.write(f"{name}{nlen}{style} ")
                    #print(f"{name}{nlen}{style} ;")
                elif name in ['|',',']:
                    if name==',': name=''
                    writer.write(f"{name} ")
                    #print(f"{name} ;")
                elif name[0] in ['{','}','?']:
                    writer.write(f"{name} ")

    except Exception as e:
        print (f"Error writing tab file:{e}")
        traceback.print_exc()

# ask user where to save file and call saveFileTab which really writes data to disc
def saveFile():
    global beatCursor,metroMultIdx, lastdir, lasttype
    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    # only alloww save as tb type, so if of abc type we replace extension 
    cfilename=filename.replace(".abc", ".tb")
    # open filedialog
    rep = filedialog.asksaveasfile(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=lastdir,
                                        initialfile=cfilename,
                                        defaultextension=".tb",
                                        filetypes=[
                                            ("Tin Whistle Tab files", ".tb")
                                    ])
    if (rep==None): return
    #print (f"rep:{rep.name}")
    scriptpath=rep.name                                
    if (scriptpath==None): return

    # store lastdir
    lastdir= os.path.dirname(scriptpath) 

    # call save method
    ext=scriptpath[-3:]
    if ext=='.tb': 
        saveFileTab(tfilepath=scriptpath)
        oldTabs.clear()
    else: return        
    print (f"Saved:{scriptpath}")

# ask user which file to load file and if valid call loadFileTab/loadFileAbc to really read data from disc
def loadFile():
    global beatCursor,metroMultIdx,lastdir,lasttype

    if len(oldTabs)>0:
        ret=messagebox.askyesno("Discard changes?","You have unsaved changes.\nDiscard and load other file?")
        if ret==False:return

    # needed otherwise timer prevents updates of filedialog
    stopTabScroll() 
    
    # ask user for file to load
    rep = filedialog.askopenfilename(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=lastdir,
                                        filetypes=[
                                            ("All files", "*.*"),
                                            ("Tin Whistle Tab files", "*.tb"),
                                            ("ABC Music files", "*.abc"),
                                        ],
                                        )
    # check if user entered filename
    if (len(rep)==0): return
    scriptpath=rep                                   # use first file in list
    if (scriptpath==None): return    

    # store lastdir
    lastdir= os.path.dirname(scriptpath) 
    print (f"{lastdir=}")
    lasttype=scriptpath[-3:]

    # check if file is of valid type/extension
    ext=scriptpath[-3:]
    try:
        if ext=='abc': 
            loadFileABC(tfilepath=scriptpath)
        elif ext=='.tb': 
          loadFileTab(tfilepath=scriptpath)
        else: return
    except Exception as e:
        print (f"Error reading tab file:{e}")
        traceback.print_exc()

    # after load we reset some vars and redraw  
    initBars()
    beatCursor=0
    #win.varZoom.set(100)
    #metroMultIdx=0
    #advMetroMult()
    drawBars(True)

    print (f"Loaded:{scriptpath}")

def loadFromSonglist(scriptpath,autosize,autoload):
    global beatCursor
    ext=scriptpath[-3:]
    try:
        if ext=='abc': 
            loadFileABC(tfilepath=scriptpath)
        elif ext=='.tb': 
          loadFileTab(tfilepath=scriptpath)
        else: return
    except Exception as e:
        print (f"Error reading tab file:{e}")
        traceback.print_exc()

    # stop play
    if autoload:
        stopTabScroll() 

    # reset some vars and redraw  
    initBars()
    beatCursor=0
    #win.varZoom.set(100)
    #metroMultIdx=0
    #advMetroMult()
    drawBars(True)

    if autosize:
        autoBars()

    # start play
    if autoload:
        startTabScroll()

    print (f"Loaded:{scriptpath}")

# calc bounding box of all tabs on page
def calcTabDims():
    global tabDims  
    tabDims=[0,0]
    lin=win.varLinear.get()   

    for tab in tabs:
        beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
        if lin:
            x = (tabLin+dur)*barInterval
        else:
            x = (tabCol+dur)*barInterval
        if lin:
            y = (0+1)*holeInterval*10
        else:
            y = (tabRow+1)*holeInterval*10
        if x>tabDims[0]: tabDims[0]=int(x+0.99999) # poor mans round up
        if y>tabDims[1]: tabDims[1]=int(y+0.99999)

# recalc some drawing vars when resizing page by setting new beatsize 
def initBars(newBeatsize=None):
    global beatsize,barInterval,holeInterval,xOffset,yOffset, beatCursor,titleHeight
    if newBeatsize is not None:
        beatsize=newBeatsize
    barInterval=1.2*beatsize
    holeInterval=1.5*beatsize
    xOffset=beatsize
    yOffset=beatsize
    titleHeight=beatsize*2
    #print (f"initBars:{beatsize} {holeInterval} {yOffset} {titleHeight}")

# return x drawing coordinate of tab column
def col2x(tabCol):
    x=xOffset+tabCol*barInterval
    return x

# return x drawing coordinate of first tab at given beat number
def beat2x(beat):
    fndTab=None
    lin=win.varLinear.get()   
    for tab in tabs:
        [tabBeat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab        
        if (beat>=tabBeat): fndTab=tab
    tabBeat,name,dur,style,tabColor,tabCol,tabRow,tabLin = fndTab
    if lin: # drawing in linear mode
        x=xOffset+tabLin*barInterval
    else:   # drawing in standard page mode with multiple rows
        x=xOffset+tabCol*barInterval
    x=x+(beat-tabBeat)*barInterval
    return x

# return y drawing coordinate of line row on page
def row2y(tabRow):
    y=yOffset+tabRow*holeInterval*10
    return y+titleHeight

# return y drawing coordinate of first tab at given beat number
def beat2y(beat):
    y=0
    lin=win.varLinear.get()   
    for tab in tabs:
        [tabBeat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab        
        if (beat>=tabBeat):
            if lin:
                y=yOffset
            else:    
                y=yOffset+tabRow*holeInterval*10
    return y+titleHeight

# return drawing width given a given duration in beats
def beat2w(dur):
    w=(dur-1)*barInterval+beatsize
    return w

# return drawing height of tabs including decorator above and note name below
def beat2h():
    return holeInterval*9
row2h=beat2h

# draw a bar on page
def drawBar(beat,dur,noteId,noteStyle='',tabColor='blue',tabCol=0,tabRow=0,tabLin=0):
    cvs=win.cvs

    # only draw if visible
    x1=beat2x(beat)
    x2=x1+beat2w(dur)
    y0=beat2y(beat)
    #yt=y0+beat2h()

    #if x2<0 or x1>winDims[0]: return False
    #if yt<0 or y0>winDims[1]: return False
    #print (f"drawBar:{beat,dur,noteId,noteStyle,tabColor,tabCol,tabRow,tabLin}")

    # stop if nothing to draw
    if noteId == '' : return False
    if noteId == ',': return False
    if noteId == eot: return False

    # draw repeat symbols
    if noteId[0] == '?':
        # n | n-1 
        # draw line
        x=col2x(tabCol)+beat2w(1)# xOffset+tabCol*barInterval+beat2w(1)
        y=row2y(tabRow)
        xm=x-beat2w(1)/2
        dashPatt =  (5,3)
        y1=y+holeInterval*0.8
        y2=y+holeInterval*9
        cvs.create_line(xm-2,y1,xm-2,y2,fill=tabColor,width=1,dash=dashPatt) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        # draw text
        x1=col2x(tabCol)+beat2w(1)/2# xOffset+tabCol*barInterval+beat2w(1)
        y=row2y(tabRow)
        y1=y+holeInterval*0.5
        fnt=("*font", int(beatsize*0.5))
        cvs.create_text(x1,y1,text='n | n-1',font=fnt,fill=tabColor)
        return False
    if noteId[0] == '{': 
        tabColor = 'black'
        # lines
        x=col2x(tabCol)+beat2w(1)# xOffset+tabCol*barInterval+beat2w(1)
        y=row2y(tabRow)
        xm=x-beat2w(1)/2
        y1=y+holeInterval*0
        y2=y+holeInterval*0.2
        cvs.create_line(xm-2,y1,xm-2,y2,fill=tabColor,width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm+3,y1,xm+3,y2,fill=tabColor,width=1) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        y1=y+holeInterval*0.8
        y2=y+holeInterval*9
        cvs.create_line(xm-2,y1,xm-2,y2,fill=tabColor,width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm+3,y1,xm+3,y2,fill=tabColor,width=1) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        #for debug
        # nr times to repeat
        x1=col2x(tabCol)+beat2w(1)/2# xOffset+tabCol*barInterval+beat2w(1)
        y1=y+holeInterval*0.5
        fnt=("*font", int(beatsize*0.5))
        cvs.create_text(x1,y1,text=noteId.replace('{',u'\u00D7'),font=fnt,fill=tabColor)
        # return, drawing done
        return False
    if noteId[0] == '}': 
        tabColor = 'black'
        x=col2x(tabCol)+beat2w(1)# xOffset+tabCol*barInterval+beat2w(1)
        y=row2y(tabRow)
        # lines
        tabColor = 'black'
        xm=x-beat2w(1)/2
        y1=y+holeInterval*0
        y2=y+holeInterval*0.2
        cvs.create_line(xm-3,y1,xm-3,y2,fill=tabColor,width=1) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm+2,y1,xm+2,y2,fill=tabColor,width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        y1=y+holeInterval*0.8
        y2=y+holeInterval*9
        cvs.create_line(xm-3,y1,xm-3,y2,fill=tabColor,width=1) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm+2,y1,xm+2,y2,fill=tabColor,width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        # nr times to repeat
        x1=col2x(tabCol)+beat2w(1)/2# xOffset+tabCol*barInterval+beat2w(1)
        y1=y+holeInterval*0.5
        fnt=("*font", int(beatsize*0.5))
        cvs.create_text(x1,y1,text=noteId.replace('}',u'\u00D7'),font=fnt,fill=tabColor)
        # return, drawing done
        return False

    # draw measure sepertor symbols
    if noteId == '|': 
        tabColor = 'black'
        #xm=beat2x( beat)-beat2w(1)/2
        x=col2x(tabCol)+beat2w(1)# xOffset+tabCol*barInterval+beat2w(1)
        y=row2y(tabRow)
        xm=x-beat2w(1)/2
        y1=y+holeInterval*0
        y2=y+holeInterval*9
        cvs.create_line(xm,y1,xm,y2,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        return

    # retreive holes in tab to draw filled (fingers on hole)
    holes=notes[noteId]
 
    # set vars to draw rest different than note
    if noteId    == '_':
        dashPatt =  (1,3)
        linewidth=  3
        #tabColor =  'gray70'
        noteId   =  '' # so no rest is printed
    else:
        dashPatt=None
        linewidth=  1

    # draw tab and color their holes depending on note to play
    for holeNr in range(6):
        openNote=(holes[holeNr]==0)
        closedNote=(holes[holeNr]==1)
        halfNote=(holes[holeNr]==2)
        if (openNote):
            fillColor='white'
            arcstyle=tk.ARC
        if (closedNote):
            fillColor=tabColor
            arcstyle=tk.CHORD
        x1=beat2x(beat)
        x2=x1+beat2w(dur)
        y1=y0+holeInterval*(holeNr+1)
        y2=y0+holeInterval*(holeNr+1)+beatsize 
        ym=(y1+y2)/2
        r=beatsize/2
        if openNote or closedNote:
            cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=180,style=arcstyle,dash=dashPatt,width=linewidth)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill=fillColor,outline=tabColor,start=270,extent=180,style=arcstyle,dash=dashPatt,width=linewidth)
        if openNote:
            cvs.create_line(x1+beatsize/2,y1,x2-beatsize/2,y1,fill=tabColor,dash=dashPatt,width=linewidth) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
            cvs.create_line(x1+beatsize/2,y2,x2-beatsize/2,y2,fill=tabColor,dash=dashPatt,width=linewidth)
        if (closedNote):
            cvs.create_rectangle(x1+beatsize/2,y1,x2-beatsize/2,y2,fill=fillColor,outline=tabColor,dash=dashPatt,width=linewidth) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
        if halfNote:
            cvs.create_arc(x1, y2-beatsize, x1+beatsize, y2,fill=tabColor,outline=tabColor,start=90,extent=90,dash=dashPatt,width=linewidth)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill=tabColor,outline=tabColor,start=0,extent=90,dash=dashPatt,width=linewidth)
            cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill='white',outline=tabColor,start=270,extent=-90,style=tk.ARC,dash=dashPatt,width=linewidth)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill='white',outline=tabColor,start=0,extent=-90,style=tk.ARC,dash=dashPatt,width=linewidth)
            cvs.create_rectangle(x1+beatsize/2,y1,x2-beatsize/2,ym,fill=tabColor,outline=tabColor,dash=dashPatt,width=linewidth) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
            cvs.create_line(x1+beatsize/2,y2,x2-beatsize/2+1,y2,fill=tabColor,dash=dashPatt,width=linewidth) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html

    # if high octave put a plus sign below tab
    highOct=(holes[6])
    if highOct:
        x1=beat2x(beat)
        x2=x1+beat2w(1)
        y1=y0+holeInterval*7
        y2=y0+holeInterval*7+beatsize 
        xm=(x1+x2)/2
        ym=(y1+y2)/2
        cvs.create_line(x1+2,ym,x2-2,ym,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm,y1+2,xm,y2-2,fill=tabColor,width=2)

    # draw decorators
    fnt=("*font", int(beatsize*0.7))
    if noteStyle=='<':# decorator cut ⮤
        w=beat2w(1)
        h=holeInterval/2
        x1=beat2x(beat)#+beat2w(1)/2
        y1=y0+holeInterval*0.25
        x2=x1+w
        y2=y1+h
        xm=x1+w/2
        ym=(y1+y2)/2
        
        cvs.create_line(x1+w*0.25,y2,x1+w*0.75,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.25,y1,x1+w*0.25,y2,fill=tabColor,width=2)
        cvs.create_line(x1,y1+h*0.5,x1+w*0.25,y1,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.5,y1+h*0.5,x1+w*0.25,y1,fill=tabColor,width=2)
          
    if noteStyle=='>':# decorator tap/strike ↴
        w=beat2w(1)
        h=holeInterval/2
        x1=beat2x(beat)+beat2w(1)/8
        y1=y0+holeInterval*0.25
        x2=x1+w
        y2=y1+h
        xm=x1+w/2
        ym=(y1+y2)/2
        
        cvs.create_line(x1,y1,x1+w*0.5,y1,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.5,y1,x1+w*0.5,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.25,y1+h*0.5,x1+w*0.5,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.75,y1+h*0.5,x1+w*0.5,y2,fill=tabColor,width=2)

    if noteStyle=='^':# decorator roll (cut+tap/strike) ⮤↴
        w=beat2w(1)
        h=holeInterval/2
        x1=beat2x(beat)+beat2w(1)/8
        y1=y0+holeInterval*0.25
        x2=x1+w
        y2=y1+h
        xm=x1+w/2
        ym=(y1+y2)/2
        
        cvs.create_line(x1+w*0.25,y2,x1+w*0.75,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.25,y1,x1+w*0.25,y2,fill=tabColor,width=2)
        cvs.create_line(x1,y1+h*0.5,x1+w*0.25,y1,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.5,y1+h*0.5,x1+w*0.25,y1,fill=tabColor,width=2)

        x1=x1+w/2
        x2=x2+w/2
        xm=xm+w/2
        cvs.create_line(x1,y1,x1+w*0.5,y1,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.5,y1,x1+w*0.5,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.25,y1+h*0.5,x1+w*0.5,y2,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.75,y1+h*0.5,x1+w*0.5,y2,fill=tabColor,width=2)

    if noteStyle=='=':# decorator slide ⇒
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21D2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
        #cvs.create_text(x1,y1,text=u'\u27B2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='@':# decorator tonguing ᳅
        w=beat2w(1)
        h=holeInterval/2
        x1=beat2x(beat)+beat2w(1)/8
        y1=y0+holeInterval*0.25
        x2=x1+w
        y2=y1+h
        xm=x1+w/2
        ym=(y1+y2)/2        
        cvs.create_line(x1,ym+h*0.25,x1+w*0.25,ym-h*0.25,fill=tabColor,width=2)
        cvs.create_line(x1,ym-h*0.25,x1+w*0.3,ym-h*0.25,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.50,ym-h*0.25,x1+w*0.75,ym-h*0.25,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.375,ym,x1+w*0.75,ym,fill=tabColor,width=2)
        cvs.create_line(x1+w*0.25,ym+h*0.25,x1+w*0.75,ym+h*0.25,fill=tabColor,width=2)
    if noteStyle=='~':# decorator vibrato ∿
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'o',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle==':':# decorator tenuto - (play notes connected)
        #x1=beat2x(beat)+beat2w(1)/2
        #y1=y0+holeInterval*0.5
        #cvs.create_text(x1,y1,text='-',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
        x1=beat2x(beat)+beat2w(1)/4
        x2=beat2x(beat)+beat2w(1)/4*3
        y1=y0+holeInterval*0.5
        cvs.create_line(x1,y1,x2,y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

    if noteStyle=='*':#  decorator staccato . (play detached)
        x1=beat2x(beat)+beat2w(1)/2-beatsize/4/2
        y1=y0+holeInterval*0.5-beatsize/4/2
        cvs.create_oval(x1, y1, x1+beatsize/4, y1+beatsize/4,fill=tabColor,outline=tabColor,width=1)
    if noteStyle=='/':# decorator join note group left
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=90,style=arcstyle,width=2)
        cvs.create_line(x1+beat2w(1)/2,y1,x1+beat2w(1)/2+beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='\\':# decorator join note group right
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_arc(x2-beatsize, y1, x2, y1+beatsize,fill=fillColor,outline=tabColor,start=0,extent=90,style=arcstyle,width=2)
        cvs.create_line(x2-beat2w(1)/2,y1,x2-beat2w(1)/2-beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='-':# decorator join note group middle
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_line(x1,y1,x2,y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='t':# decorator triplet 3
        x1=beat2x(beat)+beatsize/4
        y1=y0+holeInterval*0.375
        fnt=("*font bold", int(beatsize*0.3))
        cvs.create_text(x1,y1,text='2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
        cvs.create_line(x1+beatsize*0.4,y1-beatsize*0.05,x1-beatsize*0.05,y1+beatsize*0.4,fill=tabColor,width=1) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
        cvs.create_text(x1+beatsize*0.3,y1+beatsize*0.4,text='3',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp

        for gap in range(1,3):
            gapwidth=int(beatsize/4)
            x1=beat2x(beat)+beatsize-gapwidth
            for holeNr in range(6):
                y1=y0+holeInterval*(holeNr+1)
                y2=y0+holeInterval*(holeNr+1)+beatsize 
                cvs.create_rectangle(x1,y1-1,x1+gapwidth,y2+1,fill=backColor,outline=backColor,width=1) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
                cvs.create_line(x1,y1,x1,y2,fill=tabColor,width=linewidth) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html

    # draw note name
    noteId=noteId.replace('#',u'\u266F')
    x1=beat2x(beat)+beat2w(1)/2 # beat2x(beat)+beat2w(dur)/2
    y1=y0+holeInterval*8.5
    fnt=("*font", int(beatsize*0.5))
    cvs.create_text(x1,y1,text=noteId,font=fnt)

    return True

# draw all bars and calling drawBar for each one
cursorBar=None
cursorBar2=None
cursorAutoAdv=None
oldOffsets=[0,0]
oldBeatsize=0
inDrawBars=False
def drawBars(force=False):
    global xOffset,yOffset,cursorBar,cursorBar2,oldOffsets,oldBeatsize,inDrawBars,cursorAutoAdv
    # prevent double draws, which mainly occur on window resize
    if inDrawBars and not force: return
    inDrawBars=True

    # check if bars changed
    if force:
        #print ("full redraw")
        # store offsets
        oldOffsets[0]=xOffset 
        oldOffsets[1]=yOffset 
        oldBeatsize=beatsize

        # clear canvas
        win.cvs.delete("all")

        # resize canvas
        calcTabDims()
        win.cvs.config(scrollregion=(0,0,int(tabDims[0]+beat2x(1)+xOffset),
                                         int(tabDims[1]+beat2y(0)+yOffset)))        
        # redraw page outline
        bBox=pageBBox()
        win.cvs.create_rectangle(bBox[0],bBox[1],bBox[2],bBox[3], fill=backColor)
        # draw vertical 72 beat ruler (72ill fit measures of 3 and measures of 4 beats)
        x72=(col2x(72-1)+beatsize+col2x(72))/2
        if bBox[2]>col2x(72): #only draw if within page
            win.cvs.create_line(x72,bBox[1],x72,bBox[3], fill='#AAAAAA')

        # draw title and other text
        if len(texts)==0: #only display filename as title if no texts were given in the file
            x1=beat2x(0)
            y1=beat2y(0)
            win.cvs.create_text(x1,y1-titleHeight+beatsize*0.75,anchor=tk.W, font=("*font", int(beatsize*1.2), "bold"),text=title,fill=textColor)
        else:
            for idx,textCmd in enumerate(texts):
                if len(textCmd)>=6:                    
                    if len(textCmd)==6: 
                        text,x,y,fName,fSize,fStyle=textCmd
                        fillColor=textColor
                    if len(textCmd)==7: text,x,y,fName,fSize,fStyle,fillColor=textCmd
                    text=text[1:-1]     # remove leading and trailing "
                    fName=fName[1:-1]   # remove leading and trailing "
                    fStyle=fStyle[1:-1] # remove leading and trailing "
                    x1=int(beatsize*(float(x)))
                    y1=int(beatsize*(float(y)))
                    if x1<0:
                        print (f"{x1}+{bBox[2]}={bBox[2]+x1}") 
                        x1=bBox[2]+x1
                    if y1<0: y1=bBox[3]+y1
                    fSize=float(fSize)
                    win.cvs.create_text(x1,y1-titleHeight+beatsize*0.75,anchor="nw", font=(fName, int(beatsize*fSize), fStyle),text=text,fill=fillColor)
                    y2=int(y1-titleHeight+beatsize*0.75)
        #t1=time.time()

        # redraw tabs
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            drawBar(beat,dur,name,style,tabColor,tabCol,tabRow,tabLin)
        win.cvs.update()  
        win.update_idletasks()      
        #print (f"elaps:{time.time()-t1:2}")

        #print (f"nrDrawn:{nrDrawn}")

        # draw footer (key and bpm)
        x1=bBox[0]+beatsize*0.3#beat2x(0)
        y1=bBox[3]#-beatsize*1
        fontsize=int(beatsize*0.5)
        win.cvs.create_text(x1,y1-fontsize,anchor=tk.W, font=("*font", fontsize, "italic bold"),text=footer,fill='#AAAAAA')#=textColor)
        #win.cvs.create_line(bBox[0],y1-fontsize*2.4,bBox[2],y1-fontsize*2.4,fill='#AAAAAA',width=1) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

    # draw cursor
    w=0
    for tab in tabs:
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatCursor>=beat and beatCursor<=(beat+dur): w=beat2w(dur)
    x=beat2x(beatCursor)
    y=beat2y(beatCursor)
    h=beat2h()
    #print (f"{x}:{cursorBar}")
    if (cursorBar) : win.cvs.delete(cursorBar)
    if (cursorBar2): win.cvs.delete(cursorBar2)
    if (cursorAutoAdv): win.cvs.delete(cursorAutoAdv)
    if not playing:
        dashPatt=(1,2)
        cursorBar2=win.cvs.create_rectangle(x+1,y,x+w,y+h,width=1,outline='red',dash=dashPatt) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    cursorBar=win.cvs.create_line(x,y,x,y+h,fill='red',width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if autoAdvance and not playing:
        cursorAutoAdv=[]
        stepsize=beatsize/3
        dx=w % (int(stepsize)) # offset to make sure last line ends precisely at right of cursor 
        dy=int(beatsize/3)
        cursorAutoAdv=win.cvs.create_line(x+w,y-stepsize-dy,x+w+stepsize,y-dy,x+w,y+stepsize-dy, width=2,fill='red')
 
    # check if we need to scroll (window should have room for minimal 2 rows)
    if playing and nrRepeats<=1: # only scroll on last repeat
        linMode=win.varLinear.get()   
        if linMode==True:
            x = beat2x(beatCursor)
            cvsW=int(win.cvs.winfo_width())
            if x>cvsW/2:
                relX=(x-cvsW/2)/tabDims[0]
                win.cvs.xview_moveto(relX)
        else:
            #  active row    
            actRow=-1
            for tab in tabs:
                beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
                if beatCursor>=beat and beatCursor<=(beat+dur):actRow=tabRow
            #  nr of beats on this row        
            fromBeat,toBeat=-1,-1
            for tab in tabs:
                beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
                if tabRow==actRow: 
                    if fromBeat==-1: fromBeat=beat
                    toBeat=beat+dur
            nrBeats=toBeat-fromBeat
            #  calc scroll fraction
            if actRow>0:
                beatNr=beatCursor-fromBeat
                relBeat=beatNr/nrBeats
                rowHeight=beat2h()/tabDims[1]
                relY=(actRow-1+relBeat)*rowHeight
                win.cvs.yview_moveto(relY)

    # set inDrawBars to False
    inDrawBars=False

# start note at current tab cursor
noteSilence=100 #msec
nrRepeats=0
repeatStart=0
repeatStartIdx=0
prevCursorPlay=-1
def doCursorPlay():
    #print ("doCursorplay")
    global nrRepeats,repeatStart,beatCursor,repeatStartIdx,prevCursorPlay

    # check if we also need to play a tick
    if metroMultIdx>0:
        metroInterval=2**(metroMultIdx-1)
        if (beatCursor%metroInterval)==0: startTick()

    #
    if not win.varSound.get(): 
        endNote()
        return

    # check if we are starting new tab with repeat or new line
    if playing and int(beatCursor)==round(beatCursor,2):
        #print (f"beat:{int(beatCursor)}")
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
            if beat>prevCursorPlay and beat<=round(beatCursor,2):
                if name[0]=='{':
                    repeatStart=beatCursor
                    repeatStartIdx=idx
                    nrRepeats=int(name[1])
                    #print (f"{{ {beat}")
                if name[0]=='}':# and idx>repeatStartIdx:
                    #print (f"}} {beat}")
                    if nrRepeats>1:
                        beatCursor=repeatStart
                        prevCursorPlay=repeatStart-1
                        nrRepeats-=1
                    else:
                        nrRepeats=0
                        repeatStart=0
                        repeatStartIdx=0
                if name[0]=='?':
                    if nrRepeats==1:     # if last repeat ... 
                        while name[0]!='}' and idx<len(tabs): # we skip following notes until }
                            beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tabs[idx]
                            beatCursor=beat
                            prevCursorPlay=beatCursor-1
                            idx+=1

    # play note
    #print ("----")
    #print (f"{prevCursorPlay}-{beatCursor}")
    for tab in tabs:
        beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
        #print (f"{beatCursor=} vs {beat=} in {tab=}")
        if beat>prevCursorPlay and beat<=round(beatCursor,2):
            if name in noteIDs:#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G']:
                #print (f"play {tab=} {prevCursorPlay=} {beatCursor=}")
                startNote(name)                
                delay=dur*int(60/bpm*1000)
                noteLength=delay-noteSilence if (noteSilence<delay) else delay
                endTimer=win.after(int(noteLength),endNote,name)
                # decorator 3 is played always, even if deco control is not checked
                if style=="t":#play note as part of third note set (length = 2/3 beat)
                    # make note stop sooner
                    win.after_cancel(endTimer)
                    delay=int(2/3*dur*(60/bpm*1000))
                    noteLength=delay-noteSilence if (noteSilence<delay) else delay
                    endTimer=win.after(int(noteLength),endNote,name)
                    # play next note faster
                    beatCursor+=.3333333 # more than one decimal causes consequetive notes to not play
                # play other decos only if deco control is checked
                if win.varDeco.get():
                    if style=="@":#use tongue emulate with double note where first is very short and harder
                        fs.cc(0,7,127)#11 expression
                        win.after(100,fs.cc,0,7,normalVol)
                        win.after(noteLength,endNote,name)
                    if style==">":#strike/tap one note higher
                        # https://www.tradschool.com/en/about-irish-music/ornamentation-in-irish-music/
                        #https://www.youtube.com/watch?v=4JemxBMeZ3g
                        strikeNotes={'c#':'b','b':'a','a':'g','g':'f#','f#':'e','e':'d','d':'C#', 
                                     'C#':'B','B':'A','A':'G','G':'F#','F#':'E','E':'D','D':'C#'}
                        #noteIdx=noteIDs.index(name)
                        #strikeName=noteIDs[noteIdx+2] # full note higher is 2 halves/indices above
                        strikeName=strikeNotes[name]
                        strikeLength=70#200 # msec
                        if noteLength<400:strikeLength=70
                        if noteLength<200:strikeLength=50
                        if noteLength<100:strikeLength=0  
                        if strikeLength>0:
                            strikeStart=int((noteLength-strikeLength)/2)
                            #print (f"noteLength:{noteLength} strikeStart:{strikeStart} strikeLength:{strikeLength} ")              
                            win.after(strikeStart,endNote,name)
                            win.after(strikeStart,startNote,strikeName)
                            win.after(strikeStart+strikeLength,endNote,strikeName)
                            win.after(strikeStart+strikeLength,startNote,name)
                            win.after(noteLength,endNote,name)
                    if style=="<":#cut:lift finger on g for d/e/f and b for g/a/b see: https://learntinwhistle.com/lessons/tin-whistle-cuts/                        
                        # https://www.tradschool.com/en/about-irish-music/ornamentation-in-irish-music/
                        #https://www.youtube.com/watch?v=QXVSNLtD6AI
                        if name[0] in 'c':cutName='_'
                        if name[0] in 'def':cutName='a'
                        if name[0] in 'DEF':cutName='A'
                        if name[0] in 'gab':cutName='c#'
                        if name[0] in 'GAB':cutName='C#'
                        cutLength=70#200 # msec
                        if noteLength<400:cutLength=70
                        if noteLength<200:cutLength=50
                        if noteLength<100:cutLength=0  
                        if cutLength>0:
                            cutStart=int((noteLength-cutLength)/2)
                            #print (f"noteLength:{noteLength} strikeStart:{strikeStart} strikeLength:{strikeLength} ")              
                            win.after(cutStart,endNote,name)
                            if cutName!='_':
                                win.after(cutStart,startNote,cutName)
                                win.after(cutStart+cutLength,endNote,cutName)
                            win.after(cutStart+cutLength,startNote,name)

                        win.after(noteLength,endNote,name)
                    '''
                    if style=="<":#cut:lift finger on g for d/e/f and b for g/a/b, effect is interuption of note without stopping breath
                        cutLength=noteSilence # msec
                        if cutLength>(noteLength/2): cutLength=noteLength/3
                        if cutLength<50:cutLength=0  
                        if cutLength>0:
                            cutStart=int((noteLength-cutLength)/2)
                            #print (f"noteLength:{noteLength} cutStart:{cutStart} cutLength:{cutLength} ")              
                            win.after(cutStart,endNote,name)
                            win.after(cutStart+cutLength,startNote,name)
                    '''
                    if style=="^":#roll (cut+tap):
                        # https://www.tradschool.com/en/about-irish-music/ornamentation-in-irish-music/
                        # split note in two halves and apply cut and tap to both
                        noteLength1=int(noteLength/2)
                        if name[0] in 'c':cutName='_'
                        if name[0] in 'def':cutName='a'
                        if name[0] in 'DEF':cutName='A'
                        if name[0] in 'gab':cutName='c#'
                        if name[0] in 'GAB':cutName='C#'
                        cutLength=70#200 # msec
                        if noteLength<400:cutLength=70
                        if noteLength<200:cutLength=50
                        if noteLength<100:cutLength=0  
                        if cutLength>0:
                            cutStart=int((noteLength1-cutLength)/2)
                            #print (f"noteLength:{noteLength} strikeStart:{strikeStart} strikeLength:{strikeLength} ")              
                            win.after(cutStart,endNote,name)
                            if cutName!='_':
                                win.after(cutStart,startNote,cutName)
                                win.after(cutStart+cutLength,endNote,cutName)
                            win.after(cutStart+cutLength,startNote,name)

                        noteLength2=noteLength-noteLength1
                        
                        strikeNotes={'c#':'b','b':'a','a':'g','g':'f#','f#':'e','e':'d','d':'C#', 
                                     'C#':'B','B':'A','A':'G','G':'F#','F#':'E','E':'D','D':'C#'}
                        #noteIdx=noteIDs.index(name)
                        #strikeName=noteIDs[noteIdx+2] # full note higher is 2 halves/indices above
                        strikeName=strikeNotes[name]
                        strikeLength=200 # msec
                        if noteLength1<400:strikeLength=100
                        if noteLength1<200:strikeLength=50
                        if noteLength1<100:strikeLength=0  
                        if strikeLength>0:
                            strikeStart=int((noteLength2-strikeLength)/2)
                            #print (f"noteLength:{noteLength} strikeStart:{strikeStart} strikeLength:{strikeLength} ")              
                            win.after(noteLength1+strikeStart,endNote,name)
                            win.after(noteLength1+strikeStart,startNote,strikeName)
                            win.after(noteLength1+strikeStart+strikeLength,endNote,strikeName)
                            win.after(noteLength1+strikeStart+strikeLength,startNote,name)

                        win.after(noteLength,endNote,name)

                    '''
                    if style=="^":#roll (cut+tap):
                        # split note in two halves and apply cut and tap to both
                        noteLength1=int(noteLength/2)
                        noteIdx=noteIDs.index(name)
                        strikeName=noteIDs[noteIdx+1]
                        strikeLength=200 # msec
                        if noteLength1<400:strikeLength=100
                        if noteLength1<200:strikeLength=50
                        if noteLength1<100:strikeLength=0  
                        if strikeLength>0:
                            strikeStart=int((noteLength1-strikeLength)/2)
                            #print (f"noteLength:{noteLength} strikeStart:{strikeStart} strikeLength:{strikeLength} ")              
                            win.after(strikeStart,endNote,name)
                            win.after(strikeStart,startNote,strikeName)
                            win.after(strikeStart+strikeLength,endNote,strikeName)
                            win.after(strikeStart+strikeLength,startNote,name)

                        noteLength2=noteLength-noteLength1
                        cutLength=noteSilence # msec
                        if cutLength>(noteLength2/2): cutLength=noteLength2/3
                        if cutLength<50:cutLength=0  
                        if cutLength>0:
                            cutStart=int((noteLength2-cutLength)/2)
                            #print (f"noteLength:{noteLength} cutStart:{noteLength1+cutStart} cutLength:{cutLength} ")              
                            win.after(noteLength1+cutStart,endNote,name)
                            win.after(noteLength1+cutStart+cutLength,startNote,name)
                    '''

                    if style=="=":#slide: from note -> note +half -> note above
                        # https://www.youtube.com/watch?v=oF47eHR01-k
                        # slide is not linear, fix!
                        slideSemitones={'c#':0,'b':3,'a':2,'g':2,'f#':1,'e':3,'d':2, 
                                      'C#':0,'B':3,'A':2,'G':2,'F#':1,'E':3,'D':2}
                        slideAmount=slideSemitones[name]
                        win.after(noteLength,endNote,name)
                        pitchBend(2048*slideAmount,noteLength,0.6,0.8)
                        

                    if style=="@":#tongue
                        pass
                    if style=="~":#vibrato
                        win.after(noteLength,endNote,name)
                        vibrato(name,noteLength)
                    if style=="*":#staccato (short note)
                        delay=dur*int(60/bpm*1000)
                        noteLength=int(delay/2) 
                        win.after(noteLength,endNote,name)
                    if style==":":#tenuto (long note)
                        noteLength=delay
                        win.after(noteLength,endNote,name)

    # store from where we played, so we can play next time from here on
    prevCursorPlay=round(beatCursor,2)

# modify pitch of played note 
pitchVal=0
totBendDur=0
def pitchBend(amount,duration,bendFromPerc=0,bendToPerc=1,restart=True):
    global pitchVal,totBendDur
    if not fluidsynthLoaded: return
    if restart: 
        pitchVal=0
        totBendDur=0
        #print ("---")
        #print (f"Amount    :{amount}")
        #print (f"Duration  :{duration}")
        #print (f"Bend range:{bendFromPerc}-{bendToPerc}")
    bendFrom     = bendFromPerc*duration
    bendTo       = bendToPerc*duration 
    bendDuration = (bendToPerc-bendFromPerc)*duration

    fs.pitch_bend(chnFlute,pitchVal*2) # 2048 1 semitone / half noteId
    #print (f"{totBendDur}:{pitchVal}")

    stepDur=10 # msecs
    nrSteps=int(bendDuration/stepDur)
    stepAmount=int(amount/nrSteps)
    if totBendDur>bendFrom:
        if pitchVal<amount: 
            pitchVal+=stepAmount
        else:
            pitchVal=amount 
    totBendDur+=stepDur
    #print (f"duration:{duration} stepDur:{stepDur} nrSteps:{nrSteps} stepAmount:{stepAmount} pitchVal:{pitchVal}")
    
    #if pitchVal<amount: 
    if totBendDur<duration:
        win.after(stepDur,pitchBend,amount,duration,bendFromPerc,bendToPerc,False)
    else:
        fs.pitch_bend(chnFlute,0)          # 2048 1 semitone / half noteId

# simulate vibrato by stopping and restarting played note repeatedly 
vibStart=0
vibState=2
def vibrato(noteName,duration,restart=True):
    global vibState,vibStart
    if not fluidsynthLoaded: return
    if restart:
        vibStart=time.time()        

    vibPulseWidth=6 # msecs
    if vibState==0:endNote(noteName)                
    if vibState==1:startNote(noteName)
    vibState=(vibState+1) % 10

    vibPassed=time.time()-vibStart
    vibPassed=vibPassed*1000
    if vibPassed<duration:
        win.after(vibPulseWidth,vibrato,noteName,duration,False)
    else:
        endNote(noteName)                
        vibState=2

bpm=120
beatUpdate=0.1
playing=False
startTime=0
delayJob=None
firstPlayBeat=0

# set vars to start scrolling of cursor
def initTabScroll(fromBeat=0):
    global beatCursor,prevCursorPlay
    beatCursor=fromBeat
    prevCursorPlay=fromBeat-1
    win.beatCursor.set(f"{beatCursor:.1f}")
    setBeatUpdate()
    delay=int((60/bpm*1000)*beatUpdate)
    #print (f"initTabScroll {prevCursorPlay=}")

def forceFocus():
    # Does not always work
    if winSonglist:
        winSonglist.after(1,lambda:winSonglist.treeview.focus_force())  
    else:
        win.after(1,lambda:win.cvs.focus_force())    
# start scrolling of cursor
def startTabScroll():
    nrBarLines=barLinesFullyVisible()#(win.cvs.winfo_height())/beat2h()
    if win.varLinear.get():
        if nrBarLines<1:
            messagebox.showinfo("Cannot play","In linear mode the full bar height should be fully visible.\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            forceFocus()
            return
        #check if one row on screen
    else:        
        if nrBarLines<2 :
            messagebox.showinfo("Cannot play","In page mode, at least to bar lines should be fully visible.\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            forceFocus()
            return
        if win.cvs.winfo_width()<tabDims[0]:
            messagebox.showinfo("Cannot play","In page mode, the window-width should accomodate all bars\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            forceFocus()
            return
    global playing, beatCursor,delayJob, beatUpdate,xOffset,yOffset
    if playing: # restart from original
        initBars(beatsize) # don't reset zoom
        return    
    initTabScroll(firstPlayBeat)
    initBars(beatsize) # don't reset zoom
    playing=True

    # disable all controls/buttons in footer which cannot be used when playing
    widgets=[win.btnLoad, win.btnNew,win.btnSave,
            win.btnSlower,win.btn2xSlower,win.btnFaster,win.btn2xFaster,
            win.cbCountOff,win.cbLow,win.cbDeco,win.lbMetroMult,win.imMetro,win.cbSound,
            win.cbLinear,win.btnUnroll,win.btnAuto4Bars,win.btnShrink4Bars,win.btnGrow4Bars,win.btnZoomOut,win.btnZoomIn,win.btnHelp]
    for widget in widgets: widget.config(state=tk.DISABLED)
    #resetView(None)
    win.cvs.yview_moveto(0)
    drawBars()
    countOff()
    #doCursorPlay()
    #delayJob=win.after(delay, advTabScroll)

# stop scrolling of cursor 
def stopTabScroll():
    global playing,beatCursor,firstPlayBeat,prevCursorPlay
    if not playing:
        firstPlayBeat=0
    #print ("stopTabScroll")
    prevCursorPlay=firstPlayBeat               
    beatCursor=firstPlayBeat
    endNote()
    playing=False

    # enable all controls/buttons in footer which cannot be used when playing
    widgets=[win.btnLoad, win.btnNew,win.btnSave,
            win.btnSlower,win.btn2xSlower,win.btnFaster,win.btn2xFaster,
            win.cbCountOff,win.cbLow,win.cbDeco,win.lbMetroMult,win.imMetro,win.cbSound,
            win.cbLinear,win.btnUnroll,win.btnAuto4Bars,win.btnShrink4Bars,win.btnGrow4Bars,win.btnZoomOut,win.btnZoomIn,win.btnHelp]
    for widget in widgets: widget.config(state=tk.NORMAL)
    
    # bring top left of page in view
    win.cvs.xview_moveto(0)    
    win.cvs.yview_moveto(0)    
    drawBars()

# pause scrolling of cursor
def pauseTabScroll():
    global beatUpdate,delayJob
    if delayJob is None:
        delayJob=win.after(0, advTabScroll)
        doCursorPlay()
    else:
        win.after_cancel(delayJob)
        delayJob=None
        endNote()

# advance cursor by fraction of beat and repeatedly call this function again after some time has passed
def advTabScroll():
    global beatCursor,delayJob
    if playing:
        lastTab=tabs[-1]
        lastBeat=lastTab[0]+lastTab[2]
        if beatCursor>lastBeat:
            # remove incremented beatCursor for which no note is present
            beatCursor-=beatUpdate 
            beatCursor=round(beatCursor,2)
            win.beatCursor.set(f"{beatCursor:>5.1f}")
            # stop play
            stopTabScroll()
        else:
            delay=int((60/bpm*1000)*beatUpdate)
            delayJob=win.after(delay, advTabScroll)
            beatCursor+=beatUpdate
            beatCursor=round(beatCursor,2)
            win.beatCursor.set(f"{beatCursor:>5.1f}")
            doCursorPlay()
            drawBars()

# return 
def delay2beatUpdate(delay):
    return int((60/bpm*1000)*beatUpdate)
# set delay between each update of cursor
def setBeatUpdate():
    global beatUpdate
    beatUpdate=0.1
    delay=delay2beatUpdate(beatUpdate)
    res=35
    if delay<res: 
        beatUpdate=0.25
        delay=delay2beatUpdate(beatUpdate)
    if delay<res: 
        beatUpdate=0.5
        delay=delay2beatUpdate(beatUpdate)
    if delay<res: 
        beatUpdate=1.0
        delay=delay2beatUpdate(beatUpdate)

# use metro to do a 4-tick countoff before starting play of tune
countOffNr=0
def countOff(init=True):
    global countOffNr
    if init:                      countOffNr=0
    if not win.varCountOff.get(): countOffNr=4
    if countOffNr<4:
        startTick()
        countOffNr+=1
        print (f"{countOffNr}")
        delay=int(60/bpm*1000)
        delayJob=win.after(delay, lambda:countOff(False))
    else:
        doCursorPlay()
        delay=int((60/bpm*1000)*beatUpdate)
        delayJob=win.after(delay, advTabScroll)

# reduce beats per minute by 5 BPM
def decreaseBPM():
    if playing: return
    global bpm
    bpm=bpm-5
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3}")
# reduce beats per minute by 50%
def decrease2xBPM():
    if playing: return
    global bpm
    bpm=int(bpm/2)
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3}")
# increase beats per minute by 5 BPM
def fasterBPM():
    if playing: return
    global bpm
    bpm=bpm+5
    if bpm>960: bpm=960
    win.bpm.set(f"{bpm:3}")
    maxMetroMult()
# increase beats per minute by 200%
def faster2xBPM():
    if playing: return
    global bpm
    bpm=int(bpm*2)
    if bpm>960: bpm=960
    win.bpm.set(f"{bpm:3}")
    maxMetroMult()

drag_begin=0
drag_start=None
scroll_start=0
# store start position (x,y and scroll) and time of drag
def drag_enter(event):
    global drag_begin,drag_start,scroll_start
    drag_begin=[event.x,event.y]
    drag_start=time.time()

    linMode=win.varLinear.get()   
    if linMode==True:
        scroll_start=win.hbar.get()
    else:
        scroll_start=win.vbar.get()
# move scrollbars and thus page when dragging
def drag_handler(event):
    global drag_begin
    drawDistance=( (event.x-drag_begin[0]),(event.y-drag_begin[1]) )
    cw,ch=win.cvs.winfo_width(),win.cvs.winfo_height()

    linMode=win.varLinear.get()   
    if linMode==True:
        hScrollSize=scroll_start[1]-scroll_start[0]
        hScrollOffset=scroll_start[0]-drawDistance[0]/ch
        if hScrollOffset<0: hScrollOffset=0
        if hScrollOffset>(1-hScrollSize): hScrollOffset=(1-hScrollSize)
        win.cvs.xview_moveto(hScrollOffset)
    else:
        vScrollSize=scroll_start[1]-scroll_start[0]
        vScrollOffset=scroll_start[0]-drawDistance[1]/ch
        if vScrollOffset<0: vScrollOffset=0
        if vScrollOffset>(1-vScrollSize): vScrollOffset=(1-vScrollSize)
        win.cvs.yview_moveto(vScrollOffset)
# if drag ends very fast we register this as mouse click
def drag_end(event):
    if not drag_start: return
    if (time.time()-drag_start)<0.2: 
        click(event)
        return

# change beatsize and redraw page
def setBeatSize():
    global beatsize
    beatsize=int(win.varZoom.get()/100*DEFBEATSIZE)
    initBars(beatsize)
    calcTabDims()
    drawBars(True)  

zooms=[25,40,50,67,75,85,100,150,200,250,400]
# set zoom control
def setZoom():
    win.varZoom.set(int(100*(beatsize/DEFBEATSIZE)+0.5))
# move to next zoom percentge and recalc setBeatSize and thus redraw page 
def zoomIn():
    zIdx=zooms.index(win.varZoom.get())
    zIdx+=1
    if zIdx>=len(zooms): zIdx=len(zooms)-1
    win.varZoom.set(zooms[zIdx])        
    setBeatSize()
# move to previous zoom percentge and recalc setBeatSize and thus redraw page 
def zoomOut():
    zIdx=zooms.index(win.varZoom.get())
    zIdx-=1
    if zIdx<0: zIdx=0
    win.varZoom.set(zooms[zIdx])
    setBeatSize()
# zoom with scrollwheel calling upon zoomIn and zoomOut depending on scroll direction
def scrollwheel(event):
    if event.state==0:
        s=win.vbar.get()[0]
        d=-0.1 if event.num==4 else 0.1
        win.cvs.yview_moveto(s+d)
        #print (f"scroll:{win.vbar.get()} {win.vbar.get()[0]*tabDims[1]}")
    if event.state==4: # with control
        if event.num==4: zoomOut()
        if event.num==5: zoomIn()

# scroll page to specific row 
def scroll2Row(row):
    rowHeight=beat2h()/tabDims[1]
    relY=row*rowHeight
    win.cvs.yview_moveto(relY)

# make sure cursor is visible and scroll if necessary 
#selector=None
def keepBeatVisible(beatN=-1):
    if beatN==-1: beatN=beatCursor
    for tab in tabs:
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatN>=beat and beatN<=(beat+dur):
            #print (f"beatN:{beatN} tab:{tab}")
            y=row2y(tabRow)
            h=row2h()
            minY=win.cvs.canvasy(0) # converts mouse event coordinate to canvas coordinate
            maxY=win.cvs.canvasy(win.cvs.winfo_height())
            #print (f"  drawY:{y,y+h}")
            #print (f"  visible:{minY,maxY}")
            if y<minY or (y+h)>maxY: scroll2Row(tabRow)                    

# put cursor at clicked tab and play selected note    
def click(event):
    global beatCursor,firstPlayBeat#,selector
    eventX,eventY=event.x,event.y+win.vbar.get()[0]*tabDims[1]
    #win.cvs.delete(selector)
    eventX=win.cvs.canvasx(event.x)
    eventY=win.cvs.canvasy(event.y)
    #selector=win.cvs.create_rectangle(eventX+-3,eventY-3,eventX+3,eventY+3,fill="red",outline="blue",width=1) 

    for tab in tabs:
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        x=beat2x(beat)
        y=beat2y(beat)
        w=beat2w(dur)
        h=beat2h()
        if (eventX>=x and eventX<(x+w) and 
            eventY>=y and eventY<(y+h)):
           beatCursor=beat
           win.beatCursor.set(f"{beatCursor:.1f}")
           drawBars()   
           initTabScroll(beat)    # set for play
           doCursorPlay()
           firstPlayBeat=beatCursor
           return

metroMults=['0','1',u'\u00BD',u'\u00BC']
metroMultIdx=3
# go to next metro multiplier
def advMetroMult(event=None):
    global metroMultIdx
    if playing: return
    metroMultIdx=(metroMultIdx+1) % len(metroMults)
    win.lbMetroMult.configure(text=metroMults[metroMultIdx]+u'\u00D7')
    if metroMultIdx==0:
        win.imMetro.config(image=win.imgMetroG)
        win.lbMetroMult.configure(fg='gray80')
    if metroMultIdx==1:# just changed to 1
        win.imMetro.config(image=win.imgMetro)
        win.lbMetroMult.configure(fg='black')

# decrease metro multiplier if metronome rate fires faster than 300 bpm
def maxMetroMult():
    global metroMultIdx
    if bpm>300:
        if metroMultIdx==1: 
            #print (f"maxMetroMult {bpm} {metroMultIdx}")
            advMetroMult()

# reset zoom to 100%
def resetView(event):
    initBars(20)
    win.varZoom.set(100)
    drawBars(True)

# return min and max X,Y-coordinates of page
def pageBBox():
    return (0,0,beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize)

# return how many tab rows are visible
def barLinesFullyVisible(customWinHeight=None):
    if customWinHeight==None:
        return (win.cvs.winfo_height()-yOffset-beat2y(0))/beat2h()
    else:
        return (customWinHeight-yOffset-beat2y(0))/beat2h()

# modify beatsize until at least one (linear) or two (page) tab rows are visible 
def shrinkBars():
    global beatsize
    oldBeatsize=beatsize
    minBarLines=1 if win.varLinear.get() else 2
    # reduce beatsize until enough tab rows are visible and exit if beatsize too small
    while (barLinesFullyVisible()<minBarLines and beatsize>minBeatsize): #+56 for height of toolbar
        beatsize-=0.25
        initBars(beatsize)
        calcTabDims()
    # if not enough tab rows visible, we undo shrinkage
    if barLinesFullyVisible()<minBarLines:
        beatsize=oldBeatsize
        initBars(beatsize)
        calcTabDims()
        messagebox.showinfo("No fit found.","Try enlarging window.")
        return
    # redraw with new beatsize
    drawBars(True)   


titleBarHeight=0
# grow window until at least one (linear) or two (page) tabs are visible 
def growWindow():
    global winDims,titleBarHeight
    oldWinDims=winDims
    startX=win.winfo_x()
    startY=win.winfo_y()
    if tabDims[0]>(winDims[0]-beatsize*2-win.vbar.winfo_width()):
        winDims[0]=tabDims[0]+beatsize*2+win.vbar.winfo_width()
    minBarLines=1 if win.varLinear.get() else 2
    # increase window height VAR until enough tab rows are visible
    while (barLinesFullyVisible(winDims[1])<minBarLines): #+56 for height of toolbar
        winDims[1]+=10
    # if not enough tab rows visible, we undo growth of window
    if barLinesFullyVisible(winDims[1])<minBarLines:
        winDims=oldWinDims
        win.geometry(f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY}')    
        messagebox.showinfo("No fit found.","Try zoom.")
        return
    # set window size to window height VAR
    geomStr=f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY-titleBarHeight}'
    win.geometry(geomStr)    
    win.update()
    # compensate window drift to bottom because win.geometry will not accounted for title height
    if titleBarHeight==0:
        titleBarHeight=win.winfo_y()-startY
        geomStr=f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY-titleBarHeight}'
        win.geometry(geomStr)    
        win.update()
    #print (f"{geomStr}")

    # store resulting window and redraw 
    winDims=[win.winfo_width(),win.winfo_height()]
    initBars()#just to be sure all is updated
    drawBars(True)   

# grow if possible and shrink beatsize (zoom) to accomodate
def autoBars():
    growWindow()
    shrinkBars()
    growWindow()# to shrink window if width or height is too large

# if linear mode we need to remove unroll (duplicate) repeats
def reformatBars():
    # check if user clicked/chose linear mode
    linMode=win.varLinear.get()   
    if linMode==True:
        # if repeats check with user
        if hasRepeats():
            ret=messagebox.askyesno("Unroll tabs?","Tabs need to be unrolled to play in linear mode. \n\nDo you want to proceed?")        
            if ret==False: 
                win.varLinear.set(False)
                return
            else: # if user confirmed we unroll
                unrollRepeats()
        win.hbar.config(width=win.vbar.cget('width'))
        win.vbar.config(width=0)
    else:    
        win.vbar.config(width=win.hbar.cget('width'))
        win.hbar.config(width=0)
    # recalc and redraw
    calcTabDims()
    drawBars(True)

# return index in tabs-list of the tab currently under cursor 
def tabIdx():
    for idx,tab in enumerate(tabs):
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatCursor==beat and name not in sepIDs and name[0] not in ['{','}','?']:
            return idx
        if beatCursor>beat and beatCursor<(beat+dur):
            if idx<len(tabs)-1:
                return idx+1
            else:
                return idx    
    return -1

# return index of first tab on the same line as the given index (idx)
def tabLineStart(idx):
    for i in range(idx-1,-1,-1):
        if tabs[i][1]==eot: return i+1
    return 0

# return index of last tab on the same line as the given index (idx)
def tabLineEnd(idx):
    for i in range(idx+1,len(tabs)):
        if tabs[i][1]==eot: return i  
    return len(tabs)      
def saveScreenshot(saveAllTabs=True):
    global beatCursor
    try:
        # autosize
        if saveAllTabs: autoBars()
        # hide cursor
        cpbeatCursor=beatCursor
        beatCursor=99999
        drawBars()
        win.cvs.update()
        bBox=pageBBox()
        x=win.winfo_rootx()+win.cvs.winfo_x()+bBox[0]
        y=win.winfo_rooty()+win.cvs.winfo_y()+bBox[1]
        #x1=x+min(bBox[2],win.cvs.winfo_width())
        x1=x+win.cvs.winfo_width()
        
        if not saveAllTabs:
            # get screenshot bounding box
            y1=y+min(bBox[3],win.cvs.winfo_height())
            im=grab(bbox=(x,y,x1,y1))
            # save image
            filename=os.path.join(screenshotdir,title+".png")
            im.save(filename,format='png')
            print (f"Saved screenshot as '{filename}'")
            messagebox.showinfo("Saved screenshot",f"Saved screenshot as '{filename}'")
        if saveAllTabs:
            bBox=pageBBox()
            region=(int(bBox[2]),int(bBox[3]))
            ims = Image.new('RGB', region,backColor)
            offset=0
            toffset=0
            win.cvs.yview_moveto(0)
            win.cvs.update()
            for row in range(tabs[-1][6]+1):
                scroll2Row(row)# - scrolls, but row2y does not account for scroll
                win.cvs.update()
                yOrg=win.winfo_rooty()+win.cvs.winfo_y()
                offsetY=win.cvs.canvasy(0)
                rY=row2y(row)-offsetY
                nY=row2y(row+1)-offsetY
                if row==0: 
                    y1=yOrg
                    y2=yOrg+nY
                else: 
                    y1=yOrg+rY
                    y2=yOrg+nY
                im=grab(bbox=(x,y1,x1,y2))
                #filename=os.path.join(scriptdir,f"{title}-{row}.png")
                #im.save(filename,format='png')
                ims.paste(im, (0,int(toffset)))
                toffset+=(y2-y1)
            # save image
            filename=os.path.join(screenshotdir,title+".png")
            ims.save(filename,format='png')
            print (f"Saved screenshot as '{filename}'")
            messagebox.showinfo("Saved screenshot",f"Saved screenshot as '{filename}'")
        # show cursor
        beatCursor=cpbeatCursor
        drawBars()
    except Exception as e:
        print (f"Error saving screenshot file:{e}")
        traceback.print_exc()

# handle all key presses of user    
oldTabs=[]
autoAdvance=True
def keypress(event):
    global beatCursor, tabs,backColor,firstPlayBeat, prevCursorPlay,autoAdvance

    key=event.keysym
    char=event.char
    state=event.state
    keysym=f"{event.keysym}"
    # basic info
    curCol,curRow=-1,-1
    dur=0
    idx=tabIdx()
    if idx>-1: _,_, dur,_,_, curCol,curRow,_=tabs[idx]

    # handle play keys 
    if  key=="w":     # pause play
        if playing:
            pauseTabScroll()
        return
    elif  key=="Tab": # start play or pause
        if playing:
            pauseTabScroll() 
            return
        startTabScroll()
        return
    elif key=="q":   # stop play
        stopTabScroll()
        return
    elif  key=="r":   # auto size tabs/window to display full tab row
        autoBars()
        return

    # handle navigation
    elif key in ('Left','KP_Left'): # move cursor
        pidx=idx-1
        pdur=0
        while pdur==0 and idx>0:
            beat,_,pdur,_,_,_,_,_=tabs[pidx]
            pidx-=1
            beatCursor=beat
        keepBeatVisible()
        drawBars()
        prevCursorPlay=beatCursor-1
        doCursorPlay()
        firstPlayBeat=beatCursor
        #print (f"left  @ {beatCursor=} {pidx=}")
    elif key in ('Right','KP_Right'): # move cursor
        nidx=idx
        ndur=0
        lastTab=len(tabs)-2 if tabs[-1][1]==eot else len(tabs)-1
        while ndur==0 and idx<lastTab:
            nidx+=1
            beat,_,ndur,_,_,_,_,_=tabs[nidx]
        if ndur==0: nidx=idx # needed for last tabs, in which case no next tab with dur>0 can be found
        else: beatCursor=beat        
        keepBeatVisible()
        drawBars()
        prevCursorPlay=beatCursor-1
        doCursorPlay()
        firstPlayBeat=beatCursor
        #print (f"right {beatCursor=} {nidx=}")
    elif key in ('Up','KP_Up'): # move cursor
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow-1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        keepBeatVisible()
        drawBars()
        prevCursorPlay=beatCursor-1
        doCursorPlay()
        firstPlayBeat=beatCursor
    elif key in ('Down','KP_Down'): # move cursor
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow+1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        keepBeatVisible()
        drawBars()
        prevCursorPlay=beatCursor-1
        doCursorPlay()
        firstPlayBeat=beatCursor

    # modify note
    elif char in (noteIDs+restIDs):#['d','e','f','g','a','b','c','D','E','F','G','A','B','_','C']:
        if state==0: # NO MODIFIER KEYS (ALT, SHIFT, ALT) PRESSED
            if char=='f': char='f#'
            if char=='c': char='c#'
        if state==1: # SHIFT
            if char=='F': char='F#'
            if char=='C': char='C#' 
        if state==8: # ALT
            if char=='d': char='d#'
            if char=='f': char='f'
            if char=='g': char='g#'
            if char=='a': char='a#'
            if char=='c': char='c'
        if state==9: # SHIFT-ALT            
            if char=='D': char='D#'
            if char=='F': char='F'
            if char=='G': char='G#'
            if char=='A': char='A#'
            if char=='C': char='C'
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                oldTabs.append(copy.deepcopy(tabs))
                tabs[idx][1]=char
                if autoAdvance:
                    beatCursor+=dur  
                # make sure we have a rest so we can keep entering notes
                if tabs[-1][1]!='_':
                    beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[-1]
                    newTab=[beat+dur,'_',1,'',tabColor, tabCol+dur,tabRow,tabLin+1]
                    tabs.append(newTab)    
                calcTabDims()          
                drawBars(True)
                prevCursorPlay=beatCursor-2
                doCursorPlay()
                return
    # autoadvance note toggle
    elif key=='Scroll_Lock':
        autoAdvance= not autoAdvance
        drawBars(True)

    # modify style/decorator
    elif char in decoIDs or key=='Escape':
        deco= ' ' if key=='Escape' else char
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                oldTabs.append(copy.deepcopy(tabs))
                tabs[idx][3]=deco
                drawBars(True)
    # modify length
    elif char in ['1','2','3','4','5','6','7','8','9']:
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                oldTabs.append(copy.deepcopy(tabs))
                newDur=int(char)
                # implement triplets under alt-3            
                if char=='3' and state==8: # ALT
                    newDur=1
                    tabs[idx][3]='t'      
                delta=newDur-dur                        # store change in beats
                tabs[idx][2]=newDur                     # write new length
                #moveTabs(idx,delta)
                recalcBeats()
                calcTabDims()
                drawBars(True)
    # delete note
    elif key in ('Delete','KP_Delete'):
        oldTabs.append(copy.deepcopy(tabs))
        # increase idx if shift
        if state==1: idx+=1
        # delete tab
        tab=tabs.pop(idx)       
        # reduce idx if shift
        if state==1: idx-=1
        # move tabs
        stripSeps()
        recalcBeats()
        # make sure we have at least one rest (besides eot)
        if len(tabs)<=1: tabs.insert(0,[0,'_',1,'','green', 0,0,0])    
        # check if cursor on tab
        if idx>=(len(tabs)-1): 
            gotoPrevBeat(idx)
        # redraw
        drawBars(True)
    # insert note (before cursor)
    elif key in ('Insert', 'KP_Insert','KP_0'):
        oldTabs.append(copy.deepcopy(tabs))
        if state==1: idx+=1 # to append after
        tab=tabs[idx]
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        tabs.insert(idx,[beat,'_',1,'',tabColor, tabCol,tabRow,tabLin])
        recalcBeats()
        if state==1: beatCursor+=tabs[idx-1][2] # to append after and add dur
        calcTabDims()
        drawBars(True)
    # append note (after cursor)
    elif key in ('plus', 'KP_Add'):
        if idx==len(tabs)-1:
            oldTabs.append(copy.deepcopy(tabs))
            tab=tabs[idx]
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            tabs.append([beat+dur,'_',1,'',tabColor, tabCol+dur,tabRow,tabLin+dur])
            beatCursor+=dur
            calcTabDims()
            drawBars(True)
    # delete visual seperator
    elif key=='BackSpace':
        if idx>0:
            idx-=1
            tab=tabs[idx]
            #print (f"Backspace:{idx}|{tab}")

            if tab[1] in sepIDs or tab[1][0] in ['{','}','?']:
                oldTabs.append(copy.deepcopy(tabs))
                tab=tabs.pop(idx)
                #print (f"remove: {tab=}")
                recalcBeats()
                drawBars(True)

    # insert visual seperator of new line
    elif char in sepIDs+[' '] or key in ['Return','KP_Enter']:
        # make undo possible
        oldTabs.append(copy.deepcopy(tabs))
        # handle shift
        if state==1: idx+=1
        # check if not breaking up repeat
        fromIdx=tabLineStart(idx)
        toIdx=tabLineEnd(idx)
        fromRep,toRep=None,None
        for i in range(fromIdx,toIdx):
            if tabs[i][1][0]=='{':fromRep=i
            if tabs[i][1][0]=='}':toRep=i
        if fromRep!=None and toRep!=None:
            if idx==fromRep+1:idx-=1
            if idx==toRep:idx+=1
            if fromRep<idx<toRep:
                tabs.pop(toRep)            
                tabs.pop(fromRep)
        #print ("insert sep")
        #if beatCursor==0: return # inserting seperator as first column will shift entire page (bug)
        if idx==0: return # inserting seperator as first column will shift entire page (bug)
        sep=',' if char==' ' else char
        if key in ['Return','KP_Enter']: sep=eot
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        tabs.insert(idx,[beat,sep,0,'',tabColor, tabCol,tabRow,tabLin])
        stripSeps() # make sure we do not place a sep at start of end of row
        recalcBeats()        
        calcTabDims()
        drawBars(True)

    elif keysym in ['question']:
        char="?"
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        tabs.insert(idx,[beat,char,0,'',tabColor, tabCol,tabRow,tabLin])
        recalcBeats()        
        calcTabDims()
        drawBars(True)

    elif keysym in ['braceleft','braceright']+['bracketleft','bracketright']:
        # Do not allow overwriting
        # Replace with correct symbol
        if keysym in ('braceleft','bracketleft'): char='{'
        if keysym in ('braceright','bracketright'): char='}'
        # Read state of modifiers
        shift=1 if state%2==1 else 0
        state-=shift
        if shift: idx+=1 # shift modifier
        oldTabs.append(copy.deepcopy(tabs))
        # Construct new name
        nr=2
        if state==4:nr=3 #Ctrl
        if state==8:nr=4 #LAlt
        rep=f"{char}{nr}"
        # retrieve some info from current tabline
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        fromIdx=tabLineStart(idx)
        toIdx=tabLineEnd(idx)
        # remove old / duplicate
        for i in range (fromIdx,toIdx):
            if tabs[i][1][0]==char:
                tabs.pop(i)
                if i<idx:idx-=1
                toIdx-=1
        tabs.insert(idx,[beat,rep,0,'',tabColor, tabCol,tabRow,tabLin])
        # make nr repeats of { equal to }
        for i in range (fromIdx,toIdx):
            if char=='{': 
                if tabs[i][1][0]=='}':tabs[i][1]=f'}}{nr}'
            if char=='}': 
                if tabs[i][1][0]=='{':tabs[i][1]=f'{{{nr}'
        # make sure '{' comes before '}'
        idx1,idx2=None,None
        for i in range (fromIdx,toIdx):
            if tabs[i][1][0]=='{': idx1=i
            if tabs[i][1][0]=='}': idx2=i
        if idx1!=None and idx2!=None:
            if (idx2<idx1):
                tabs[idx1][1],tabs[idx2][1]=tabs[idx2][1],tabs[idx1][1]
        # we do not want the new } to be selected 
        while tabs[idx][1][0] in ['{','}'] and idx>0: idx-=1    
        # recalc and redraw
        recalcBeats()        
        calcTabDims()
        drawBars(True)

    # change tab color
    elif key[0]=='F':
        if len(key)>1:
            colorNr=int(key[1:])-1
            if colorNr<len(colors):
                oldTabs.append(copy.deepcopy(tabs))
                if state==0:
                    tab=tabs[idx]
                    tab[4]=colors[colorNr]
                if state==1:
                    backColor=backcolors[colorNr]
                drawBars(True)
    # undo del
    elif key in ('z') and state==4:
        if len(oldTabs)>0:
            tabs=oldTabs.pop()
            recalcBeats()
            calcTabDims()
            drawBars(True)
        else:
            print ("STACK EMPTY")    

    elif key in ('l') and state==4:#debug
        loadFileTab(tfilepath=filepath)
        initBars()
        beatCursor=0
        metroMultIdx=0
        advMetroMult()
        drawBars(True)

    elif key in ('s') and state==4:#debug
        saveFileTab(tfilepath=filepath)


    elif key in ('p','P'):
        saveScreenshot(saveAllTabs=(key=='P'))
        '''
        try:
            # autosize
            if state==1: autoBars()
            # hide cursor
            cpbeatCursor=beatCursor
            beatCursor=99999
            drawBars()
            win.cvs.update()
            bBox=pageBBox()
            x=win.winfo_rootx()+win.cvs.winfo_x()+bBox[0]
            y=win.winfo_rooty()+win.cvs.winfo_y()+bBox[1]
            #x1=x+min(bBox[2],win.cvs.winfo_width())
            x1=x+win.cvs.winfo_width()
            
            if key=='p':
                # get screenshot bounding box
                y1=y+min(bBox[3],win.cvs.winfo_height())
                im=grab(bbox=(x,y,x1,y1))
                # save image
                filename=os.path.join(screenshotdir,title+".png")
                im.save(filename,format='png')
                print (f"Saved screenshot as '{filename}'")
                messagebox.showinfo("Saved screenshot",f"Saved screenshot as '{filename}'")
            if key=='P':
                bBox=pageBBox()
                region=(int(bBox[2]),int(bBox[3]))
                ims = Image.new('RGB', region,backColor)
                offset=0
                toffset=0
                win.cvs.yview_moveto(0)
                win.cvs.update()
                for row in range(tabs[-1][6]+1):
                    scroll2Row(row)# - scrolls, but row2y does not account for scroll
                    win.cvs.update()
                    yOrg=win.winfo_rooty()+win.cvs.winfo_y()
                    offsetY=win.cvs.canvasy(0)
                    rY=row2y(row)-offsetY
                    nY=row2y(row+1)-offsetY
                    if row==0: 
                        y1=yOrg
                        y2=yOrg+nY
                    else: 
                        y1=yOrg+rY
                        y2=yOrg+nY
                    im=grab(bbox=(x,y1,x1,y2))
                    #filename=os.path.join(scriptdir,f"{title}-{row}.png")
                    #im.save(filename,format='png')
                    ims.paste(im, (0,int(toffset)))
                    toffset+=(y2-y1)
                # save image
                filename=os.path.join(screenshotdir,title+".png")
                ims.save(filename,format='png')
                print (f"Saved screenshot as '{filename}'")
                messagebox.showinfo("Saved screenshot",f"Saved screenshot as '{filename}'")
            # show cursor
            beatCursor=cpbeatCursor
            drawBars()
        except Exception as e:
            print (f"Error saving screenshot file:{e}")
            traceback.print_exc()
        '''
        
    # debug 
    #print (event)
    elif key in ('Home'):
        print (f"{idx=} {beatCursor=}")
        for idx2,tab in enumerate(tabs):
            print (f"{idx2:2d}> {tab}")

    elif key in ('Control_L','Alt_L','Shift_L'):
        pass # modifiers used in conjunction with other keys should not trigger "Key unknown" message.

    else:
        print (f"Key {key} unknown.")

# show help window    
def showHelp():
    helpWin.init(win,os.path.join(helpdir,"manual.txt"))
    helpWin.show()

# show help window   
winHelpdock=None 
def showHelpDocked():
    global winHelpdock
    if winHelpdock: 
        win.childResizeCallbacks.remove(helpWin.relocate)
        winHelpdock.destroy()
        winHelpdock=None
        win.btnHelpDock.config(image=win.imgSlideRight)
    else:     # already visible
        helpWin.init(win,os.path.join(helpdir,"shortcuts.txt"))
        winHelpdock=helpWin.show(docked=True)
        win.childResizeCallbacks.append(helpWin.relocate)
        win.btnHelpDock.config(image=win.imgSlideLeft)

# show help window   
winSonglist=None 
def showSonglist():
    global winSonglist
    if winSonglist: 
        win.childResizeCallbacks.remove(songlistWin.relocate)
        winSonglist.destroy()
        winSonglist=None
        win.btnSonglist.config(image=win.imgSlideLeft)
    else:     # already visible
        songlistWin.init(win,
                        ["/home/nard/Tin Whistle/TWHelper/tabs","/home/nard/Tin Whistle/TWHelper/abc"],
                        loadFromSonglist)
        winSonglist=songlistWin.show()
        win.childResizeCallbacks.append(songlistWin.relocate)
        win.btnSonglist.config(image=win.imgSlideRight)

# on resize window store new size of window
def resizeWindow(event):
    global winDims,winSonglist
    winDims=[win.winfo_width(),win.winfo_height()]
    for cCB in win.childResizeCallbacks:
        win.after(5,cCB())

def on_mousedown(event):
    mouse_begin_begin=[event.x,event.y]
    #print (f"{mouse_begin_begin=}")

def on_mouseup(event):
    mouse_end_begin=[event.x,event.y]
    #print (f"{mouse_end_begin=}")

def on_focus(event):
    win.lift()
    if winSonglist:
        winSonglist.lift()
    if winHelpdock:
        winHelpdock.lift()

# handle user closing window
def closeWindow():
    win.destroy()

# init window with all controls/widgets to display
def initWindow():
    global win
    
    sepSpacing=(8,8)

    # CREATE WINDOW
    win = tk.Tk()  
    win.option_add('*font',  '*font 9')
    # CREATE ROOM FOR CALLBACKS OF CHILDS IF win RESIZES OR MOVE
    win.childResizeCallbacks=[]

    # Set Window properties
    win.title(f"Tin Whistle Helper")
    win.geometry(f"{winDims[0]}x{winDims[1]}")
    backcolor=win["bg"]#"#DDDDDD"
    win.configure(background=backcolor)
    style=tk.SOLID
    iconpath=os.path.join(icondir,"TinWhistleHelper.png")
    win.tk.call('wm', 'iconphoto', win._w, tk.PhotoImage(file=iconpath))
    # set fonts

    win.buttonframe=tk.Frame(win,background="white",border=0,highlightthickness=0,relief=tk.FLAT,takefocus=0)
    win.buttonframe.pack(side=tk.BOTTOM,padx=(0,0),pady=(0,0),ipadx=2,ipady=2,expand=False,fill=tk.X)

    pathSlideLeft=os.path.join(icondir,"slideLeft.png")
    pathSlideRight=os.path.join(icondir,"slideRight.png")
    win.imgSlideLeft= tk.PhotoImage(file=pathSlideLeft)#.subsample(4,4)
    win.imgSlideRight= tk.PhotoImage(file=pathSlideRight)#.subsample(4,4)
    win.btnSonglist=tk.Button(win.buttonframe,image=win.imgSlideLeft,relief=tk.FLAT,width=8,height=26,command=showSonglist,takefocus=0)
    win.btnSonglist.pack(side=tk.LEFT,padx=(3,0))
    win.btnSonglist.tooltip=CreateToolTip(win.btnSonglist,"Show file list.\n(Discard changes\nDocked)")

    win.btnLoad=tk.Button(win.buttonframe,text="Load",relief=tk.FLAT,width=4,command=loadFile)
    win.btnLoad.pack(side=tk.LEFT,padx=(1,0))
    win.btnLoad.tooltip=CreateToolTip(win.btnLoad,"Load file.\n(Discard changes.)")

    imgPath=os.path.join(icondir,"new.png")
    win.imgNew= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnNew=tk.Button(win.buttonframe,image=win.imgNew,relief=tk.FLAT,width=24,command=newFile,takefocus=0)
    #win.btnNew=tk.Button(win.buttonframe,text="New",relief=tk.FLAT,width=4,command=newFile)
    win.btnNew.pack(side=tk.LEFT,padx=(1,0))
    win.btnNew.tooltip=CreateToolTip(win.btnNew,"New blank file.\n(Discard changes.)")

    imgPath=os.path.join(icondir,"save.png")
    win.imgSave= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnSave=tk.Button(win.buttonframe,image=win.imgSave,relief=tk.FLAT,width=24,command=saveFile,takefocus=0)
    #win.btnSave=tk.Button(win.buttonframe,text="Save",relief=tk.FLAT,width=4,command=saveFile)
    win.btnSave.pack(side=tk.LEFT,padx=(1,0))
    win.btnSave.tooltip=CreateToolTip(win.btnSave,"Save file.\n(Clear undo stack.)")

    imgPath=os.path.join(icondir,"screenshot.png")
    win.imgScreenshot= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnScreenshot=tk.Button(win.buttonframe,image=win.imgScreenshot,relief=tk.FLAT,width=24,command=saveScreenshot,takefocus=0)
    #win.btnSave=tk.Button(win.buttonframe,text="Save",relief=tk.FLAT,width=4,command=saveFile)
    win.btnScreenshot.pack(side=tk.LEFT,padx=(1,0))
    win.btnScreenshot.tooltip=CreateToolTip(win.btnScreenshot,"Save screenshot.\nShortcut: [p]/[P]")

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    imgPath=os.path.join(icondir,"chevLeftS.png")
    win.img2xSlower= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btn2xSlower=tk.Button(win.buttonframe,image=win.img2xSlower,relief=tk.FLAT,width=9,command=decrease2xBPM,takefocus=0)
    win.btn2xSlower.pack(side=tk.LEFT,padx=(2,0))
    win.btn2xSlower.tooltip=CreateToolTip(win.btn2xSlower,"Slow down play\n by 50%.")
    imgPath=os.path.join(icondir,"triLeftS.png")
    win.imgSlower= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnSlower=tk.Button(win.buttonframe,image=win.imgSlower,relief=tk.FLAT,width=9,command=decreaseBPM,takefocus=0)
    win.btnSlower.pack(side=tk.LEFT,padx=(0,2))
    win.btnSlower.tooltip=CreateToolTip(win.btnSlower,"Slow down play\n by 5 bpm.")
    win.bpm = tk.StringVar()
    win.bpm.set(f"{bpm:3}")
    win.speed = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.bpm, width=3)     
    win.speed.pack(side=tk.LEFT,padx=(0,0))
    win.speedl = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',text="bpm",font=("*font",6))     
    win.speedl.pack(side=tk.LEFT,padx=(0,0))
    imgPath=os.path.join(icondir,"triRightS.png")
    win.imgFaster= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnFaster=tk.Button(win.buttonframe,image=win.imgFaster,relief=tk.FLAT,width=9,command=fasterBPM,takefocus=0)
    win.btnFaster.pack(side=tk.LEFT,padx=(2,0))
    win.btnFaster.tooltip=CreateToolTip(win.btnFaster,"Speed up play\n by 5 bpm.")
    imgPath=os.path.join(icondir,"chevRightS.png")
    win.img2xFaster= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btn2xFaster=tk.Button(win.buttonframe,image=win.img2xFaster,relief=tk.FLAT,width=9,command=faster2xBPM,takefocus=0)
    win.btn2xFaster.pack(side=tk.LEFT,padx=(0,2))
    win.btn2xFaster.tooltip=CreateToolTip(win.btn2xFaster,"Speed up play\n by 200%.")

    if fluidsynthLoaded: 

        # draw sep
        win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,0))

        # countOff 
        win.varCountOff=tk.BooleanVar(value=False)
        win.cbCountOff=tk.Checkbutton(win.buttonframe,text='CO',variable=win.varCountOff,takefocus=0)
        footerbgcolor='white'
        footerfgcolor='black'
        win.cbCountOff.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
        #win.cbSound.config(font=("*font", 12))
        win.cbCountOff.pack(side=tk.LEFT,padx=(2,2))
        win.cbCountOff.tooltip=CreateToolTip(win.cbCountOff,"Count of 4 \nbeats before play.")

        # play metro (see:https://en.wikipedia.org/wiki/Media_control_symbols)
        win.metroFrame=tk.Frame(win.buttonframe,background="white",border=0,highlightthickness=0,relief=tk.FLAT)
        win.metroFrame.pack(side=tk.LEFT,padx=(0,6),pady=(0,0),ipadx=2,ipady=2,expand=False,fill=tk.Y)
        win.varMetro=tk.BooleanVar(value=True)
        win.lbMetroMult = tk.Label(win.metroFrame, text=u'\u00BC'+u'\u00D7',anchor="e",width=3,background='white',cursor="exchange")#"pirate")#"exchange")
        win.lbMetroMult.pack(side=tk.LEFT)
        footerbgcolor='white'
        footerfgcolor='black'
        imgPath=os.path.join(icondir,"Metronome18.png")
        imgPathG=os.path.join(icondir,"Metronome18G.png")
        win.imgMetro = tk.PhotoImage(file=imgPath)#.subsample(4,4)
        win.imgMetroG = tk.PhotoImage(file=imgPathG)#.subsample(4,4)
        win.imMetro = tk.Label(win.metroFrame, image=win.imgMetro,cursor="exchange")
        win.imMetro.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
        win.imMetro.pack(side=tk.LEFT)
        win.imMetro.tooltip=CreateToolTip(win.imMetro,"Slow down \nmetro 50%.")
        
        win.lbMetroMult.bind("<Button-1>",advMetroMult)
        win.imMetro.bind("<Button-1>",advMetroMult)
        

        # play sound (see:https://en.wikipedia.org/wiki/Media_control_symbols)
        imgPath=os.path.join(icondir,"whistlesound.png")
        win.imgSound= tk.PhotoImage(file=imgPath)
        win.varSound=tk.BooleanVar(value=True)
        win.cbSound=tk.Checkbutton(win.buttonframe,text='',variable=win.varSound,takefocus=0)
        win.lbSound=tk.Label(win.buttonframe,image=win.imgSound,takefocus=0)
        footerbgcolor='white'
        footerfgcolor='black'
        win.cbSound.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
        #win.cbSound.config(font=("*font", 12))
        win.cbSound.pack(side=tk.LEFT,padx=(2,0))
        win.cbSound.tooltip=CreateToolTip(win.cbSound,"Turn on/off\n whistle.")
        win.lbSound.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
        win.lbSound.pack(side=tk.LEFT,padx=(0,2))
        win.lbSound.tooltip=CreateToolTip(win.lbSound,"Turn on/off\n whistle.")

        # play decorations
        imgPath=os.path.join(icondir,"decos.png")
        win.imgDeco= tk.PhotoImage(file=imgPath)
        win.varDeco=tk.BooleanVar(value=False)
        win.cbDeco=tk.Checkbutton(win.buttonframe,text='',variable=win.varDeco,command=experimental,takefocus=0)
        win.lbDeco=tk.Label(win.buttonframe,image=win.imgDeco,takefocus=0)
        footerbgcolor='white'
        footerfgcolor='black'
        win.cbDeco.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
        #win.cbSound.config(font=("*font", 12))
        win.cbDeco.pack(side=tk.LEFT,padx=(2,0))
        win.cbDeco.tooltip=CreateToolTip(win.cbDeco,"Play \ndecorations.")
        win.lbDeco.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
        win.lbDeco.pack(side=tk.LEFT,padx=(0,2))
        win.lbDeco.tooltip=CreateToolTip(win.lbDeco,"Play \ndecorations.")

        # Low whistle 
        win.varLow=tk.BooleanVar(value=False)
        win.cbLow=tk.Checkbutton(win.buttonframe,text='Low',variable=win.varLow,command=setLowHigh,takefocus=0)
        footerbgcolor='white'
        footerfgcolor='black'
        win.cbLow.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
        #win.cbSound.config(font=("*font", 12))
        win.cbLow.pack(side=tk.LEFT,padx=(2,2))
        win.cbLow.tooltip=CreateToolTip(win.cbLow,"High/Low \nwhistle.")

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))
    
    # play symbols (see:https://en.wikipedia.org/wiki/Media_control_symbols)
    imgPath=os.path.join(icondir,"play.png")
    win.imgPlay= tk.PhotoImage(file=imgPath)
    win.btnPlay=tk.Button(win.buttonframe,image=win.imgPlay,relief=tk.FLAT,width=24,command=startTabScroll,takefocus=0)
    win.btnPlay.pack(side=tk.LEFT,padx=(1,0))
    win.btnPlay.tooltip=CreateToolTip(win.btnPlay,"Start tabs scroll. \nShortcut [Tab]")

    imgPath=os.path.join(icondir,"stop.png")
    win.imgStop= tk.PhotoImage(file=imgPath)
    win.btnStop=tk.Button(win.buttonframe,image=win.imgStop,relief=tk.FLAT,width=24,command=stopTabScroll,takefocus=0)
    win.btnStop.pack(side=tk.LEFT,padx=(1,0))
    win.btnStop.tooltip=CreateToolTip(win.btnStop,"Stop tabs scroll.\nShortcut [q]")

    imgPath=os.path.join(icondir,"pause.png")
    win.imgPause= tk.PhotoImage(file=imgPath)
    win.btnPause=tk.Button(win.buttonframe,image=win.imgPause,relief=tk.FLAT,width=24,command=pauseTabScroll,takefocus=0)
    win.btnPause.pack(side=tk.LEFT,padx=(1,0))
    win.btnPause.tooltip=CreateToolTip(win.btnPause,"Pause tabs scroll.\nShortcut [w]/[Tab]")

    win.beatCursor = tk.StringVar()
    win.beatCursor.set(f"{beatCursor:>5.1f}")
    win.beat = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.beatCursor,width=6)     
    win.beat.pack(side=tk.LEFT,padx=(3,3))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    imgPath=os.path.join(icondir,"unroll.png")
    win.imgUnroll = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnUnroll=tk.Button(win.buttonframe,command=unrollRepeats,relief=tk.FLAT,bg='white',image=win.imgUnroll,takefocus=0)
    win.btnUnroll.pack(side=tk.LEFT,padx=(0,2))
    win.btnUnroll.tooltip=CreateToolTip(win.btnUnroll,"Unroll repeated\nsections.")

    imgPath=os.path.join(icondir,"linear.png")
    win.imgLinear = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    imgPath=os.path.join(icondir,"wrap.png")
    win.imgWrap = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.varLinear=tk.BooleanVar(value=False)
    win.cbLinear=tk.Checkbutton(win.buttonframe,variable=win.varLinear,command=reformatBars,takefocus=0,
                                indicatoron=False,selectimage=win.imgWrap,image=win.imgLinear)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbLinear.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor,)
    #win.cbSound.config(font=("*font", 12))
    win.cbLinear.pack(side=tk.LEFT,padx=(0,2))
    win.cbLinear.tooltip=CreateToolTip(win.cbLinear,"Page / Linear view.")

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(6,6))

    imgPath=os.path.join(icondir,"autosize.png")
    win.imgAuto = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnAuto4Bars=tk.Button(win.buttonframe,image=win.imgAuto,relief=tk.FLAT,command=autoBars,takefocus=0)
    win.btnAuto4Bars.pack(side=tk.LEFT,padx=(1,0))
    win.btnAuto4Bars.tooltip=CreateToolTip(win.btnAuto4Bars,"Enlarge window and zoom out to fit tab \nwidth(page view) or height (linear view).\nShortcut [r]")

    imgPath=os.path.join(icondir,"shrink.png")
    win.imgShrink = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnShrink4Bars=tk.Button(win.buttonframe,image=win.imgShrink,relief=tk.FLAT,command=shrinkBars,takefocus=0)
    win.btnShrink4Bars.pack(side=tk.LEFT,padx=(1,0))
    win.btnShrink4Bars.tooltip=CreateToolTip(win.btnShrink4Bars,"Zoom out to fit tabs width(page view) \nor height (linear view) in window.")

    imgPath=os.path.join(icondir,"grow.png")
    win.imgGrow = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnGrow4Bars=tk.Button(win.buttonframe,image=win.imgGrow,relief=tk.FLAT,command=growWindow,takefocus=0)
    win.btnGrow4Bars.pack(side=tk.LEFT,padx=(1,2))
    win.btnGrow4Bars.tooltip=CreateToolTip(win.btnGrow4Bars,"Enlarge window to fit tabs width(page view) \nor height (linear view) in window.")

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    # zoom
    imgPath=os.path.join(icondir,"zoomout.png")
    win.imgZoomOut = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnZoomOut=tk.Button(win.buttonframe,image=win.imgZoomOut,bg='white',relief=tk.FLAT,command=zoomOut,takefocus=0)
    win.btnZoomOut.pack(side=tk.LEFT,padx=(0,0))
    win.btnZoomOut.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
    win.btnZoomOut.tooltip=CreateToolTip(win.btnZoomOut,"Zoom out \n(shrink) tabs.")

    win.varZoom = tk.IntVar()
    win.varZoom.set(100)
    win.zoom = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.varZoom, anchor='e',width=3)     
    win.zoom.pack(side=tk.LEFT,padx=(0,0))
    win.zooml = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',text="%",anchor='e',font=("*font",6),width=1)     
    win.zooml.pack(side=tk.LEFT,padx=(0,0))

    imgPath=os.path.join(icondir,"zoomin.png")
    win.imgZoomIn = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnZoomIn=tk.Button(win.buttonframe,image=win.imgZoomIn,bg='white',relief=tk.FLAT,command=zoomIn,takefocus=0)
    win.btnZoomIn.pack(side=tk.LEFT,padx=(0,0))
    win.btnZoomIn.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
    win.btnZoomIn.tooltip=CreateToolTip(win.btnZoomIn,"Zoom in \n(enlarge) tabs.")

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    # help
    win.btnHelpDock=tk.Button(win.buttonframe,image=win.imgSlideRight,bg='white',relief=tk.FLAT,width=8,height=26,command=showHelpDocked,takefocus=0)
    win.btnHelpDock.pack(side=tk.RIGHT,padx=(0,3))
    win.btnHelpDock.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
    win.btnHelpDock.tooltip=CreateToolTip(win.btnHelpDock,"Show control help.\n(Docked)")

    imgPath=os.path.join(icondir,"help.png")
    win.imgHelp = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnHelp=tk.Button(win.buttonframe,image=win.imgHelp,bg='white',relief=tk.FLAT,command=showHelp,takefocus=0)
    win.btnHelp.pack(side=tk.RIGHT,padx=(0,0))
    win.btnHelp.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)

    # make canvas
    win.vbar=tk.Scrollbar(win,orient=tk.VERTICAL,takefocus=0)
    win.vbar.pack(side=tk.RIGHT,fill=tk.Y)
    win.hbar=tk.Scrollbar(win,orient=tk.HORIZONTAL,takefocus=0)
    win.hbar.pack(side=tk.BOTTOM,fill=tk.X)
    win.cvs = tk.Canvas(win, bg="white" )
    win.cvs.pack(expand=True,fill=tk.BOTH,padx=(0,0),pady=(0,0))
    win.vbar.config(command=win.cvs.yview)
    win.hbar.config(command=win.cvs.xview)
    win.cvs.config(yscrollcommand=win.vbar.set)
    win.cvs.config(xscrollcommand=win.hbar.set)
    win.hbar.config(width=0)

    # bind mouse
    win.cvs.bind("<ButtonPress-1>", drag_enter)
    win.cvs.bind("<B1-Motion>", drag_handler)
    win.cvs.bind("<ButtonRelease-1>", drag_end)    
    # bind keys
    win.bind("<Key>",keypress)
    win.bind("<Button-4>", scrollwheel) # for linux scrollup
    win.bind("<Button-5>", scrollwheel) # for linux scrolldown
    win.bind("<MouseWheel>",scrollwheel)# for windows/macos
    win.bind("<Button-3>", resetView)
    win.bind("<Configure>", resizeWindow) #
    win.bind("<FocusIn>", on_focus)
    win.bind("<ButtonPress-1>", on_mousedown)
    win.bind("<ButtonRelease-1>", on_mouseup)
    win.protocol("WM_DELETE_WINDOW", closeWindow) # custom function which sets winDestroyed so we can check state of win


def loadDefaultTune():
    # wait for splash to disappear
    if splash.visible(): 
        win.after(50,loadDefaultTune)
        return
    
    print ("load default tune")
    #loadFileTab("Fee Ra Huri.tb")
    #loadFileTab("tutorial.tb")
    # public domain tunes
    #loadFileABC("Down By The Sally Garden.abc")    
    #loadFileTab("Fig For A Kiss.tb")
    #loadFileTab("testDecos.tb")
    
    #loadFileTab("testTriplet.tb")                  # not playing al notes above 240 bpm
    #loadFileTab("Down By The Sally Gardens.tb")
    loadFileTab("Drowsy Maggie.tb")                 
    #loadFileTab("testTongue.tb")                  # not playing al notes above 240 bpm
    #loadFileTab("testRepeat.tb")                  # not playing al notes above 240 bpm
    
    #loadFileABC("Raggle Taggle Gipsy.abc")

    autoBars() # make sure tabs are fully on screen
    drawBars(True)
    #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/canvas-methods.html


initWindow()

initPlayer()

#fs.noteon(0, 64,127)
#time.sleep(0.1)
#fs.noteon(0, 64,92)
#fs.
#time.sleep(0.1)
#fs.noteoff(0,64)
#time.sleep(1)
#fs.noteoff(1,64)
#quit()

newFile()

win.update()
toolbarWidth=win.btnHelp.winfo_x()+win.btnHelp.winfo_width()
win.minsize(toolbarWidth, 120)
win.after(50,showSplash)
win.after(50,loadDefaultTune)

#showSonglist()

tk.mainloop()
closePlayer()