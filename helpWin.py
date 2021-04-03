import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkf
from tkRTFText import RTFText 

scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)
win=None

def init(rootWin):
    global win
    win=rootWin

def show():
    with open(os.path.join(scriptdir,"helpWin.txt"), "r") as reader: # open file
        msg=reader.readlines()    

    popupMdown = tk.Toplevel(win)
    popupMdown.transient(win) 
    popupMdown.wm_title("Tin Whistle Helper - Manual")
    #backcolor=rootWin["bg"]#"#DDDDDD"
    popupMdown.configure(background='white')

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
    #popupMdown.varScript=tk.StringVar() #use textInput.get()
    textframe=tk.Frame(popupMdown,height=12,bg='white')
    textframe.pack(side=tk.TOP,fill='both',expand=True,padx=(0,0),pady=(0,0))
    popupMdown.helpText=RTFText(textframe,bg='white',relief=tk.SOLID)
    popupMdown.helpText.pack(side=tk.LEFT,expand=True,padx=(2,0),pady=(2,0),fill=tk.BOTH)
    popupMdown.helpText.configure(wrap=tk.NONE)

    popupMdown.helpText.setRTF(msg,pad=(8,8),bg='white', font=tkf.Font(family='Terminal', weight = 'normal', size = 9))

    popupMdown.grab_set()