import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkf
from tkRTFText import RTFText 

scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)
win=None
helppath=None
popupMdown=None

def init(rootWin,helpPath):
    global win,helppath
    win=rootWin
    helppath=helpPath

def relocate():
    global popupMdown
    if not popupMdown.docked: 
        return
    try:
        winDims=[410,win.winfo_height()]
        winPos=[win.winfo_rootx()+win.winfo_width(),win.winfo_rooty()]
        popupMdown.geometry(f'{winDims[0]:.0f}x{winDims[1]:.0f}+{winPos[0]}+{winPos[1]}')  
        popupMdown.after(500,relocate)
    except Exception as e:
        print (f"Error relocating songlistWin! (Perhaps closed?):{e}")

def show(docked=False):
    global popupMdown,dockstate
    dockstate=docked  

    with open(helppath, "r",encoding='utf-8') as reader: # open file
        msg=reader.readlines()    

    popupMdown = tk.Toplevel(win)
    popupMdown.wm_title("Tin Whistle Helper - Manual")
    #backcolor=rootWin["bg"]#"#DDDDDD"
    popupMdown.configure(background='white')

    popupMdown.docked=docked
    if popupMdown.docked:
        popupMdown.attributes('-type', 'splash')
        relocate()
    else:
        popupMdown.transient(win) 

    if not popupMdown.docked:
        # footer
        footerframe=tk.Frame(popupMdown,height=12,bg='white')
        footerframe.pack(side=tk.BOTTOM,fill='x',expand=False,padx=(0,0),pady=(0,0))
        #   resize grip
        resizeGrip=ttk.Sizegrip(footerframe,style='popupMdown.TSizegrip')
        resizeGrip.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        popupMdown.style = ttk.Style()
        popupMdown.style.configure('popupMdown.TSizegrip', background='white')
        #   OK button
        popupMdown.cmdOk = tk.Button(footerframe, text="OK",command=popupMdown.destroy,width=10)
        popupMdown.cmdOk.pack(side=tk.RIGHT,padx=(8,8),pady=(8,8))
        popupMdown.cmdOk.configure(relief=tk.FLAT)

    # script area
    padX=(2,0)
    padY=(2,0)
    reliefT=tk.SOLID
    if popupMdown.docked:
        padX=(0,0)
        padY=(0,0)
        reliefT=tk.FLAT
        vScroll=False
        hScroll=True 
    else:
        vScroll=True
        hScroll=False

    #popupMdown.varScript=tk.StringVar() #use textInput.get()
    textframe=tk.Frame(popupMdown,height=12,bg='white')
    textframe.pack(side=tk.TOP,fill='both',expand=True,padx=(0,0),pady=(0,0))
    popupMdown.helpText=RTFText(textframe,bg='white',relief=reliefT,hscroll=hScroll,vscroll=vScroll)
    popupMdown.helpText.pack(side=tk.LEFT,expand=True,padx=padX,pady=padY,fill=tk.BOTH)
    popupMdown.helpText.configure(wrap=tk.NONE)
    popupMdown.helpText.setRTF(msg,pad=(8,8),bg='white', font=tkf.Font(family='Terminal', weight = 'normal', size = 9))

    if not popupMdown.docked:
        popupMdown.grab_set()
    
    return popupMdown