#   Elan - Nightwish uitwerken
#   README.md > does double click in windows on py file really start

# BUG: Cannot enter f# in windows
# TODO: make splash to thank for usage of fluidsynt?
# DONE: show experimental only once
#
# FOR EACH RELEASE
# TODO: pip3 freeze >requirements.txt
# TODO: make packages  
#        1) 'pyinstaller TWHelper.py'       see https://pyinstaller.readthedocs.io/en/stable/usage.html#using-pyinstaller
#        2) copy resources/screenshots/tabs folder to dist folder
#        3) copy libfluidsynth.so.* and libfluidsynth64.dll to dist folder

import traceback
import os
from sys import platform

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
icondir   = os.path.join(scriptdir,"resources/icons")
sf2dir    = os.path.join(scriptdir,"resources/sf2")
screenshotdir=os.path.join(scriptdir,"screenshots")
helpdir   = os.path.join(scriptdir,"resources")

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
expShown=False
def experimental():
    global expShown
    if expShown: return
    infoDialog.show(win,title= "Experimental",
                        message="This feature is experimental and \nprobably will not work properly.",
                        timeout=2000)
    expShown=True
def showSplash():
    mw=win.winfo_width()
    mh=win.winfo_height()
    sw=700
    sh=400
    sx=win.winfo_x()+int((mw-sw)/2)
    sy=win.winfo_y()+int((mh-sh)/2)
    dims=f"{sw}x{sh}+{sx}+{sy}"
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

#https://www.fluidsynth.org/api/LoadingSoundfonts.html
#https://github.com/nwhitehead/pyfluidsynth
sfFlute=None
sfMetro=None
chnFlute=None
chnMetro=None
def initPlayer():
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
decoIDs = ['<','^', '>', '=', '@', '~', '\\','/','-']
repID   = 'rep'

def setLowHigh():
    global noteNrs
    if playing: 
        win.varLow.set(noteNrs==noteNrsLow)
        return
    noteNrs=noteNrsLow if win.varLow.get() else noteNrsHigh

def startNote(noteId):    
    if not fluidsynthLoaded: return
    global oldNoteNr
    if noteId in noteNrs:
        noteNr=noteNrs[noteId]
        fs.noteon(0, noteNr,127)
        oldNoteNr=noteNr
    #print (f"On : {noteId}")
startNote('')
def endNote(noteId=None):
    if not fluidsynthLoaded: return    
    noteNr=oldNoteNr if noteId==None else noteNrs[noteId]
    fs.noteoff(0, noteNr)
    #print (f"Off: {noteId}")

def startTick():
    if not fluidsynthLoaded: return
    noteNr=12*9+2
    fs.noteoff(1, noteNr)
    fs.noteon(1, noteNr,127)

def closePlayer():
    if not fluidsynthLoaded: return
    fs.delete()

win=None
tabs=[]
title=""

def capTitle():
    global title
    title=" ".join([word.capitalize() for word in title.split(" ")])

colors=['blue', 'purple3', '#00BBED','red','DeepPink3','magenta','orange','gold','brown','green','gray39','black',]
backcolors=['#7BDAFF','#FFC6F4','#CeF1Fd','#ffC0C0','#F7A8Db','#f1Bbf1','#FeE59a','#FFFFDE','#D3B4B4','#A0FdA0','#D4D4D4','#FFFFFF']
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

textColor='black'
backColor='#FFFFDE'
texts=[]
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

def nrTabRows():
    if len(tabs)==0: return 0
    return tabs[-1][6]+1
def rowStart(rowNr):
    for idx in range(len(tabs)):
        if tabs[idx][6]==rowNr: return idx
def rowEnd(rowNr):
    for idx in range(len(tabs)-1,-1,-1):
        if tabs[idx][6]==rowNr: return idx

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

def hasRepeats(fromIdx=0,toIdx=-1):
    if toIdx==-1: toIdx=len(tabs)
    for idx in range(fromIdx,toIdx):
        if tabs[idx][1][0]=='}': return True
    return False

def firstRepeat(fromIdx=0,toIdx=-1):
    if toIdx==-1: toIdx=len(tabs)
    for idx in range(fromIdx,toIdx):
        if tabs[idx][1][0]=='{': return idx
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

'''
def gotoPrevBeat2():
    global beatCursor
    for idx in range(len(tabs)-1,-1,-1):
        print (f"{idx}> {beatCursor} vs {tabs[idx][0]}")
        if ( tabs[idx][0] == beatCursor ) :
            for idx2 in range(idx-1,-1,-1):
                if tabs[idx2][2]>0: 
                    beatCursor=tabs[idx2][0]
                    return idx2
    print ("not fnd")
    return -1
'''

filename=None
filepath=None
def loadFile2(tfilename=None,tfilepath=None):
    global tabs,bpm,title,filename,filepath
    global textColor,backColor,texts   

    if tfilepath==None:
        tfilepath=os.path.join(tabdir,tfilename)        
    if not os.path.isfile(tfilepath): return

    tabs.clear()
    initBars(20)
    tabColor=colors[2]
    backColor='#FFFFDE'
    beat,tabRow,tabCol,tabLin=0,0,0,0 #just placeholders, real values will be calculated after loading by recalcBeats
    #print (f"filename:{filename}|")
    filepath=tfilepath
    filename=os.path.basename(tfilepath)
    title=os.path.basename(tfilepath).split('.')[0].replace("_"," ")
    capTitle()
    texts.clear()
    try:
        with open(tfilepath,'r',encoding='utf-8') as reader:
            lines=reader.readlines()
        #remove comments and empty lines
        for idx in range(len(lines)-1,-1,-1):            
            line=lines[idx].strip()
            if len(line)==0: lines=lines[:idx]+lines[idx+1:]
            elif line[0]=='#':lines=lines[:idx]+lines[idx+1:]
        #read bpm
        bpm=int(lines[0])        
        win.bpm.set(f"{bpm:3}")
        maxMetroMult()
        lines=lines[1:]
        for line in lines:      # go line by line
            line=line.strip()   # remove leading and trailing spaces and eol chars
            if len(line)>0:     # ignore empty lines
                if ':' in line: # read colors and text to display
                    colIdx=line.index(':')
                    cmd=line[:colIdx]
                    val=line[colIdx+1:]
                    #cmd,val=line.split(':')
                    cmd=cmd.strip()
                    vals=val.split(",")
                    for idx in range(len(vals)): vals[idx]=vals[idx].strip()
                    if cmd=='color': textColor=vals[0]
                    if cmd=='back' : backColor=vals[0]
                    if cmd=='text' : texts.append(vals)
                else:           # read notes                
                    line=line.replace('   ',' , , ') # tripple space is visual space between tabs
                    line=line.replace('  ',' , ') # double space is visual space between tabs
                    while '  ' in line:
                        line=line.replace('  ','') # more spaces are removed visual space between tabs
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
                            if name in (noteIDs+restIDs+sepIDs) or name in ('{','}'):#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_','|',',']:
                                if name in sepIDs: dur=0 #('|',','): dur=0
                                if name in ('{','}'): name,dur=note,0
                                tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]) 
                                notesfound=True
                            else:
                                print (f"Rejected: [{note}] {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
                    if notesfound: # ignore lines with only color
                        name=eot
                        dur=0
                        style=''
                        tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
        
        win.title(f"Tin Whistle Helper - {os.path.basename(tfilepath).split('.')[0]}")
        recalcBeats()
        calcTabDims()
    except Exception as e:
        print (f"Error reading tab file:{e}")
        #if line: print (f"line:'{line}'") # not working, at least not under windows
        #print (f"Note:'{note}'")
        traceback.print_exc()



def saveFile2(tfilename=None,tfilepath=None):
    global title,filename,filepath
    if tfilepath==None:
        tfilepath=os.path.join(tabdir,tfilename)        
    if not os.path.isfile(tfilepath): return

    title=os.path.basename(tfilepath).split('.')[0].replace("_"," ")
    filepath=tfilepath
    filename=os.path.basename(tfilepath)
    capTitle()
    drawBars(True)
    eol='\n'
    try:
        with open(tfilepath,'w',encoding='utf-8') as writer:   
            writer.write(f"# {title}{eol}")
            writer.write(f"#   made with TWHelper{eol}")
            writer.write(f"#   see https://github.com/NardJ/Tin-Whistle-Helper{eol}")
            writer.write(f"{eol}")
            writer.write(f"# Beats per Minute (bpm){eol}")
            writer.write(f"{bpm}{eol}")
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
                elif name[0] in ['{','}']:
                    writer.write(f"{name} ")

    except Exception as e:
        print (f"Error writing tab file:{e}")
        traceback.print_exc()
    
def saveFile():
    global beatCursor,metroMultIdx
    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    rep = filedialog.asksaveasfile(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=tabdir,
                                        initialfile=filename,
                                        defaultextension=".tb",
                                        filetypes=[
                                            ("Tin Whistle Tab files", ".tb")
                                    ])
    if (rep==None): return
    #print (f"rep:{rep.name}")
    scriptpath=rep.name                                
    if (scriptpath==None): return    
    ext=scriptpath[-3:]
    if ext=='.tb': 
        saveFile2(tfilepath=scriptpath)
        oldTabs.clear()
    else: return        
    print (f"Saved:{scriptpath}")

    

def loadFile():
    global beatCursor,metroMultIdx

    if len(oldTabs)>0:
        ret=messagebox.askyesno("Discard changes?","You have unsaved changes.\nDiscard and load other file?")
        if ret==False:return

    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    rep = filedialog.askopenfilenames(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=tabdir,
                                        defaultextension="*.tb",
                                        filetypes=[
                                            #("Tin Whistle Tab files", "*.tbs"),
                                            ("Tin Whistle Tab files", "*.tb"),
                                    ])
    if (len(rep)==0): return
    scriptpath=rep[0]                                   # use first file in list
    if (scriptpath==None): return    
    ext=scriptpath[-3:]
    #if ext=='tbs': 
    #    loadFile(filepath=scriptpath)
    #elif ext=='.tb': 
    if ext=='.tb':
        loadFile2(tfilepath=scriptpath)
    else: return        
    initBars()
    beatCursor=0
    metroMultIdx=0
    advMetroMult()
    drawBars(True)
    print (f"Loaded:{scriptpath}")

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
beatsize=20
barInterval=1.2*beatsize
holeInterval=1.5*beatsize
xOffset=beatsize
yOffset=beatsize
beatCursor=0
winDims=[1118,800]

tabDims=[0,0]
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

def col2x(tabCol):
    x=xOffset+tabCol*barInterval
    return x
def beat2x(beat):
    fndTab=None
    lin=win.varLinear.get()   
    for tab in tabs:
        [tabBeat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab        
        if (beat>=tabBeat): fndTab=tab
    tabBeat,name,dur,style,tabColor,tabCol,tabRow,tabLin = fndTab
    if lin:
        x=xOffset+tabLin*barInterval
    else:
        x=xOffset+tabCol*barInterval
    x=x+(beat-tabBeat)*barInterval
    return x

titleHeight=40
def row2y(tabRow):
    y=yOffset+tabRow*holeInterval*10
    return y+titleHeight
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

def beat2w(dur):
    w=(dur-1)*barInterval+beatsize
    return w

def beat2h():
    return holeInterval*9
row2h=beat2h

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

    if noteId == '' : return False
    if noteId == ',': return False
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
        return False
    if noteId == eot: return False

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

    holes=notes[noteId]

    if noteId    == '_':
        dashPatt =  (1,3)
        linewidth=  3
        #tabColor =  'gray70'
        noteId   =  '' # so no rest is printed
    else:
        dashPatt=None
        linewidth=  1

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

    fnt=("*font", int(beatsize*0.7))
    if noteStyle=='<':#cut ⮤
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
          
    if noteStyle=='>':#tap/strike ↴
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

    if noteStyle=='^':#roll (cut+tap/strike) ⮤↴
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

    if noteStyle=='=':#slide ⇒
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21D2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
        #cvs.create_text(x1,y1,text=u'\u27B2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='@':#tonguing ᳅
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
    if noteStyle=='~':#vibrato ∿
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u223F',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='/':#join
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=90,style=arcstyle,width=2)
        cvs.create_line(x1+beat2w(1)/2,y1,x1+beat2w(1)/2+beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='\\':
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_arc(x2-beatsize, y1, x2, y1+beatsize,fill=fillColor,outline=tabColor,start=0,extent=90,style=arcstyle,width=2)
        cvs.create_line(x2-beat2w(1)/2,y1,x2-beat2w(1)/2-beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='-':
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_line(x1,y1,x2,y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

    # Draw note Name
    noteId=noteId.replace('#',u'\u266F')
    x1=beat2x(beat)+beat2w(1)/2 # beat2x(beat)+beat2w(dur)/2
    y1=y0+holeInterval*8.5
    fnt=("*font", int(beatsize*0.5))
    cvs.create_text(x1,y1,text=noteId,font=fnt)

    return True


cursorBar=None
cursorBar2=None
oldOffsets=[0,0]
oldBeatsize=0
inDrawBars=False
def drawBars(force=False):
    global xOffset,yOffset,cursorBar,cursorBar2,oldOffsets,oldBeatsize,inDrawBars
    # prevent double draws, which mainly occur on window resize
    if inDrawBars and not force: return
    inDrawBars=True

    curTabIdx=-1
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
    if not playing:
        dashPatt=(1,2)
        cursorBar2=win.cvs.create_rectangle(x+1,y,x+w,y+h,width=1,outline='red',dash=dashPatt) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    cursorBar=win.cvs.create_line(x,y,x,y+h,fill='red',width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

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

noteSilence=50 #msec
nrRepeats=0
repeatStart=0
repeatStartIdx=0
def doCursorPlay():
    global nrRepeats,repeatStart,beatCursor,repeatStartIdx
    if int(beatCursor)!=round(beatCursor,1): return
    if metroMultIdx>0:
        metroInterval=2**(metroMultIdx-1)
        if (beatCursor%metroInterval)==0: startTick()

    if not win.varSound.get(): 
        endNote()
        return

    # check if we are starting new tab with repeat or new line
    if playing and int(beatCursor)==round(beatCursor,2):
        #print (f"beat:{int(beatCursor)}")
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
            if beat==round(beatCursor,2):
                if name[0]=='{':
                    repeatStart=beatCursor
                    repeatStartIdx=idx
                    nrRepeats=int(name[1])
                    #print (f"{{ {beat}")
                if name[0]=='}':# and idx>repeatStartIdx:
                    #print (f"}} {beat}")
                    if nrRepeats>1:
                        beatCursor=repeatStart
                        nrRepeats-=1
                    else:
                        nrRepeats=0
                        repeatStart=0
                        repeatStartIdx=0

    # play note
    for tab in tabs:
        beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
        if (beat==round(beatCursor,2)):
            if name in noteIDs:#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G']:
                startNote(name)                
                delay=dur*int(60/bpm*1000)
                noteLength=delay-noteSilence if (noteSilence<delay) else delay
                win.after(noteLength,endNote,name)

                if win.varDeco.get():
                    if style==">":#strike/tap one note higher
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
                    if style=="<":#cut:lift finger on g for d/e/f and b for g/a/b see: https://learntinwhistle.com/lessons/tin-whistle-cuts/                        
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
                        pitchBend(2048*slideAmount,noteLength,0.6,0.8)
                        
                    if style=="@":#tongue
                        pass
                    if style=="~":#vibrato
                        vibrato(name,noteLength)


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
def stopTabScroll():
    global playing,beatCursor,firstPlayBeat
    if not playing:
        firstPlayBeat=0
    beatCursor=firstPlayBeat
    endNote()
    playing=False
    widgets=[win.btnLoad, win.btnNew,win.btnSave,
            win.btnSlower,win.btn2xSlower,win.btnFaster,win.btn2xFaster,
            win.cbCountOff,win.cbLow,win.cbDeco,win.lbMetroMult,win.imMetro,win.cbSound,
            win.cbLinear,win.btnUnroll,win.btnAuto4Bars,win.btnShrink4Bars,win.btnGrow4Bars,win.btnZoomOut,win.btnZoomIn,win.btnHelp]
    for widget in widgets: widget.config(state=tk.NORMAL)
    win.cvs.xview_moveto(0)    
    win.cvs.yview_moveto(0)    
    drawBars()
def pauseTabScroll():
    global beatUpdate,delayJob
    if delayJob is None:
        delayJob=win.after(0, advTabScroll)
        doCursorPlay()
    else:
        win.after_cancel(delayJob)
        delayJob=None
        endNote()

def advTabScroll():
    global beatCursor,delayJob
    if playing:
        lastTab=tabs[-1]
        lastBeat=lastTab[0]+lastTab[2]
        if beatCursor>lastBeat:
            # remove incremented beatCursor for which no note is present
            beatCursor-=beatUpdate 
            beatCursor=round(beatCursor,3)
            win.beatCursor.set(f"{beatCursor:>5.1f}")
            # stop play
            stopTabScroll()
        else:
            delay=int((60/bpm*1000)*beatUpdate)
            delayJob=win.after(delay, advTabScroll)
            beatCursor+=beatUpdate
            beatCursor=round(beatCursor,3)
            win.beatCursor.set(f"{beatCursor:>5.1f}")
            doCursorPlay()
            drawBars()

def delay2beatUpdate(delay):
    return int((60/bpm*1000)*beatUpdate)
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

def initTabScroll(fromBeat=0):
    beatCursor=fromBeat
    win.beatCursor.set(f"{beatCursor:.1f}")
    setBeatUpdate()
    delay=int((60/bpm*1000)*beatUpdate)

def startTabScroll():
    nrBarLines=barLinesFullyVisible()#(win.cvs.winfo_height())/beat2h()
    if win.varLinear.get():
        if nrBarLines<1:
            messagebox.showinfo("Cannot play","In linear mode the full bar height should be fully visible.\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            return
        #check if one row on screen
    else:        
        if nrBarLines<2 :
            messagebox.showinfo("Cannot play","In page mode, at least to bar lines should be fully visible.\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            return
        if win.cvs.winfo_width()<tabDims[0]:
            messagebox.showinfo("Cannot play","In page mode, the window-width should accomodate all bars\nEnlarge window or use [Ctrl]-scroll wheel to zoom.")
            return
    global playing, beatCursor,delayJob, beatUpdate,xOffset,yOffset
    if playing: # restart from original
        initBars(beatsize) # don't reset zoom
        return    
    initTabScroll(firstPlayBeat)
    initBars(beatsize) # don't reset zoom
    playing=True
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

def decreaseBPM():
    if playing: return
    global bpm
    bpm=bpm-5
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3}")
def decrease2xBPM():
    if playing: return
    global bpm
    bpm=int(bpm/2)
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3}")
def fasterBPM():
    if playing: return
    global bpm
    bpm=bpm+5
    if bpm>960: bpm=960
    win.bpm.set(f"{bpm:3}")
    maxMetroMult()
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
def drag_enter(event):
    global drag_begin,drag_start,scroll_start
    drag_begin=[event.x,event.y]
    drag_start=time.time()

    linMode=win.varLinear.get()   
    if linMode==True:
        scroll_start=win.hbar.get()
    else:
        scroll_start=win.vbar.get()
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
def drag_end(event):
    if (time.time()-drag_start)<0.2: 
        click(event)
        return

zooms=[25,40,50,67,75,85,100,150,200,250,400]
def setZoom():
    win.varZoom.set(int(100*(beatsize/20)+0.5))
def setBeatSize():
    global beatsize
    beatsize=int(win.varZoom.get()/100*20)
    initBars(beatsize)
    calcTabDims()
    drawBars(True)  
def zoomIn():
    zIdx=zooms.index(win.varZoom.get())
    zIdx+=1
    if zIdx>=len(zooms): zIdx=len(zooms)-1
    win.varZoom.set(zooms[zIdx])        
    setBeatSize()
def zoomOut():
    zIdx=zooms.index(win.varZoom.get())
    zIdx-=1
    if zIdx<0: zIdx=0
    win.varZoom.set(zooms[zIdx])
    setBeatSize()
def scrollwheel(event):
    if event.state==0:
        s=win.vbar.get()[0]
        d=-0.1 if event.num==4 else 0.1
        win.cvs.yview_moveto(s+d)
        #print (f"scroll:{win.vbar.get()} {win.vbar.get()[0]*tabDims[1]}")
    if event.state==4: # with control
        if event.num==4: zoomOut()
        if event.num==5: zoomIn()
def scroll2Row(row):
    rowHeight=beat2h()/tabDims[1]
    relY=row*rowHeight
    win.cvs.yview_moveto(relY)

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
metroMultIdx=1
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
def maxMetroMult():
    global metroMultIdx
    if bpm>300:
        if metroMultIdx==1: advMetroMult()
def resetView(event):
    initBars(20)
    drawBars(True)

def pageBBox():
    return (0,0,beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize)
def barLinesFullyVisible(customWinHeight=None):
    if customWinHeight==None:
        return (win.cvs.winfo_height()-yOffset-beat2y(0))/beat2h()
    else:
        return (customWinHeight-yOffset-beat2y(0))/beat2h()

def shrinkBars():
    global beatsize
    oldBeatsize=beatsize
    minBarLines=1 if win.varLinear.get() else 2
    while (barLinesFullyVisible()<minBarLines and beatsize>minBeatsize): #+56 for height of toolbar
        beatsize-=0.25
        initBars(beatsize)
        calcTabDims()
    if barLinesFullyVisible()<minBarLines:
        beatsize=oldBeatsize
        initBars(beatsize)
        calcTabDims()
        messagebox.showinfo("No fit found.","Try enlarging window.")
        return
    drawBars(True)   

titleBarHeight=0
def growWindow():
    global winDims,titleBarHeight
    oldWinDims=winDims
    startX=win.winfo_x()
    startY=win.winfo_y()
    if tabDims[0]>(winDims[0]-beatsize*2-win.vbar.winfo_width()):
        winDims[0]=tabDims[0]+beatsize*2+win.vbar.winfo_width()
    minBarLines=1 if win.varLinear.get() else 2
    while (barLinesFullyVisible(winDims[1])<minBarLines): #+56 for height of toolbar
        winDims[1]+=10
    if barLinesFullyVisible(winDims[1])<minBarLines:
        winDims=oldWinDims
        win.geometry(f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY}')    
        messagebox.showinfo("No fit found.","Try zoom.")
        return
    geomStr=f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY-titleBarHeight}'
    win.geometry(geomStr)    
    win.update()
    if titleBarHeight==0:
        titleBarHeight=win.winfo_y()-startY
        geomStr=f'{winDims[0]:.0f}x{winDims[1]:.0f}+{startX}+{startY-titleBarHeight}'
        win.geometry(geomStr)    
        win.update()
    print (f"{geomStr}")
    winDims=[win.winfo_width(),win.winfo_height()]
    initBars()#just to be sure all is updated
    drawBars(True)   

def autoBars():
    growWindow()
    shrinkBars()
    growWindow()# to shrink window if width or height is too large

def reformatBars():
    linMode=win.varLinear.get()   
    if linMode==True:
        if hasRepeats():
            ret=messagebox.askyesno("Unroll tabs?","Tabs need to be unrolled to play in linear mode. \n\nDo you want to proceed?")        
            if ret==False: 
                win.varLinear.set(False)
                return
            else:
                unrollRepeats()
        win.hbar.config(width=win.vbar.cget('width'))
        win.vbar.config(width=0)
    else:    
        win.vbar.config(width=win.hbar.cget('width'))
        win.hbar.config(width=0)
    calcTabDims()
    drawBars(True)

def tabIdx():
    for idx,tab in enumerate(tabs):
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatCursor==beat and name not in sepIDs and name[0] not in ['{','}']:
            return idx
        if beatCursor>beat and beatCursor<(beat+dur):
            if idx<len(tabs)-1:
                return idx+1
            else:
                return idx    
    return -1
def tabLineStart(idx):
    for i in range(idx-1,-1,-1):
        if tabs[i][1]==eot: return i+1
    return 0
def tabLineEnd(idx):
    for i in range(idx+1,len(tabs)):
        if tabs[i][1]==eot: return i  
    return len(tabs)      
    
oldTabs=[]
def keypress(event):
    global beatCursor, tabs,backColor,firstPlayBeat
    #print (event)
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
    if  key=="w":
        if playing:
            pauseTabScroll()
        return
    elif  key=="Tab":
        if playing: return
        startTabScroll()
        return
    elif  key=="r":
        autoBars()
        return
    elif key=="q":
        stopTabScroll()
        return

    # handle navigation
    elif key in ('Left','KP_Left'): 
        pidx=idx-1
        pdur=0
        while pdur==0 and idx>0:
            beat,_,pdur,_,_,_,_,_=tabs[pidx]
            pidx-=1
            beatCursor=beat
        keepBeatVisible()
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor
    elif key in ('Right','KP_Right'): 
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
        doCursorPlay()
        firstPlayBeat=beatCursor
    elif key in ('Up','KP_Up'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow-1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        keepBeatVisible()
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor
    elif key in ('Down','KP_Down'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow+1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        keepBeatVisible()
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor

    # modify note
    elif char in (noteIDs+restIDs):#['d','e','f','g','a','b','c','D','E','F','G','A','B','_','C']:
        if state==0:
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
                beatCursor+=dur  
                # make sure we have a rest so we can keep entering notes
                if tabs[-1][1]!='_':
                    beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[-1]
                    newTab=[beat+dur,'_',1,'',tabColor, tabCol+dur,tabRow,tabLin+1]
                    tabs.append(newTab)    
                calcTabDims()          
                drawBars(True)
                return

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
            if tab[1] in sepIDs or tab[1][0] in ['{','}']:
                oldTabs.append(copy.deepcopy(tabs))
                tab=tabs.pop(idx)
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
        loadFile2(tfilepath=filepath)
        initBars()
        beatCursor=0
        metroMultIdx=0
        advMetroMult()
        drawBars(True)

    elif key in ('s') and state==4:#debug
        saveFile2(tfilepath=filepath)


    elif key in ('p','P'):
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
        
    # debug 
    #print (event)
    elif key in ('Home'):
        for idx,tab in enumerate(tabs):
            print (f"{idx:2d}> {tab}")

    elif key in ('Control_L','Alt_L','Shift_L'):
        pass # modifiers used in conjunction with other keys should not trigger "Key unknown" message.

    else:
        print (f"Key {key} unknown.")

    
def showHelp():
    helpWin.init(win,helpdir)
    helpWin.show()

def resizeWindow(event):
    global winDims
    winDims=[win.winfo_width(),win.winfo_height()]
    #drawBars(True)
def closeWindow():
    win.destroy()
def initWindow():
    global win
    sepSpacing=(8,8)

    # CREATE WINDOW
    win = tk.Tk()  
    win.option_add('*font',  '*font 9')

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
        win.lbMetroMult = tk.Label(win.metroFrame, text='1'+u'\u00D7',anchor="e",width=3,background='white',cursor="exchange")#"pirate")#"exchange")
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
    win.btnPlay.tooltip=CreateToolTip(win.btnPlay,"Start tabs\n scroll.")

    imgPath=os.path.join(icondir,"stop.png")
    win.imgStop= tk.PhotoImage(file=imgPath)
    win.btnStop=tk.Button(win.buttonframe,image=win.imgStop,relief=tk.FLAT,width=24,command=stopTabScroll,takefocus=0)
    win.btnStop.pack(side=tk.LEFT,padx=(1,0))
    win.btnStop.tooltip=CreateToolTip(win.btnStop,"Stop tabs\n scroll.")

    imgPath=os.path.join(icondir,"pause.png")
    win.imgPause= tk.PhotoImage(file=imgPath)
    win.btnPause=tk.Button(win.buttonframe,image=win.imgPause,relief=tk.FLAT,width=24,command=pauseTabScroll,takefocus=0)
    win.btnPause.pack(side=tk.LEFT,padx=(1,0))
    win.btnPause.tooltip=CreateToolTip(win.btnPause,"Pause tabs\n scroll.")

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
    win.btnAuto4Bars.tooltip=CreateToolTip(win.btnAuto4Bars,"Enlarge window and zoom out to fit tab \nwidth(page view) or height (linear view).")

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
    imgPath=os.path.join(icondir,"help.png")
    win.imgHelp = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnHelp=tk.Button(win.buttonframe,image=win.imgHelp,bg='white',relief=tk.FLAT,command=showHelp,takefocus=0)
    win.btnHelp.pack(side=tk.RIGHT,padx=(0,3))
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
    win.protocol("WM_DELETE_WINDOW", closeWindow) # custom function which sets winDestroyed so we can check state of win

initWindow()

initPlayer()
#loadFile2("Fee Ra Huri.tb")
#loadFile2("tutorial.tb")

# public domain tunes
loadFile2("Down By The Sally Gardens.tb")
#loadFile2("Fig For A Kiss.tb")
#loadFile2("testDecos.tb")
autoBars() # make sure tabs are fully on screen

drawBars(True)
#https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/canvas-methods.html

win.update()
toolbarWidth=win.btnHelp.winfo_x()+win.btnHelp.winfo_width()
win.minsize(toolbarWidth, 120)

win.after(50,showSplash)
tk.mainloop()
closePlayer()