import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkf

def show(rootWin,title,message,timeout=-1):
    win=rootWin
    popupMdown = tk.Toplevel(win)
    popupMdown.transient(win) 
    popupMdown.wm_title(title)
    #backcolor=rootWin["bg"]#"#DDDDDD"
    #popupMdown.configure(background='white')

    # footer
    footerframe=tk.Frame(popupMdown,height=12)#,bg='white')
    footerframe.pack(side=tk.BOTTOM,fill='x',expand=False,padx=(0,0),pady=(0,0))
    #   OK button
    popupMdown.cmdOk = tk.Button(footerframe, text="OK",command=popupMdown.destroy,width=10)
    popupMdown.cmdOk.pack(padx=(8,8),pady=(8,8))
    #popupMdown.cmdOk.configure(relief=tk.FLAT)

    # script area
    #popupMdown.varScript=tk.StringVar() #use textInput.get()
    popupMdown.helpText=tk.Label(popupMdown,text=message, relief=tk.FLAT)
    popupMdown.helpText.pack(side=tk.LEFT,expand=True,padx=(8,8),pady=(8,8),fill=tk.BOTH)
    
    if timeout>0:
        win.after(timeout,popupMdown.destroy)