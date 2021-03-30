# TODO
#   bug:tabs do not scroll in linear mode
#   do we want to delete consequetive spaces, bars, eot's
# use pip3 freeze >requirements.txt

import os
from datetime import datetime
import time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from pyscreenshot import grab

#GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)
icondir   = os.path.join(scriptdir,"icons")

import fluidsynth #pip3 install pyFluidSynth
import helpWin

#https://www.fluidsynth.org/api/LoadingSoundfonts.html
#https://github.com/nwhitehead/pyfluidsynth
fs=fluidsynth.Synth()
sfFlute=None
sfMetro=None
def initPlayer():
    global sfFlute, sfMetro
    fs.start(driver="alsa")
    
    #soundfontpath = os.path.join(scriptdir,"SynthThik.sf2")
    soundfontpath = os.path.join(scriptdir,"198-WSA percussion kit.SF2")
    sfMetro = fs.sfload(soundfontpath)
    fs.program_select(1, sfMetro, 0, 0)

    soundfontpath = os.path.join(scriptdir,"Tin_Whistle_AIR.sf2")
    sfFlute = fs.sfload(soundfontpath)
    fs.program_select(0, sfFlute, 0, 0)

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
decoIDs = ['^', '>', '=', '@', '~']

def setLowHigh():
    global noteNrs
    if playing: 
        win.varLow.set(noteNrs==noteNrsLow)
        return
    noteNrs=noteNrsLow if win.varLow.get() else noteNrsHigh

def startNote(noteId):    
    global oldNoteNr
    if noteId in noteNrs:
        noteNr=noteNrs[noteId]
        fs.noteon(0, noteNr,127)
        oldNoteNr=noteNr
    #print (f"On : {noteId}")
startNote('')
def endNote(noteId=None):    
    noteNr=oldNoteNr if noteId==None else noteNrs[noteId]
    fs.noteoff(0, noteNr)
    #print (f"Off: {noteId}")

#debug
'''
initPlayer()
keyIdx=0
while keyIdx<len(noteNrsHigh):
    startNote(list(noteNrsHigh.keys())[keyIdx])
    time.sleep(0.5)
    endNote(list(noteNrsHigh.keys())[keyIdx])
    keyIdx+=1
quit()
'''

def startTick():
    noteNr=12*9+2
    fs.noteoff(1, noteNr)
    fs.noteon(1, noteNr,127)

def closePlayer():
    fs.delete()

win=None
tabs=[]
title=""

def capTitle():
    global title
    title=" ".join([word.capitalize() for word in title.split(" ")])

def loadFile(filename=None,filepath=None):
    global tabs,bpm,title,beatsize,backColor
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return
    tabs.clear()
    texts.clear()
    initBars(20)
    beat=0
    cur=0
    tabColor=colors[2]
    backColor='#FFFFDE'
    tabRow=0
    tabCol=0
    tabLin=0
    #print (f"filename:{filename}|")
    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
    capTitle()
    try:
        with open(filepath,'r') as reader:
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
        #read notes
        lines=lines[1:]
        for line in lines:
            line=line.strip()
            if line in colors:
                tabColor=line
            elif line =='=':
                # first append newline
                name=eot
                dur=0
                style=''
                tabCol+=1
                tabLin+=1
                tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])   
                # next proceed to new line               
                tabRow+=1
                tabCol=0
            else:    
                data=line.split(",")
                if len(data)==3:
                    name=data[0].strip()
                    dur=data[1].strip()
                    dur=int(dur)                    
                    style=data[2].strip()
                    if name in (noteIDs+sepIDs+restIDs):
                        tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
                        #print ([beat,name,dur,style])
                    else:
                        print (f"Rejected: {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
                    beat+=dur                    
                    tabCol=tabCol+dur if dur>1 else tabCol+1
                    tabLin=tabLin+dur if dur>1 else tabLin+1
        
        win.title(f"Tin Whistle Helper - {os.path.basename(filepath).split('.')[0]}")
        calcTabDims()
    except Exception as e:
        print (f"Error reading tab file:{e}")

colors=['blue', 'purple3', '#00BBED','red','DeepPink3','magenta','orange','gold','brown','green','gray39','black',]
backcolors=['#7BDAFF','#FFC6F4','#CeF1Fd','#ffC0C0','#F7A8Db','#f1Bbf1','#FeE59a','#FFFFDE','#D3B4B4','#A0FdA0','#D4D4D4','#FFFFFF']
def newFile():
    global beatCursor,tabs,bpm,title,backColor
    bpm=120
    title="New File"
    tabs.clear()
    texts.clear()
    beatCursor=0
    tabColor=colors[2]
    backColor='#FFFFDE'
    for beat in range (20):
        tabs.append([beat,'_',1,'','green',beat,0,beat])                        

    win.title(f"Tin Whistle Helper - {title}")
    calcTabDims()
    drawBars(True)

textColor='black'
backColor='#FFFFDE'
texts=[]
def recalcBeats():
    beat,tabRow,tabCol,tabLin=0,0,0,0
    for idx,tab in enumerate(tabs):
        #[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab
        [_,name,dur,style,tabColor,_,_,_]=tab
        #print (f"{idx:2}> {tab}")
        tabs[idx]=[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]
        #print (f"{'  '}> {tabs[idx]}")
        #calc new beat, col, row and lin
        beat+=dur
        tabCol+=max(1,dur)
        tabLin+=max(1,dur)
        if name==eot:
            tabRow+=1
            tabCol=0
def nrTabRows():
    return tabs[-1][6]+1
def rowStart(rowNr):
    for idx in range(len(tabs)):
        if tabs[idx][6]==rowNr: return idx
def rowEnd(rowNr):
    for idx in range(len(tabs)-1,-1,-1):
        if tabs[idx][6]==rowNr: return idx
def stripSeps():
    #strips all seps at beginning or end of each row
    for rowNr in range(nrTabRows()):
        firstRowIdx=rowStart(rowNr)
        firstRowTab=tabs[firstRowIdx]
        if firstRowTab[1] in sepIDs: tabs.pop(firstRowIdx)
    for rowNr in range(nrTabRows()):
        lastRowIdx=rowEnd(rowNr)-1 # last is eot, we want to strip seps just before eot
        lastRowTab=tabs[lastRowIdx]
        if lastRowTab[1] in sepIDs and lastRowTab[1]!=eot: tabs.pop(lastRowIdx)
def gotoPrevBeat():
    global beatCursor
    for idx in range(len(tabs)-1,-1,-1):
        if tabs[idx][0]==beatCursor:
            for idx2 in range(idx-1,-1,-1):
                if tabs[idx2][2]>0: 
                    beatCursor=tabs[idx2][0]
                    return idx2
    return -1

def loadFile2(filename=None,filepath=None):
    global tabs,bpm,title
    global textColor,backColor,texts
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return

    tabs.clear()
    initBars(20)
    tabColor=colors[2]
    backColor='#FFFFDE'
    beat,tabRow,tabCol,tabLin=0,0,0,0 #just placeholders, real values will be calculated after loading by recalcBeats
    #print (f"filename:{filename}|")
    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
    capTitle()
    texts.clear()
    try:
        with open(filepath,'r') as reader:
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
                    cmd,val=line.split(':')
                    cmd=cmd.strip()
                    vals=val.split(",")
                    for idx in range(len(vals)): vals[idx]=vals[idx].strip()
                    if cmd=='color': textColor=vals[0]
                    if cmd=='back' : backColor=vals[0]
                    if cmd=='text' : texts.append(vals)
                else:           # read notes                
                    line=line.replace('  ',' , ') # double space is visual space between tabs
                    notes=line.split(" ")
                    notesfound=False
                    for note in notes:   
                        if note in colors:         
                            tabColor=note
                        else:   
                            name=note[0]
                            if len(note)>1: 
                                if note[1]=='#': name+='#'
                            dur=1+note.count('.')
                            style=''
                            if len(note)>1:
                                if note[-1] in '^>=@~/\\-':
                                    style = note[-1] 
                            if name in (noteIDs+restIDs+sepIDs):#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_','|',',']:
                                if name in sepIDs: dur=0 #('|',','): dur=0
                                tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
                                notesfound=True
                            else:
                                print (f"Rejected: [{note}] {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
                    if notesfound: # ignore lines with only color
                        name=eot
                        dur=0
                        style=''
                        tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
        
        win.title(f"Tin Whistle Helper - {os.path.basename(filepath).split('.')[0]}")
        recalcBeats()
        calcTabDims()
    except Exception as e:
        print (f"Error reading tab file:{e}")


def saveFile2(filename=None,filepath=None):
    global title
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return

    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
    capTitle()
    drawBars(True)
    eol='\n'
    try:
        with open(filepath,'w') as writer:   
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
                if name in ['|',',']:
                    if name==',': name=''
                    writer.write(f"{name} ")
                    #print(f"{name} ;")

    except Exception as e:
        print (f"Error writing tab file:{e}")
    
def saveFile():
    global beatCursor,metroMultIdx
    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    rep = filedialog.asksaveasfile(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=scriptdir,
                                        defaultextension="*.tbs",
                                        filetypes=[
                                            ("Tin Whistle Tab files", "*.tb")
                                    ])
    if (rep==None): return
    print (f"rep:{rep.name}")
    scriptpath=rep.name                                   # use first file in list
    if (scriptpath==None): return    
    ext=scriptpath[-3:]
    if ext=='.tb': 
        saveFile2(filepath=scriptpath)
    else: return        
    print (f"Saved:{scriptpath}")

    

def openFile():
    global beatCursor,metroMultIdx
    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    rep = filedialog.askopenfilenames(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=scriptdir,
                                        defaultextension="*.tbs",
                                        filetypes=[
                                            ("Tin Whistle Tab files", "*.tbs"),
                                            ("Tin Whistle Tab files", "*.tb")
                                    ])
    if (len(rep)==0): return
    scriptpath=rep[0]                                   # use first file in list
    if (scriptpath==None): return    
    ext=scriptpath[-3:]
    if ext=='tbs': 
        loadFile(filepath=scriptpath)
    elif ext=='.tb': 
        loadFile2(filepath=scriptpath)
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
winDims=[1024,800]

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

def drawBar(beat,dur,noteId,noteStyle='',tabColor='blue',tabCol=0,tabRow=0,tabLin=0):
    cvs=win.cvs

    # only draw if visible
    x1=beat2x(beat)
    x2=x1+beat2w(dur)
    y0=beat2y(beat)
    #yt=y0+beat2h()

    #if x2<0 or x1>winDims[0]: return False
    #if yt<0 or y0>winDims[1]: return False

    if noteId == '' : return False
    if noteId == ',': return False
    if noteId == eot: return False

    if noteId == '|': 
        tabColor = 'black'
        xm=beat2x(beat)-beat2w(1)/2
        y1=y0+holeInterval*0
        y2=y0+holeInterval*9 
        cvs.create_line(xm,y1,xm,y2,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        return

    holes=notes[noteId]

    if noteId    == '_':
        dashPatt =  (2,4)
        tabColor =  'gray80'
        noteId   =  '' # so no rest is printed
    else:
        dashPatt=None

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
            cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=180,style=arcstyle,dash=dashPatt)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill=fillColor,outline=tabColor,start=270,extent=180,style=arcstyle,dash=dashPatt)
        if openNote:
            cvs.create_line(x1+beatsize/2,y1,x2-beatsize/2,y1,fill=tabColor,dash=dashPatt) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
            cvs.create_line(x1+beatsize/2,y2,x2-beatsize/2,y2,fill=tabColor,dash=dashPatt)
        if (closedNote):
            cvs.create_rectangle(x1+beatsize/2,y1,x2-beatsize/2,y2,fill=fillColor,outline=tabColor,dash=dashPatt) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
        if halfNote:
            cvs.create_arc(x1, y2-beatsize, x1+beatsize, y2,fill=tabColor,outline=tabColor,start=90,extent=90,dash=dashPatt)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill=tabColor,outline=tabColor,start=0,extent=90,dash=dashPatt)
            cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill='white',outline=tabColor,start=270,extent=-90,style=tk.ARC,dash=dashPatt)
            cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill='white',outline=tabColor,start=0,extent=-90,style=tk.ARC,dash=dashPatt)
            cvs.create_rectangle(x1+beatsize/2,y1,x2-beatsize/2,ym,fill=tabColor,outline=tabColor,dash=dashPatt) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html
            cvs.create_line(x1+beatsize/2,y2,x2-beatsize/2+1,y2,fill=tabColor,dash=dashPatt) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html

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

    fnt=("Arial", int(beatsize*0.7))
    if noteStyle=='^':#tap/strike
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21C5',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='>':#cut
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21B4',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='>^':#roll (cut+tap)
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21B4\u21C5',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='=':#slide
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21D2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
        #cvs.create_text(x1,y1,text=u'\u27B2',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='@':#tonguing
        x1=beat2x(beat)+beat2w(1)/2
        y1=y0+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u1CC5',font=fnt,fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='~':#vibrato
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
    fnt=("Arial", int(beatsize*0.5))
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
    if inDrawBars: return
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
        win.cvs.config(scrollregion=(0,0,tabDims[0],int(tabDims[1]+beat2y(0)+yOffset)))        

        # redraw page outline
        #win.cvs.create_rectangle(beat2x(0)-beatsize, beat2y(0)-beatsize-titleHeight, beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize, fill=color)
        bBox=pageBBox()
        win.cvs.create_rectangle(bBox[0],bBox[1],bBox[2],bBox[3], fill=backColor)
        p1=(int(bBox[0]),int(bBox[1]))
        p2=(int(bBox[2]),int(bBox[3]))
        color=(0,255,0)
        t1=time.time()
        
        t1=time.time()
        rect=(int(bBox[0]),int(bBox[1]),int(bBox[2]),int(bBox[3]))
        
        # draw title and other text
        if len(texts)==0: #only display filename as title if no texts were given in the file
            x1=beat2x(0)
            y1=beat2y(0)
            win.cvs.create_text(x1,y1-titleHeight+beatsize*0.75,anchor=tk.W, font=("Arial", int(beatsize*1.2), "bold"),text=title,fill=textColor)
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
    if playing:
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
                toBeat=beat
        nrBeats=toBeat-fromBeat+1
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
def doCursorPlay():
    if int(beatCursor)!=round(beatCursor,1): return
    if metroMultIdx>0:
        metroInterval=2**(metroMultIdx-1)
        if (beatCursor%metroInterval)==0: startTick()

    if not win.varSound.get(): 
        endNote()
        return
    #print (f"{beatCursor}")
    for tab in tabs:
        beat,name,dur,style,tabColor,tabCol,tabRow,tabLin=tab
        if (beat==round(beatCursor,2)):
            if name in noteIDs:#['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G']:
                startNote(name)                
                delay=dur*int(60/bpm*1000)
                noteLength=delay-noteSilence if (noteSilence<delay) else delay
                win.after(noteLength,endNote,name)

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
            drawBars()
            doCursorPlay()

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
            messagebox.showinfo("Cannot play","In linear mode the full bar height should be fully visible.\nEnlarge window or use scroll wheel to zoom.")
            return
        #check if one row on screen
    else:        
        if nrBarLines<2 :
            messagebox.showinfo("Cannot play","In page mode, at least to bar lines should be fully visible.\nEnlarge window or use scroll wheel to zoom.")
            return
        if win.cvs.winfo_width()<tabDims[0]:
            messagebox.showinfo("Cannot play","In page mode, the window-width should accomodate all bars\nEnlarge window or use scroll wheel to zoom.")
            return
    global playing, beatCursor,delayJob, beatUpdate,xOffset,yOffset
    if playing: # restart from original
        initBars(beatsize) # don't reset zoom
        return    
    initTabScroll(firstPlayBeat)
    initBars(beatsize) # don't reset zoom
    playing=True
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
    scroll_start=win.vbar.get()
def drag_handler(event):
    global drag_begin
    drawDistance=( (event.x-drag_begin[0]),(event.y-drag_begin[1]) )
    cw,ch=win.cvs.winfo_width(),win.cvs.winfo_height()
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
    if event.state==4: # with control
        if event.num==4: zoomOut()
        if event.num==5: zoomIn()

def click(event):
    global beatCursor,firstPlayBeat
    eventX,eventY=event.x,event.y+win.vbar.get()[0]*tabDims[1]
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
    return (beat2x(0)-beatsize, beat2y(0)-beatsize-titleHeight, beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize)
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
    calcTabDims()
    drawBars(True)

def tabIdx():
    for idx,tab in enumerate(tabs):
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatCursor==beat and name not in sepIDs:
            return idx
        if beatCursor>beat and beatCursor<(beat+dur):
            if idx<len(tabs)-1:
                return idx+1
            else:
                return idx    
    return -1

delTab=None
delIdx=-1
def keypress(event):
    global beatCursor, tabs,delTab,delIdx,backColor,firstPlayBeat
    #print (event)
    key=event.keysym
    char=event.char
    state=event.state
    # basic info
    curCol,curRow=-1,-1
    dur=0
    idx=tabIdx()
    if idx>-1: _,_, dur,_,_, curCol,curRow,_=tabs[idx]

    # handle navigation
    if key in ('Left','KP_Left'): 
        pidx=idx-1
        pdur=0
        while pdur==0 and idx>0:
            _,_,pdur,_,_,_,_,_=tabs[pidx]
            pidx-=1
        if beatCursor>0:            beatCursor-=pdur
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor
    if key in ('Right','KP_Right'): 
        nidx=idx
        ndur=0
        while ndur==0 and idx<len(tabs)-2:
            _,_,ndur,_,_,_,_,_=tabs[nidx]
            nidx+=1
        if beatCursor<tabs[-1][0]:  beatCursor+=ndur
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor
    if key in ('Up','KP_Up'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow-1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor
    if key in ('Down','KP_Down'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow+1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        drawBars()
        doCursorPlay()
        firstPlayBeat=beatCursor

    # modify note
    if char in (noteIDs+restIDs):#['d','e','f','g','a','b','c','D','E','F','G','A','B','_','C']:
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
                tabs[idx][1]=char
                beatCursor+=dur  
                # make sure we have a rest so we can keep entering notes
                #if tabs[-1][1]!='_':
                beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[-1]
                newTab=[beat+dur,'_',1,'',tabColor, tabCol+dur,tabRow,tabLin+1]
                tabs.append(newTab)    
                calcTabDims()          
                drawBars(True)
                return

    # modify style/decorator
    if char in decoIDs or key=='Escape':
        deco= ' ' if key=='Escape' else char
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                tabs[idx][3]=deco
                drawBars(True)
    # modify length
    if char in ['1','2','3','4','5','6','7','8','9']:
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                newDur=int(char)                  
                delta=newDur-dur                        # store change in beats
                tabs[idx][2]=newDur                     # write new length
                #moveTabs(idx,delta)
                recalcBeats()
                calcTabDims()
                drawBars(True)
    # delete note
    if key in ('Delete','KP_Delete'):
        # delete tab
        tab=tabs.pop(idx)       
        # move tabs
        stripSeps()
        recalcBeats()
        # store del
        delTab=tab
        delIdx=idx
        # check if cursor on tab
        if idx>=(len(tabs)-1): 
            gotoPrevBeat()
        # redraw
        drawBars(True)
    # undo del
    if key in ('z') and state==4:
        if delTab!=None:
            tab=tabs[idx]
            tabs.insert(delIdx,delTab)
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=delTab
            #moveTabs(idx,dur)
            recalcBeats()
            calcTabDims()
            drawBars(True)
            delTab=None
    # insert note (before cursor)
    if key in ('Insert', 'KP_Insert','KP_0'):
        if state==1: idx+=1 # to append after
        tab=tabs[idx]
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        tabs.insert(idx,[beat,'_',1,'',tabColor, tabCol,tabRow,tabLin])
        recalcBeats()
        if state==1: beatCursor+=tabs[idx-1][2] # to append after and add dur
        calcTabDims()
        drawBars(True)
    # append note (after cursor)
    if key in ('plus', 'KP_Add'):
        if idx==len(tabs)-1:
            tab=tabs[idx]
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            tabs.append([beat+dur,'_',1,'',tabColor, tabCol+dur,tabRow,tabLin+dur])
            beatCursor+=dur
            calcTabDims()
            drawBars(True)
    # delete visual seperator
    if key=='BackSpace':
        if idx>0:
            idx-=1
            tab=tabs[idx]
            if tab[1] in sepIDs:
                #firstTabRow=tabs[idx][6]
                tab=tabs.pop(idx)
                recalcBeats()
                drawBars(True)

    # insert visual seperator of new line
    if char in sepIDs+[' '] or key=='Return':
        #print ("insert sep")
        if beatCursor==0: return # inserting seperator as first column will shift entire page (bug)
        sep=',' if char==' ' else char
        if key=='Return': sep=eot
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        tabs.insert(idx,[beat,sep,0,'',tabColor, tabCol,tabRow,tabLin])
        stripSeps() # make sure we do not place a sep at start of end of row
        recalcBeats()        
        calcTabDims()
        drawBars(True)

    # change tab color
    if key[0]=='F':
        print (int(state))
        if len(key)>1:
            colorNr=int(key[1:])-1
            if colorNr<len(colors):
                if state==0:
                    tab=tabs[idx]
                    tab[4]=colors[colorNr]
                if state==1:
                    backColor=backcolors[colorNr]
                drawBars(True)

    # replay from last start
    if  key=="Tab":
        if playing: stopTabScroll()
        startTabScroll()

    if key in ('p','P'):
        try:
            # autosize
            if state==1: autoBars()
            # hide cursor
            cpbeatCursor=beatCursor
            beatCursor=99999
            drawBars()
            win.cvs.update()
            bBox=pageBBox()
            # get screenshot bounding box
            x=win.winfo_rootx()+win.cvs.winfo_x()+bBox[0]
            y=win.winfo_rooty()+win.cvs.winfo_y()+bBox[1]
            x1=x+min(bBox[2],win.cvs.winfo_width())
            y1=y+min(bBox[3],win.cvs.winfo_height())
            im=grab(bbox=(x,y,x1,y1))
            # save image
            filename=os.path.join(scriptdir,title+".png")
            im.save(filename,format='png')
            print (f"Saved screenshot as '{filename}'")
            # show cursor
            beatCursor=cpbeatCursor
            drawBars()
        except Exception as e:
            print (f"Error saving screenshot file:{e}")
        
    # debug 
    #print (event)
    if key in ('Home'):
        for idx,tab in enumerate(tabs):
            print (f"{idx:2d}> {tab}")

    
def showHelp():
    helpWin.init(win)
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
    win.option_add('*Font', 'Verdana 9')

    # Set Window properties
    win.title(f"Tin Whistle Helper")
    win.geometry(f"{winDims[0]}x{winDims[1]}")
    backcolor=win["bg"]#"#DDDDDD"
    win.configure(background=backcolor)
    style=tk.SOLID
    iconpath=os.path.join(icondir,"TinWhistleHelper.png")
    win.tk.call('wm', 'iconphoto', win._w, tk.PhotoImage(file=iconpath))
    # set fonts

    win.buttonframe=tk.Frame(win,background="white",border=0,highlightthickness=0,relief=tk.FLAT)
    win.buttonframe.pack(side=tk.BOTTOM,padx=(0,0),pady=(0,0),ipadx=2,ipady=2,expand=False,fill=tk.X)
    win.btnLoad=tk.Button(win.buttonframe,text="Load",relief=tk.FLAT,width=4,command=openFile)
    win.btnLoad.pack(side=tk.LEFT,padx=(1,0))

    imgPath=os.path.join(icondir,"new.png")
    win.imgNew= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnNew=tk.Button(win.buttonframe,image=win.imgNew,relief=tk.FLAT,width=24,command=newFile)
    #win.btnNew=tk.Button(win.buttonframe,text="New",relief=tk.FLAT,width=4,command=newFile)
    win.btnNew.pack(side=tk.LEFT,padx=(1,0))

    imgPath=os.path.join(icondir,"save.png")
    win.imgSave= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnSave=tk.Button(win.buttonframe,image=win.imgSave,relief=tk.FLAT,width=24,command=saveFile)
    #win.btnSave=tk.Button(win.buttonframe,text="Save",relief=tk.FLAT,width=4,command=saveFile)
    win.btnSave.pack(side=tk.LEFT,padx=(1,0))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    imgPath=os.path.join(icondir,"chevLeftS.png")
    win.img2xSlower= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btn2xSlower=tk.Button(win.buttonframe,image=win.img2xSlower,relief=tk.FLAT,width=9,command=decrease2xBPM)
    win.btn2xSlower.pack(side=tk.LEFT,padx=(2,0))
    imgPath=os.path.join(icondir,"triLeftS.png")
    win.imgSlower= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnSlower=tk.Button(win.buttonframe,image=win.imgSlower,relief=tk.FLAT,width=9,command=decreaseBPM)
    win.btnSlower.pack(side=tk.LEFT,padx=(0,2))
    win.bpm = tk.StringVar()
    win.bpm.set(f"{bpm:3}")
    win.speed = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.bpm, width=3)     
    win.speed.pack(side=tk.LEFT,padx=(0,0))
    win.speedl = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',text="bpm",font=("*font",6))     
    win.speedl.pack(side=tk.LEFT,padx=(0,0))
    imgPath=os.path.join(icondir,"triRightS.png")
    win.imgFaster= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnFaster=tk.Button(win.buttonframe,image=win.imgFaster,relief=tk.FLAT,width=9,command=fasterBPM)
    win.btnFaster.pack(side=tk.LEFT,padx=(2,0))
    imgPath=os.path.join(icondir,"chevRightS.png")
    win.img2xFaster= tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btn2xFaster=tk.Button(win.buttonframe,image=win.img2xFaster,relief=tk.FLAT,width=9,command=faster2xBPM)
    win.btn2xFaster.pack(side=tk.LEFT,padx=(0,2))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,0))

    # countOff 
    win.varCountOff=tk.BooleanVar(value=False)
    win.cbCountOff=tk.Checkbutton(win.buttonframe,text='CO',variable=win.varCountOff)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbCountOff.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    #win.cbSound.config(font=("Courier", 12))
    win.cbCountOff.pack(side=tk.LEFT,padx=(2,2))

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
    
    win.lbMetroMult.bind("<Button-1>",advMetroMult)
    win.imMetro.bind("<Button-1>",advMetroMult)
    

    # play sound (see:https://en.wikipedia.org/wiki/Media_control_symbols)
    win.varSound=tk.BooleanVar(value=True)
    win.cbSound=tk.Checkbutton(win.buttonframe,text=u'\u266B\u269F',variable=win.varSound)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbSound.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    #win.cbSound.config(font=("Courier", 12))
    win.cbSound.pack(side=tk.LEFT,padx=(2,2))

    # Low whistle 
    win.varLow=tk.BooleanVar(value=False)
    win.cbLow=tk.Checkbutton(win.buttonframe,text='Low',variable=win.varLow,command=setLowHigh)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbLow.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    #win.cbSound.config(font=("Courier", 12))
    win.cbLow.pack(side=tk.LEFT,padx=(2,2))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))
    
    # play symbols (see:https://en.wikipedia.org/wiki/Media_control_symbols)
    win.btnStop=tk.Button(win.buttonframe,text=u'\u23F9',relief=tk.FLAT,width=1,command=stopTabScroll)
    win.btnStop.pack(side=tk.LEFT,padx=(1,0))
    win.btnPlay=tk.Button(win.buttonframe,text=u'\u25B6',relief=tk.FLAT,width=1,command=startTabScroll)
    win.btnPlay.pack(side=tk.LEFT,padx=(1,0))
    win.btnPause=tk.Button(win.buttonframe,text=u'\u23F8',relief=tk.FLAT,width=1,command=pauseTabScroll)
    win.btnPause.pack(side=tk.LEFT,padx=(1,0))

    win.beatCursor = tk.StringVar()
    win.beatCursor.set(f"{beatCursor:>5.1f}")
    win.beat = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.beatCursor,width=6)     
    win.beat.pack(side=tk.LEFT,padx=(3,3))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    imgPath=os.path.join(icondir,"linear.png")
    win.imgLinear = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    imgPath=os.path.join(icondir,"wrap.png")
    win.imgWrap = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.varLinear=tk.BooleanVar(value=False)
    win.cbLinear=tk.Checkbutton(win.buttonframe,variable=win.varLinear,command=reformatBars,
                                indicatoron=False,selectimage=win.imgWrap,image=win.imgLinear)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbLinear.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor,)
    #win.cbSound.config(font=("Courier", 12))
    win.cbLinear.pack(side=tk.LEFT,padx=(0,2))

    imgPath=os.path.join(icondir,"autosize.png")
    win.imgAuto = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnAuto4Bars=tk.Button(win.buttonframe,image=win.imgAuto,relief=tk.FLAT,command=autoBars)
    win.btnAuto4Bars.pack(side=tk.LEFT,padx=(1,0))

    imgPath=os.path.join(icondir,"shrink.png")
    win.imgShrink = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnShrink4Bars=tk.Button(win.buttonframe,image=win.imgShrink,relief=tk.FLAT,command=shrinkBars)
    win.btnShrink4Bars.pack(side=tk.LEFT,padx=(1,0))

    imgPath=os.path.join(icondir,"grow.png")
    win.imgGrow = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnGrow4Bars=tk.Button(win.buttonframe,image=win.imgGrow,relief=tk.FLAT,command=growWindow)
    win.btnGrow4Bars.pack(side=tk.LEFT,padx=(1,2))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    # zoom
    imgPath=os.path.join(icondir,"zoomout.png")
    win.imgZoomOut = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnZoomOut=tk.Button(win.buttonframe,image=win.imgZoomOut,bg='white',relief=tk.FLAT,command=zoomOut)
    win.btnZoomOut.pack(side=tk.LEFT,padx=(0,0))
    win.btnZoomOut.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)

    win.varZoom = tk.IntVar()
    win.varZoom.set(100)
    win.zoom = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.varZoom, anchor='e',width=3)     
    win.zoom.pack(side=tk.LEFT,padx=(0,0))
    win.zooml = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',text="%",anchor='e',font=("*font",6),width=1)     
    win.zooml.pack(side=tk.LEFT,padx=(0,0))

    imgPath=os.path.join(icondir,"zoomin.png")
    win.imgZoomIn = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnZoomIn=tk.Button(win.buttonframe,image=win.imgZoomIn,bg='white',relief=tk.FLAT,command=zoomIn)
    win.btnZoomIn.pack(side=tk.LEFT,padx=(0,0))
    win.btnZoomIn.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(8,8))

    # help
    imgPath=os.path.join(icondir,"help.png")
    win.imgHelp = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnHelp=tk.Button(win.buttonframe,image=win.imgHelp,bg='white',relief=tk.FLAT,command=showHelp)
    win.btnHelp.pack(side=tk.RIGHT,padx=(0,3))
    win.btnHelp.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)

    # make canvas
    win.vbar=tk.Scrollbar(win,orient=tk.VERTICAL)
    win.vbar.pack(side=tk.RIGHT,fill=tk.Y)
    win.cvs = tk.Canvas(win, bg="white" )
    win.cvs.pack(expand=True,fill=tk.BOTH,padx=(0,0),pady=(0,0))
    win.vbar.config(command=win.cvs.yview)
    win.cvs.config(yscrollcommand=win.vbar.set)

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
#loadFile("Fee Ra Huri.tbs")
#loadFile("tutorial.tbs")
loadFile2("tutorial.tb")
drawBars(True)
#https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/canvas-methods.html

win.update()
toolbarWidth=win.btnHelp.winfo_x()+win.btnHelp.winfo_width()
win.minsize(toolbarWidth, 120)

tk.mainloop()

closePlayer()