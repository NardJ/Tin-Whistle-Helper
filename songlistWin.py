import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkf
from tkRTFText import RTFText 

from tooltip import CreateToolTip

scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)
tabdir    = os.path.join(scriptdir,"tabs")
abcdir    = os.path.join(scriptdir,"abc")
icondir   = os.path.join(scriptdir,"resources/icons")

win=None
songdirs=None
popupMdown=None
remoteload=None

def init(rootWin,songDirs,remoteLoad):
    global win,songdirs,remoteload
    win=rootWin
    songdirs=songDirs
    remoteload=remoteLoad

def relocate():
    global popupMdown
    try:
        winDims=[300,win.winfo_height()]
        winPos=[win.winfo_rootx(),win.winfo_rooty()]
        popupMdown.geometry(f'{winDims[0]:.0f}x{winDims[1]:.0f}+{winPos[0]-winDims[0]}+{winPos[1]}')  
    except Exception as e:
        print (f"Error relocating songlistWin! (Perhaps closed?):{e}")

def clickFile(ev):
    curItem = popupMdown.treeview.focus();
    isDir,filepath=popupMdown.treeview.item(curItem)['values']
    isDir=(isDir=='True') # Treeview stores values as str
    if isDir: return
    print (f"load: {filepath}")
    remoteload( filepath,
                popupMdown.varAutoResize.get(),
                popupMdown.varAutoPlay.get()
                )
    return
    '''
    filename=popupMdown.listbox.get(popupMdown.listbox.curselection())
    filepath=popupMdown.files[filename]
    if filepath=='<header>': return
    filename=filename[2:]
    #print (f"{filepath}/{filename}")
    remoteload( os.path.join(filepath,filename),
                popupMdown.varAutoResize.get(),
                popupMdown.varAutoPlay.get()
                )
    '''
def show():
    global popupMdown

    # create window
    popupMdown = tk.Toplevel(win)
    #popupMdown.transient(win) 
    popupMdown.wm_title("Select tune")
    #backcolor=rootWin["bg"]#"#DDDDDD"
    popupMdown.configure(background='white')
    popupMdown.attributes('-type', 'dock')
 
    footerbgcolor='white'
    footerfgcolor='black'
    # footer
    footerframe=tk.Frame(popupMdown,height=16,bg='white')
    footerframe.pack(side=tk.BOTTOM,fill='x',expand=False,padx=(4,0),pady=(5,6))
    popupMdown.lbDeco=tk.Label(footerframe,text="On load:",takefocus=0,font="*font 9 bold")
    popupMdown.lbDeco.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
    popupMdown.lbDeco.pack(side=tk.LEFT,padx=(0,2))

    # auto resize
    popupMdown.varAutoResize=tk.BooleanVar(value=False)
    popupMdown.cbAutoResize=tk.Checkbutton(footerframe,text='resize',variable=popupMdown.varAutoResize,takefocus=0)
    popupMdown.cbAutoResize.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    popupMdown.cbAutoResize.pack(side=tk.LEFT,padx=(2,0))
    popupMdown.cbAutoResize.tooltip=CreateToolTip(popupMdown.cbAutoResize,"Resize on load.")
    # auto play
    popupMdown.varAutoPlay=tk.BooleanVar(value=False)
    popupMdown.cbAutoPlay=tk.Checkbutton(footerframe,text='play',variable=popupMdown.varAutoPlay,takefocus=0)
    popupMdown.cbAutoPlay.configure(background=footerbgcolor,activebackground=footerbgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    popupMdown.cbAutoPlay.pack(side=tk.LEFT,padx=(2,0))
    popupMdown.cbAutoPlay.tooltip=CreateToolTip(popupMdown.cbAutoPlay,"Play on load.")
    
    # tree file list
    f=tk.Frame(popupMdown,bg='white')
    tv=ttk.Treeview(f,show='tree')
    #ybar=tk.Scrollbar(f,orient=tk.VERTICAL,command=tv.yview)
    #tv.configure(yscroll=ybar.set)
    for directory in songdirs:
        foldername=f"{os.path.basename(os.path.normpath(directory))} files"
        tv.heading('#0',text='Dir：'+directory,anchor='w')
        path=os.path.abspath(directory)
        node=tv.insert('','end',text=foldername,values=(True,path),open=True)
        def traverse_dir(parent,path):
            for d in sorted(os.listdir(path)):
                full_path=os.path.join(path,d)
                isdir = os.path.isdir(full_path)
                id=tv.insert(parent,'end',text=d,values=(isdir,full_path),open=False)
                if isdir:
                    traverse_dir(id,full_path)
        traverse_dir(node,path)
    #ybar.pack(side=tk.RIGHT,fill=tk.Y)
    tv.pack(side=tk.LEFT,expand=True,padx=(2,0),pady=(2,0),fill=tk.BOTH)
    f.pack(side=tk.TOP,fill='both',expand=True,padx=(0,0),pady=(0,0))
    popupMdown.treeview=tv
    popupMdown.treeview.bind('<ButtonRelease-1>', clickFile)
    
    '''
    # flat file list
    listframe = tk.Frame(popupMdown,height=12,bg='white' )
    listframe.pack(side=tk.TOP,fill='both',expand=True,padx=(0,0),pady=(0,0))
    popupMdown.listbox = tk.Listbox(listframe,bg='white',relief=tk.FLAT)#,listvariable=popupMdown.varListbox)
    popupMdown.files={}
    for songdir in songdirs:
        lastFolder=f"🗁 {os.path.basename(os.path.normpath(songdir))}"
        popupMdown.listbox.insert('end', lastFolder)
        popupMdown.files[songdir]='<header>'
        for name in sorted(os.listdir(songdir)):
            name=f"  {name}"
            popupMdown.listbox.insert('end', name)
            popupMdown.files[name]=songdir

    popupMdown.listbox.pack(side=tk.LEFT,expand=True,padx=(2,0),pady=(2,0),fill=tk.BOTH)
    listframe.pack( padx = 4, pady = (2,0) )

    popupMdown.listbox.bind('<<ListboxSelect>>', clickFile)
    
    #popupMdown.listbox.focus_set()
    #popupMdown.listbox.bind("<FocusOut>", refocusListBox)
    #popupMdown.listbox.bind('<Key>',key )
    #refocusListBox()    
    #popupMdown.protocol("WM_DELETE_WINDOW", on_closing)
    #popupMdown.protocol("<Destroy>", on_closing)
    '''

    relocate()
    return popupMdown
   
