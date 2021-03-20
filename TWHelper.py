import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

#GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

import fluidsynth #pip3 install pyFluidSynth
import time

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
noteNrsHigh={'d':octM*12+2,'e':octM*12+4,'f#':octM*12+6,'g':octM*12+7,'a':octM*12+9,'b':octM*12+11,'c':octM*12+12, 
             'D':octH*12+2,'E':octH*12+4,'F#':octH*12+6,'G':octH*12+7,'A':octH*12+9,'B':octH*12+11,'C':octH*12+12,}
noteNrsLow= {'d':octL*12+2,'e':octL*12+4,'f#':octL*12+6,'g':octL*12+7,'a':octL*12+9,'b':octL*12+11,'c':octL*12+12, 
             'D':octM*12+2,'E':octM*12+4,'F#':octM*12+6,'G':octM*12+7,'A':octM*12+9,'B':octM*12+11,'C':octM*12+12}
noteNrs=noteNrsHigh 
oldNoteNr=0
def setLowHigh():
    global noteNrs
    noteNrs=noteNrsLow if win.varLow.get() else noteNrsHigh

def startNote(noteId):    
    global oldNoteNr
    if noteId in noteNrs:
        noteNr=noteNrs[noteId]
        fs.noteon(0, noteNr,127)
        oldNoteNr=noteNr
    #print (f"On : {noteId}")
def endNote(noteId=None):    
    noteNr=oldNoteNr if noteId==None else noteNrs[noteId]
    fs.noteoff(0, noteNr)
    #print (f"Off: {noteId}")
def startTick():
    noteNr=12*9+2
    fs.noteoff(1, noteNr)
    fs.noteon(1, noteNr,127)

def closePlayer():
    fs.delete()

win=None
tabs=[]
def loadFile(filename=None,filepath=None):
    global tabs,bpm
    if filepath==None:
        filepath=os.path.join(scriptdir,filename)        
    if not os.path.isfile(filepath): return
    tabs.clear()
    beat=0
    cur=0
    tabColor='blue'
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
            if line in ['red','green','blue','yellow', 'orange', 'brown', 'black','grey']:
                tabColor=line
            else:    
                data=line.split(",")
                if len(data)==3:
                    name=data[0].strip()
                    dur=data[1].strip()
                    dur=int(dur)
                    style=data[2].strip()
                    if name in ['a','b','c','d','e','f#','g','A','B','C','D','E','F#','G','','_','|','r']:
                        tabs.append([beat,name,dur,style,tabColor])
                        #print ([beat,name,dur,style])
                    else:
                        print (f"Rejected: {[beat,name,dur,style]}")
                    beat+=dur
        
        win.title(f"Tin Whistle Helper - {os.path.basename(filepath).split('.')[0]}")

    except Exception as e:
        print (f"Error reading tab file:{e}")

def openFile():
    global beatCursor,metroMultIdx
    stopTabScroll() # needed otherwise timer prevents updates of filedialog
    rep = filedialog.askopenfilenames(                  # open dialog so user can select file
                                        parent=win,
                                        initialdir=scriptdir,
                                        defaultextension="*.tbs",
                                        filetypes=[
                                            ("Tin Whistle Tab files", "*.tbs"),
        ])
    if (len(rep)==0): return
    scriptpath=rep[0]                                   # use first file in list
    if (scriptpath==None): return    
    loadFile(filepath=scriptpath)
    initBars()
    beatCursor=0
    metroMultIdx=0
    advMetroMult()
    drawBars()
    print (f"Loaded:{scriptpath}")

notes={ 'a' :(1,1,0,0,0,0,''), 
        'b' :(1,0,0,0,0,0,''),
        'c' :(0,1,1,0,0,0,''),
        'd' :(1,1,1,1,1,1,''),
        'e' :(1,1,1,1,1,0,''),
        'f#':(1,1,1,1,0,0,''),
        'g' :(1,1,1,0,0,0,''),
        'A' :(1,1,0,0,0,0,'+'), 
        'B' :(1,0,0,0,0,0,'+'),
        'C' :(0,1,1,1,0,0,'+'),
        'D' :(0,1,1,1,1,1,'+'),
        'E' :(1,1,1,1,1,0,'+'),
        'F#':(1,1,1,1,0,0,'+'),
        'G' :(1,1,1,0,0,0,'+'),
        '_' :(0,0,0,0,0,0,'')#rest
        }

beatsize=20
barInterval=1.2*beatsize
holeInterval=1.5*beatsize
xOffset=beatsize
yOffset=beatsize
beatCursor=0
winDims=[1024,int(yOffset+holeInterval*11)+32]


def initBars(newBeatsize=None):
    global beatsize,barInterval,holeInterval,xOffset,yOffset, beatCursor
    if newBeatsize is not None:
        beatsize=newBeatsize
    barInterval=1.2*beatsize
    holeInterval=1.5*beatsize
    xOffset=beatsize
    yOffset=beatsize

def beat2x(beat):
    #print (f"beat2x: {beat}")
    delta=0
    space=2
    for tab in tabs:
        [tabBeat,name,dur,style,tabColor]=tab        
        #print (f"  tab: {tab}")
        if (beat>=tabBeat):
            if dur==0:
                delta+=space
                #print ("DELTA")
    x=xOffset+dragOffset+(beat+delta)*barInterval
    return x

def beat2w(dur):
    w=(dur-1)*barInterval+beatsize
    return w

def drawBar(beat,dur,noteId,noteStyle='',tabColor='blue'):
    cvs=win.cvs

    if noteId == '': return

    if noteId == '|': 
        tabColor = 'black'
        xm=beat2x(beat)-beat2w(1)
        y1=yOffset+holeInterval*0
        y2=yOffset+holeInterval*9 
        cvs.create_line(xm,y1,xm,y2,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        return

    holes=notes[noteId]

    if noteId    == '_':
        dashPatt =  (2,4)
        tabColor =  'gray80'
        noteId   =  '' # so no rest is printed
    else:
        dashPatt=None

    # only draw if visible
    x1=beat2x(beat)
    x2=x1+beat2w(dur)
    if x2<0 or x1>winDims[0]: return

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
        y1=yOffset+holeInterval*(holeNr+1)
        y2=yOffset+holeInterval*(holeNr+1)+beatsize 
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
        y1=yOffset+holeInterval*7
        y2=yOffset+holeInterval*7+beatsize 
        xm=(x1+x2)/2
        ym=(y1+y2)/2
        cvs.create_line(x1+2,ym,x2-2,ym,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
        cvs.create_line(xm,y1+2,xm,y2-2,fill=tabColor,width=2)

    if noteStyle=='^':#tap/strike
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21C5',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='>':#cut
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21B4',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='>^':#roll (cut+tap)
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u21B4\u21C5',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='=':#slide
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u27B2',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='@':#tonguing
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u1CC5',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='~':#vibrato
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_text(x1,y1,text=u'\u223F',fill=tabColor)# https://www.w3schools.com/graphics/canvas_text.asp
    if noteStyle=='/':#join
        x1=beat2x(beat)+beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_arc(x1, y1, x1+beatsize, y1+beatsize,fill=fillColor,outline=tabColor,start=90,extent=90,style=arcstyle,width=2)
        cvs.create_line(x1+beat2w(1)/2,y1,x1+beat2w(1)/2+beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='\\':
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_arc(x2-beatsize, y1, x2, y1+beatsize,fill=fillColor,outline=tabColor,start=0,extent=90,style=arcstyle,width=2)
        cvs.create_line(x2-beat2w(1)/2,y1,x2-beat2w(1)/2-beat2w(dur),y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
    if noteStyle=='-':
        x1=beat2x(beat)+beat2w(1)/2
        x2=beat2x(beat)+beat2w(dur)-beat2w(1)/2
        y1=yOffset+holeInterval*0.5
        cvs.create_line(x1,y1,x2,y1,fill=tabColor,width=2) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

    # Draw note Name
    noteId=noteId.replace('#',u'\u266F')
    x1=beat2x(beat)+beat2w(1)/2 # beat2x(beat)+beat2w(dur)/2
    y1=yOffset+holeInterval*8.5
    cvs.create_text(x1,y1,text=noteId)

def drawBars():
    global xOffset
    x=beat2x(beatCursor)
    if x>winDims[0]/2:
        xOffset+=winDims[0]/2-x

    win.cvs.delete("all")
    for tab in tabs:
        beat,name,dur,style,tabColor=tab
        beatrel=beat
        drawBar(beatrel,dur,name,style,tabColor)

    # draw cursor
    if (playing or beatCursor>0):
        x=beat2x(beatCursor)
    else: 
        x=0    
    win.cvs.create_line(x,0,x,800,fill='red',width=3) # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html

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
        beat,name,dur,style,tabColor=tab
        if (beat==round(beatCursor,2)):
            if name in ['a','b','c','d','e','f#','g','A','B','C','D','E','F#','G']:
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
    if delayJob is not None:
        win.after_cancel(delayJob)
        delayJob=None
        endNote()
    else:
        delayJob=win.after(0, advanceMetronome)
        doCursorPlay()

def advanceMetronome():
    global beatCursor,delayJob
    if playing:
        lastTab=tabs[-1]
        lastBeat=lastTab[0]+lastTab[2]
        if beatCursor>lastBeat:
            # remove incremented beatCursor for which no note is present
            beatCursor-=beatUpdate 
            beatCursor=round(beatCursor,3)
            win.beatCursor.set(f"beat: {beatCursor:.2f}")
            # stop play
            stopTabScroll()
        else:
            delay=int((60/bpm*1000)*beatUpdate)
            delayJob=win.after(delay, advanceMetronome)
            beatCursor+=beatUpdate
            beatCursor=round(beatCursor,3)
            win.beatCursor.set(f"beat: {beatCursor:.2f}")
            drawBars()
            doCursorPlay()

def delay2beatUpdate(delay):
    return int((60/bpm*1000)*beatUpdate)
def setBeatUpdate():
    global beatUpdate
    beatUpdate=0.1
    delay=delay2beatUpdate(beatUpdate)
    if delay<10: 
        beatUpdate=0.25
        delay=delay2beatUpdate(beatUpdate)
    if delay<10: 
        beatUpdate=0.5
        delay=delay2beatUpdate(beatUpdate)
    if delay<10: 
        beatUpdate=1.0
        delay=delay2beatUpdate(beatUpdate)
def startTabScroll():
    global playing, beatCursor,delayJob, beatUpdate,xOffset,yOffset,dragOffset
    if playing: return
    initBars(beatsize) # don't reset zoom
    beatCursor=0
    setBeatUpdate()
    playing=True
    win.beatCursor.set(f"beat: {beatCursor:.1f}")
    delay=int((60/bpm*1000)*beatUpdate)
    #resetView(None)
    dragOffset=0
    drawBars()
    doCursorPlay()
    delayJob=win.after(delay, advanceMetronome)
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
dragOffset=0
def drag_enter(event):
    global drag_begin
    drag_begin=event.x
def drag_handler(event):
    global drag_begin,dragOffset
    drawDistance=(event.x-drag_begin)
    dragOffset=dragOffset+drawDistance
    #if dragOffset>0: dragOffset=0
    drag_begin=event.x
    drawBars()
def drag_end(event):
    global dragOffset
    drawDistance=(event.x-drag_begin)
    dragOffset=dragOffset+drawDistance
    #if dragOffset>0: dragOffset=0
    drawBars()
def scrollwheel(event):
    global beatsize
    if (event.num==4):
        beatsize=beatsize-1
    if (event.num==5):   
        beatsize=beatsize+1
    #print (f"event:{event}")
    if beatsize<5: beatsize=5
    if beatsize>60: beatsize=60
    initBars(beatsize)
    drawBars()
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
    global dragOffset
    dragOffset=0
    initBars(20)
    drawBars()
def resizeWindow(event):
    global winDims
    winDims=(win.winfo_width(),win.winfo_height())
    drawBars()
def closeWindow():
    win.destroy()
def initWindow():
    global win

    # CREATE WINDOW
    win = tk.Tk()  

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
    win.btnLoad=tk.Button(win.buttonframe,text="Load",relief=tk.FLAT,width=6,command=openFile)
    win.btnLoad.pack(side=tk.LEFT,padx=(2,2))

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
    win.cbLow=tk.Checkbutton(win.buttonframe,text='low',variable=win.varLow,command=setLowHigh)
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
    win.beatCursor.set(f"beat: {beatCursor:3}")
    win.beat = tk.Label(win.buttonframe, relief=tk.FLAT,bg='white',textvariable = win.beatCursor)     
    win.beat.pack(side=tk.LEFT,padx=(3,3))

    # make canvas
    win.cvs = tk.Canvas(win, bg="white" )
    win.cvs.pack(expand=True,fill=tk.BOTH,padx=(0,0),pady=(0,0))
    win.cvs.bind("<ButtonPress-1>", drag_enter)
    win.cvs.bind("<B1-Motion>", drag_handler)
    win.cvs.bind("<ButtonRelease-1>", drag_end)
    # bind keys
    win.bind("<Button-4>", scrollwheel) # for linux scrollup
    win.bind("<Button-5>", scrollwheel) # for linux scrolldown
    win.bind("<MouseWheel>",scrollwheel)# for windows/macos
    win.bind("<Button-3>", resetView)
    win.bind("<Configure>", resizeWindow) #
    win.protocol("WM_DELETE_WINDOW", closeWindow) # custom function which sets winDestroyed so we can check state of win

initWindow()
initPlayer()
loadFile("Fee Ra Huri.tbs")
#loadFile("test.tbs")
t=time.time()
drawBars()

tk.mainloop()

closePlayer()