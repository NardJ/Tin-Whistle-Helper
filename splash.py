import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkf
popupSplash=None
def destroy(ev):
    popupSplash.destroy()

def show(rootWin,title,message,dims="700x200+100+100",timeout=-1):
    global popupSplash
    win=rootWin
    #popupSplash=tk.Tk()
    popupSplash = tk.Toplevel(win)
    popupSplash.transient(win) 
    popupSplash.wm_title(title)
    popupSplash.geometry(dims)
    popupSplash.configure(background='white')
    popupSplash.overrideredirect(True)

    popupSplash.splashTitle=tk.Label(popupSplash,text=title, relief=tk.FLAT,bg='white',font= '*font 15')
    popupSplash.splashTitle.pack(side=tk.TOP,expand=True,padx=(8,8),pady=(16,0),fill=tk.X)
    
    popupSplash.splashText=tk.Label(popupSplash,text=message, relief=tk.FLAT,bg='white',font= 'Consolas 8',justify='left')
    popupSplash.splashText.pack(side=tk.TOP,expand=True,padx=(0,8),pady=(0,8),fill=tk.BOTH)
    
    popupSplash.bind("<ButtonRelease>",destroy)
    
    if timeout>0:
        popupSplash.after(timeout,popupSplash.destroy)
