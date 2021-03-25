# TODO
# reflow tab blocks?
# make tab printable
# tab file editor
#   make cursor movable with keypad
# tabs do not scroll in linear mode

import os
from datetime import datetime
import time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

#GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

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
noteNrsHigh={'d':octM*12+2,'e':octM*12+4,'f#':octM*12+6,'g':octM*12+7,'a':octM*12+9,'b':octM*12+11,'c':octM*12+12,'c#':octM*12+13, 
             'D':octH*12+2,'E':octH*12+4,'F#':octH*12+6,'G':octH*12+7,'A':octH*12+9,'B':octH*12+11,'C#':octH*12+13,}
noteNrsLow= {'d':octL*12+2,'e':octL*12+4,'f#':octL*12+6,'g':octL*12+7,'a':octL*12+9,'b':octL*12+11,'c':octL*12+12,'c#':octL*12+13, 
             'D':octM*12+2,'E':octM*12+4,'F#':octM*12+6,'G':octM*12+7,'A':octM*12+9,'B':octM*12+11,'C#':octM*12+13}
noteNrs=noteNrsHigh 
oldNoteNr=0
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

def loadFile(filename=None,filepath=None):
    global tabs,bpm,title
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return
    tabs.clear()
    beat=0
    cur=0
    tabColor='blue'
    tabRow=0
    tabCol=0
    tabLin=0
    #print (f"filename:{filename}|")
    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
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
        win.bpm.set(f"{bpm:3} bpm")
        maxMetroMult()
        #read notes
        lines=lines[1:]
        for line in lines:
            line=line.strip()
            if line in colors:
                tabColor=line
            elif line =='=':
                tabRow+=1
                tabCol=0
            else:    
                data=line.split(",")
                if len(data)==3:
                    name=data[0].strip()
                    dur=data[1].strip()
                    dur=int(dur)                    
                    style=data[2].strip()
                    if name in ['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','','_','|','r']:
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

colors=['red','green','blue','yellow', 'orange', 'brown', 'black','grey']

def newFile():
    global beatCursor,tabs,bpm,title
    beatCursor=0
    tabs=[]
    for beat in range (20):
        tabs.append([beat,'_',1,'','green',beat,0,beat])                        

    bpm=120
    title="New File"
    win.title(f"Tin Whistle Helper - {title}")
    calcTabDims()
    drawBars(True)

def loadFile2(filename=None,filepath=None):
    global tabs,bpm,title
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return

    tabs.clear()
    beat=0
    cur=0
    tabColor=colors[2]
    tabRow=0
    tabCol=0
    tabLin=0
    #print (f"filename:{filename}|")
    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
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
        win.bpm.set(f"{bpm:3} bpm")
        maxMetroMult()
        #read notes
        lines=lines[1:]
        for line in lines:
            line=line.strip()
            if len(line)>0: # ignore empty lines
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
                        if name in ['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_','|',',']:
                            if name in ('|',','): dur=0
                            tabs.append([beat,name,dur,style,tabColor,tabCol,tabRow,tabLin])                        
                            if name != '|' and name!=',': 
                                beat+=dur                    
                            notesfound=True
                            #print ([beat,name,dur,style])
                        else:
                            print (f"Rejected: [{note}] {[beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]}")
                        tabCol=tabCol+dur if dur>1 else tabCol+1
                        tabLin=tabLin+dur if dur>1 else tabLin+1
                if notesfound: # ignore lines with only color
                    tabRow+=1
                    tabCol=0
                    tabLin+=1
        
        win.title(f"Tin Whistle Helper - {os.path.basename(filepath).split('.')[0]}")
        calcTabDims()
    except Exception as e:
        print (f"Error reading tab file:{e}")

def saveFile2(filename=None,filepath=None):
    global title
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return

    title=os.path.basename(filepath).split('.')[0].replace("_"," ")
    eol='\n'
    try:
        with open(filepath,'w') as writer:   
            writer.write(f"{bpm}{eol}")
            currColor=''
            currRow=0
            for tab in tabs:
                [beat,name,dur,style,tabColor,tabCol,tabRow,tabLin]=tab
                if currColor!=tabColor: 
                    writer.write(f"{tabColor} ")
                    currColor=tabColor
                if tabRow!=currRow:
                    writer.write(eol)
                    currRow=tabRow
                if name in ['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G','_']:
                    nlen=(dur-1)*'.'
                    writer.write(f"{name}{nlen}{style} ")
                    #print(f"{name}{nlen}{style} ;")
                if name in ['|',',']:
                    if name==',': name=''
                    writer.write(f"{name} ")
                    print(f"{name} ;")

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
        'c' :(0,1,1,0,0,0,''),
        'c#':(0,0,0,0,0,0,''),
        'D' :(0,1,1,1,1,1,'+'),
        'E' :(1,1,1,1,1,0,'+'),
        'F#':(1,1,1,1,0,0,'+'),
        'G' :(1,1,1,0,0,0,'+'),
        'A' :(1,1,0,0,0,0,'+'), 
        'B' :(1,0,0,0,0,0,'+'),
        'C#':(0,1,1,0,0,0,'+'),
        '_' :(0,0,0,0,0,0,'')#rest
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
        if x>tabDims[0]: tabDims[0]=x
        if y>tabDims[1]: tabDims[1]=y

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
        x=xOffset+dragXOffset+tabLin*barInterval
    else:
        x=xOffset+dragXOffset+tabCol*barInterval
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
                y=yOffset+dragYOffset
            else:    
                y=yOffset+dragYOffset+tabRow*holeInterval*10
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
    yt=y0+beat2h()

    if x2<0 or x1>winDims[0]: return False
    if yt<0 or y0>winDims[1]: return False

    if noteId == '': return False
    if noteId == ',': return False

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
        if (openNote):
            fillColor='white'
            arcstyle=tk.ARC
        else:    
            fillColor=tabColor
            arcstyle=tk.CHORD
        x1=beat2x(beat)
        x2=x1+beat2w(dur)
        y1=y0+holeInterval*(holeNr+1)
        y2=y0+holeInterval*(holeNr+1)+beatsize 
        ym=(y1+y2)/2
        r=beatsize/2
        cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=180,style=arcstyle,dash=dashPatt)
        cvs.create_arc(x2-beatsize, y2-beatsize, x2, y2,fill=fillColor,outline=tabColor,start=270,extent=180,style=arcstyle,dash=dashPatt)
        if openNote:
            cvs.create_line(x1+beatsize/2,y1,x2-beatsize/2,y1,fill=tabColor,dash=dashPatt) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
            cvs.create_line(x1+beatsize/2,y2,x2-beatsize/2,y2,fill=tabColor,dash=dashPatt)
        else:    
            cvs.create_rectangle(x1+beatsize/2,y1,x2-beatsize/2,y2,fill=fillColor,outline=tabColor,dash=dashPatt) #https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_arc.html

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
def drawBars(force=False):
    global xOffset,yOffset,cursorBar,cursorBar2,oldOffsets,oldBeatsize    
  
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

        # redraw page outline
        color="#FFFFDE"
        #win.cvs.create_rectangle(beat2x(0)-beatsize, beat2y(0)-beatsize-titleHeight, beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize, fill=color)
        bBox=pageBBox()
        win.cvs.create_rectangle(bBox[0],bBox[1],bBox[2],bBox[3], fill=color)

        # draw title
        x1=beat2x(0)
        y1=beat2y(0)
        win.cvs.create_text(x1,y1-titleHeight+beatsize*0.75,anchor=tk.W, font=("Arial", int(beatsize*1.2), "bold"),text=title)

        # redraw tabs
        nrDrawn=0
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            didDraw=drawBar(beat,dur,name,style,tabColor,tabCol,tabRow,tabLin)
            if didDraw: nrDrawn+=1
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
            if name in ['a','b','c','c#','d','e','f#','g','A','B','C#','D','E','F#','G']:
                startNote(name)                
                delay=dur*int(60/bpm*1000)
                noteLength=delay-noteSilence if (noteSilence<delay) else delay
                win.after(noteLength,endNote,name)

bpm=120
beatUpdate=0.1
playing=False
startTime=0
delayJob=None
def stopTabScroll():
    global playing,beatCursor
    playing=False
    beatCursor=0
    endNote()
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
            win.beatCursor.set(f"beat: {beatCursor:>5.1f}")
            # stop play
            stopTabScroll()
        else:
            delay=int((60/bpm*1000)*beatUpdate)
            delayJob=win.after(delay, advTabScroll)
            beatCursor+=beatUpdate
            beatCursor=round(beatCursor,3)
            win.beatCursor.set(f"beat: {beatCursor:>5.1f}")
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
    win.beatCursor.set(f"beat: {beatCursor:.1f}")
    setBeatUpdate()
    delay=int((60/bpm*1000)*beatUpdate)

def startTabScroll():
    if not allBarsOnScreen() and not win.varLinear.get():
        messagebox.showinfo("Cannot play","Play can only start if in linear mode or \nif all bars are visible.\nUse scroll wheel to zoom or the 'auto'-button.")
        return
    global playing, beatCursor,delayJob, beatUpdate,xOffset,yOffset,dragXOffset,dragYOffset
    if playing: return
    initTabScroll(0)
    initBars(beatsize) # don't reset zoom
    playing=True
    #resetView(None)
    dragXOffset=0
    dragYOffset=0
    drawBars()
    countOff()
    #doCursorPlay()
    #delayJob=win.after(delay, advTabScroll)

def decreaseBPM():
    if playing: return
    global bpm
    bpm=bpm-5
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3} bpm")
def decrease2xBPM():
    if playing: return
    global bpm
    bpm=int(bpm/2)
    if bpm<5: bpm=5
    win.bpm.set(f"{bpm:3} bpm")
def fasterBPM():
    if playing: return
    global bpm
    bpm=bpm+5
    if bpm>960: bpm=960
    win.bpm.set(f"{bpm:3} bpm")
    maxMetroMult()
def faster2xBPM():
    if playing: return
    global bpm
    bpm=int(bpm*2)
    if bpm>960: bpm=960
    win.bpm.set(f"{bpm:3} bpm")
    maxMetroMult()

drag_begin=0
dragXOffset=0
dragYOffset=0
drag_start=None
def drag_enter(event):
    global drag_begin,drag_start
    drag_begin=[event.x,event.y]
    drag_start=time.time()
def drag_handler(event):
    global drag_begin,dragXOffset,dragYOffset
    drawDistance=( (event.x-drag_begin[0]),(event.y-drag_begin[1]) )
    dragXOffset=dragXOffset+drawDistance[0]
    dragYOffset=dragYOffset+drawDistance[1]
    #if dragXOffset>0: dragXOffset=0
    drag_begin=[event.x,event.y]
    drawBars(True)
def drag_end(event):
    if (time.time()-drag_start)<0.2: 
        click(event)
        return
    global dragXOffset,dragYOffset
    drawDistance=( (event.x-drag_begin[0]),(event.y-drag_begin[1]) )
    dragXOffset=dragXOffset+drawDistance[0]
    dragYOffset=dragYOffset+drawDistance[1]
    #if dragXOffset>0: dragXOffset=0
    drawBars(True)
def scrollwheel(event):
    global beatsize
    if (event.num==4):
        beatsize=beatsize-1
    if (event.num==5):   
        beatsize=beatsize+1
    #print (f"event:{event}")
    if beatsize<minBeatsize: beatsize=minBeatsize
    if beatsize>maxBeatsize: beatsize=maxBeatsize
    initBars(beatsize)
    calcTabDims()
    drawBars(True)
def click(event):
    global beatCursor
    for tab in tabs:
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        x=beat2x(beat)
        y=beat2y(beat)
        w=beat2w(dur)
        h=beat2h()
        if (event.x>=x and event.x<(x+w) and 
            event.y>=y and event.y<(y+h)):
           beatCursor=beat
           win.beatCursor.set(f"beat: {beatCursor:.1f}")
           drawBars()   
           initTabScroll(beat)    # set for play
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
    global dragXOffset,dragYOffset
    dragXOffset=0
    dragYOffset=0
    initBars(20)
    drawBars(True)
def fitButtonState():
    if win.varLinear.get(): 
        win.btnShrink4Bars.config(state='disabled')
        win.btnGrow4Bars.config(state='disabled')
        win.btnAuto4Bars.config(state='disabled')
    else:    
        win.btnShrink4Bars.config(state='normal')
        win.btnGrow4Bars.config(state='normal')
        win.btnAuto4Bars.config(state='normal')

def pageBBox():
    return (beat2x(0)-beatsize, beat2y(0)-beatsize-titleHeight, beat2x(0)+tabDims[0]+beatsize, beat2y(0)+tabDims[1]+beatsize)
def allBarsOnScreen():    
    bBox=pageBBox()
    toolH=win.buttonframe.winfo_height()
    menuH=24
    #return (tabDims[0]<winDims[0] and (tabDims[1]+2*beatsize+toolH)<winDims[1]) 
    return (bBox[2]<winDims[0] and bBox[3]<(winDims[1]-toolH) )
def shrinkBars():
    global beatsize
    oldBeatsize=beatsize
    while (not allBarsOnScreen()) and beatsize>minBeatsize: #+56 for height of toolbar
        beatsize-=0.25
        initBars(beatsize)
        calcTabDims()
    if not allBarsOnScreen():
        beatsize=oldBeatsize
        initBars(beatsize)
        calcTabDims()
        messagebox.showinfo("No fit found.","Try enlarging window or \na smaller tbs file.")
        return
    drawBars(True)   
def growWindow():
    global winDims
    oldWinDims=winDims
    winDims[0]=tabDims[0]
    winDims[1]=tabDims[1]+win.buttonframe.winfo_height()+2*beatsize
    if winDims[0]<1024: winDims[0]=1024
    if winDims[1]<320: winDims[1]=320
    while (not allBarsOnScreen()): #+56 for height of toolbar
        winDims=[int(winDims[0]+10),int(winDims[1]+10)]
    if not allBarsOnScreen():
        winDims=oldWinDims
        messagebox.showinfo("No fit found.","Try zoom out or \na smaller tbs file.")
        return
    win.geometry(f'{winDims[0]:.0f}x{winDims[1]:.0f}+{win.winfo_x()}+{win.winfo_y()}')    
    win.update()
    winDims=[win.winfo_width(),win.winfo_height()]
    initBars()#just to be sure all is updated
    drawBars(True)   
def autoBars():
    growWindow()
    shrinkBars()
    growWindow()# to shrink window if width or height is too large

def reformatBars():
    fitButtonState()
    calcTabDims()
    drawBars(True)

def tabIdx():
    for idx,tab in enumerate(tabs):
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        if beatCursor==beat and name!='|' and name !=',':
            return idx
        if beatCursor>beat and beatCursor<(beat+dur):
            if idx<len(tabs)-1:
                return idx+1
            else:
                return idx    
    return -1
def moveTabs(afterTabIdx, nrBeats):
    delta=nrBeats
    firstTabRow=tabs[afterTabIdx][6]
    for tailIdx in range(afterTabIdx+1,len(tabs)):  # move following tabs according to change
        tabs[tailIdx][0]+=delta          #beat
        if tabs[tailIdx][6]==firstTabRow:#tabCol
            tabs[tailIdx][5]+=delta 
        tabs[tailIdx][7]+=delta          #tabLin

delTab=None
delIdx=-1
def keypress(event):
    global beatCursor, tabs,delTab,delIdx
    #print (event)
    key=event.keysym
    char=event.char
    state=event.state
    # basic info
    curCol,curRow=-1,-1
    dur,pdur=0,0
    idx=tabIdx()
    if idx>-1: _,_, dur,_,_, curCol,curRow,_=tabs[idx]
    pidx=idx-1
    while pdur==0 and idx>0:
      _,_,pdur,_,_,_,_,_=tabs[pidx]
      pidx-=1

    # handle navigation
    if key in ('Left','KP_Left'): 
        if beatCursor>0:            beatCursor-=pdur
        drawBars()
    if key in ('Right','KP_Right'): 
        if beatCursor<tabs[-1][0]:  beatCursor+=dur
        drawBars()
        return
    if key in ('Up','KP_Up'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow-1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        drawBars()
    if key in ('Down','KP_Down'): 
        for tab in tabs:
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if tabRow==curRow+1 and curCol>=tabCol and curCol<(tabCol+dur): beatCursor=beat
        drawBars()

    # modify note
    if char in ['a','b','c','c','d','e','f','g','A','B','C','D','E','F','G','_']:
        if char=='f': char='f#'
        if char=='F': char='F#'
        print (state)
        if char=='c' and state==8: char='c#'
        for idx,tab in enumerate(tabs):
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
            if beatCursor>=beat and beatCursor<(beat+dur):
                tabs[idx][1]=char
                beatCursor+=dur  
                # make sure we have a rest so we can keep entering notes
                if tabs[-1][1]!='_':
                    beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[-1]
                    newTab=[beat+dur,'_',1,'',tabColor, tabCol+1,tabRow,tabLin+1]
                    tabs.append(newTab)    
                    calcTabDims()          
                drawBars(True)
                return

    # modify style/decorator
    if char in ['^', '>', '=', '@', '~'] or key=='Escape':
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
                moveTabs(idx,delta)
                drawBars(True)
    # delete note
    if key in ('Delete','KP_Delete'):
        tab=tabs.pop(idx)
        moveTabs(idx-1,-tab[2])
        if idx>=len(tabs): beatCursor=tabs[-1][0]
        drawBars(True)
        delTab=tab
        delIdx=idx
    # undo del
    if key in ('z') and state==4:
        if delTab!=None:
            tab=tabs[idx]
            tabs.insert(delIdx,delTab)
            beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=delTab
            moveTabs(idx,dur)
            calcTabDims()
            drawBars(True)
            delTab=None
    # insert note (before cursor)
    print (event)
    if key in ('Insert', 'KP_Insert','KP_0'):
        if state==1: idx+=1 # to append after
        tab=tabs[idx]
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tab
        tabs.insert(idx,[beat,'_',1,'',tabColor, tabCol,tabRow,tabLin])
        moveTabs(idx,1)
        if state==1: beatCursor+=1 # to append after
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
            if tab[1] in ('|',','):
                firstTabRow=tabs[idx][6]
                tab=tabs.pop(idx)
                for tailIdx in range(idx,len(tabs)):  # move following tabs according to change
                    if tabs[tailIdx][6]==firstTabRow: # tabCol
                        tabs[tailIdx][5]-=1
                    tabs[tailIdx][7]-=1               # tabLin
                drawBars(True)

    # insert visual seperator
    if char in ('|',' '):
        print ("insert sep")
        sep=',' if char==' ' else char
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        tabs.insert(idx,[beat,sep,0,'',tabColor, tabCol,tabRow,tabLin])
        for tailIdx in range(idx+1,len(tabs)):  # move following tabs according to change
            if tabs[tailIdx][6]==tabRow:#tabCol
                tabs[tailIdx][5]+=1
            tabs[tailIdx][7]+=1         #tabLin
        calcTabDims()
        drawBars(True)

    # del new line
    if key=='BackSpace':
        idx+=1
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        if tabCol==0 and idx>0:
            _,_,appDur,_,_,appCol,_,_=tabs[idx-1]
            appDelta=appCol+appDur
            for tailIdx in range(idx,len(tabs)):  # move following tabs according to change
                if tabs[tailIdx][6]==tabRow:      # tabCol
                    tabs[tailIdx][5]=tabs[tailIdx][5]+appDelta
                tabs[tailIdx][6]-=1               # tabRow
            calcTabDims()
            drawBars(True)

    # insert new line
    if key=='Return':
        beat,name,dur,style,tabColor, tabCol,tabRow,tabLin=tabs[idx]
        for tailIdx in range(idx,len(tabs)):  # move following tabs according to change
            if tabs[tailIdx][6]==tabRow:      # tabCol
                tabs[tailIdx][5]=tabs[tailIdx][5]-tabCol 
            tabs[tailIdx][6]+=1               # tabRow
        calcTabDims()
        drawBars(True)

    if key[0]=='F':
        if len(key)>1:
            colorNr=int(key[1:])
            if colorNr<len(colors):
                tab=tabs[idx]
                tab[4]=colors[colorNr]
                drawBars(True)

    print ("change title")


    # debug 
    if key in ('Tab'):
        for idx,tab in enumerate(tabs):
            print (f"{idx:2d}> {tab}")

    
def showHelp():
    helpWin.init(win)
    helpWin.show()

def resizeWindow(event):
    global winDims
    winDims=[win.winfo_width(),win.winfo_height()]
    drawBars(True)
def closeWindow():
    win.destroy()
def initWindow():
    global win

    # CREATE WINDOW
    win = tk.Tk()  
    win.option_add('*Font', 'Verdana 9')

    # Set Window properties
    win.title(f"Tin Whistle Helper")
    win.geometry(f"{winDims[0]}x{winDims[1]}")
    backcolor=win["bg"]#"#DDDDDD"
    win.configure(background=backcolor)
    style=tk.SOLID
    iconpath=os.path.join(scriptdir,"TinWhistleHelper.png")
    win.tk.call('wm', 'iconphoto', win._w, tk.PhotoImage(file=iconpath))
    # set fonts

    win.buttonframe=tk.Frame(win,background="white",border=0,highlightthickness=0,relief=tk.FLAT)
    win.buttonframe.pack(side=tk.BOTTOM,padx=(0,0),pady=(0,0),ipadx=2,ipady=2,expand=False,fill=tk.X)
    win.btnLoad=tk.Button(win.buttonframe,text="Load",relief=tk.FLAT,width=4,command=openFile)
    win.btnLoad.pack(side=tk.LEFT,padx=(2,2))

    win.btnNew=tk.Button(win.buttonframe,text="New",relief=tk.FLAT,width=4,command=newFile)
    win.btnNew.pack(side=tk.LEFT,padx=(2,2))

    win.btnSave=tk.Button(win.buttonframe,text="Save",relief=tk.FLAT,width=4,command=saveFile)
    win.btnSave.pack(side=tk.LEFT,padx=(2,2))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(16,16))

    win.btn2xSlower=tk.Button(win.buttonframe,text='\u00BD\u00D7',relief=tk.FLAT,width=1,command=decrease2xBPM)
    win.btn2xSlower.pack(side=tk.LEFT,padx=(2,2))
    win.btnSlower=tk.Button(win.buttonframe,text=u'\u23EA',relief=tk.FLAT,width=1,command=decreaseBPM)
    win.btnSlower.pack(side=tk.LEFT,padx=(2,2))
    win.bpm = tk.StringVar()
    win.bpm.set(f"{bpm:3} bpm")
    win.speed = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.bpm)     
    win.speed.pack(side=tk.LEFT,padx=(3,3))
    win.btnFaster=tk.Button(win.buttonframe,text=u'\u23E9',relief=tk.FLAT,width=1,command=fasterBPM)
    win.btnFaster.pack(side=tk.LEFT,padx=(2,2))
    win.btnFaster=tk.Button(win.buttonframe,text='2'+'\u00D7',relief=tk.FLAT,width=1,command=faster2xBPM)
    win.btnFaster.pack(side=tk.LEFT,padx=(2,2))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(16,16))

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
    imgPath=os.path.join(scriptdir,"Metronome18.png")
    imgPathG=os.path.join(scriptdir,"Metronome18G.png")
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
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(16,16))
    
    # play symbols (see:https://en.wikipedia.org/wiki/Media_control_symbols)
    win.btnStop=tk.Button(win.buttonframe,text=u'\u23F9',relief=tk.FLAT,width=1,command=stopTabScroll)
    win.btnStop.pack(side=tk.LEFT,padx=(2,2))
    win.btnPlay=tk.Button(win.buttonframe,text=u'\u25B6',relief=tk.FLAT,width=1,command=startTabScroll)
    win.btnPlay.pack(side=tk.LEFT,padx=(2,2))
    win.btnPause=tk.Button(win.buttonframe,text=u'\u23F8',relief=tk.FLAT,width=1,command=pauseTabScroll)
    win.btnPause.pack(side=tk.LEFT,padx=(2,2))

    win.beatCursor = tk.StringVar()
    win.beatCursor.set(f"beat: {beatCursor:>5.1f}")
    win.beat = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.beatCursor,width=12)     
    win.beat.pack(side=tk.LEFT,padx=(3,3))

    # draw sep
    win.separator = ttk.Separator(win.buttonframe,orient='vertical').pack(side=tk.LEFT,fill='y',padx=(16,16))

    imgPath=os.path.join(scriptdir,"linear.png")
    win.imgLinear = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    imgPath=os.path.join(scriptdir,"wrap.png")
    win.imgWrap = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.varLinear=tk.BooleanVar(value=False)
    win.cbLinear=tk.Checkbutton(win.buttonframe,variable=win.varLinear,command=reformatBars,
                                indicatoron=False,selectimage=win.imgWrap,image=win.imgLinear)
    footerbgcolor='white'
    footerfgcolor='black'
    win.cbLinear.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor,)
    #win.cbSound.config(font=("Courier", 12))
    win.cbLinear.pack(side=tk.LEFT,padx=(2,2))

    imgPath=os.path.join(scriptdir,"autosize.png")
    win.imgAuto = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnAuto4Bars=tk.Button(win.buttonframe,image=win.imgAuto,relief=tk.FLAT,command=autoBars)
    win.btnAuto4Bars.pack(side=tk.LEFT,padx=(2,2))

    imgPath=os.path.join(scriptdir,"shrink.png")
    win.imgShrink = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnShrink4Bars=tk.Button(win.buttonframe,image=win.imgShrink,relief=tk.FLAT,command=shrinkBars)
    win.btnShrink4Bars.pack(side=tk.LEFT,padx=(2,2))

    imgPath=os.path.join(scriptdir,"grow.png")
    win.imgGrow = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnGrow4Bars=tk.Button(win.buttonframe,image=win.imgGrow,relief=tk.FLAT,command=growWindow)
    win.btnGrow4Bars.pack(side=tk.LEFT,padx=(2,2))

    imgPath=os.path.join(scriptdir,"help.png")
    win.imgHelp = tk.PhotoImage(file=imgPath)#.subsample(4,4)
    win.btnHelp=tk.Button(win.buttonframe,image=win.imgHelp,relief=tk.FLAT,command=showHelp)
    win.btnHelp.pack(side=tk.LEFT,padx=(2,2))

    # make canvas
    win.cvs = tk.Canvas(win, bg="white" )
    win.cvs.pack(expand=True,fill=tk.BOTH,padx=(0,0),pady=(0,0))
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
#drawBars(True)
#https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/canvas-methods.html

tk.mainloop()

closePlayer()