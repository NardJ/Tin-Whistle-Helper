from tkinter import *

def setScroll():
    print(vbar.get())
   # vbar.set(0.5,0.5)
    canvas.yview_moveto(0.11)


root=Tk()
frame=Frame(root,width=800,height=600)
frame.pack(expand=True, fill=BOTH) #.grid(row=0,column=0)
canvas=Canvas(frame,bg='#FFFFFF',width=800,height=600,scrollregion=(0,0,800,600*4))
hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(width=800,height=600)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
canvas.config(scrollregion=(0,0,800,600*5))
canvas.create_oval((100,100,130,130),fill='red')
root.after(1000,setScroll)
root.mainloop()
