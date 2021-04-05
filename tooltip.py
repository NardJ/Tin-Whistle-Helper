''' tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
'''

import tkinter as tk
class CreateToolTip(object):
    delay=1500
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter2(self):
        #print (f"enter2 {self.widget}")
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() - self.widget.winfo_height()-2
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='yellow', relief='solid', borderwidth=1,
                       font=("", "8", "normal"))
        label.pack(ipadx=1)
        label.configure(bg="#FFFFAA")
        #label.configure(wraplength=20)

    def enter(self,event=None):
        #print (f"enter {self.widget}")
        self.job=self.widget.after(self.delay,self.enter2)

    def close(self, event=None):
        #print (f"close {self.widget}")
        self.widget.after_cancel(self.job)
        if hasattr(self, 'tw'):
            if self.tw:
                self.tw.destroy()