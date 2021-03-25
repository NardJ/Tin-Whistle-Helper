import tkinter as tk
from tkinter import font as tkf
import re 

class RTFText(tk.Text):
    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)

        self.vbar = tk.Scrollbar(self.frame)
        kw.update({'yscrollcommand': self.vbar.set})
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar['command'] = self.yview

        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def setRTF(self,rtf,pad,bg,font):
        message=''.join(rtf)
        parts = re.split("(\<.*?\>)",message)
        taglist=[]
        fontNames=["Courier"]
        fontWeight="normal"
        fontSlant="roman"
        fontUnderline=False
        fontSizes=[10,]
        fontColors=['black',]
        backColors=['white',]
        align='left'

        self.configure(padx=pad[0])
        self.configure(pady=pad[1])
        self.configure(bg=bg)
        self.configure(font= font) 

        for idx,part in enumerate(parts):
            if len(part)>0:
                #taglist.append('html')
                if part[0]=="<":
                    part=part.lower()
                    #print (part)
                    if part[:8]=='<family:':fontNames.append(part[8:-1])
                    if part=='</family>':fontNames.pop()
                    if part[:6]=='<size:':fontSizes.append(int(part[6:-1]))
                    if part=='</size>':fontSizes.pop()
                    if part[:7]=='<color:':fontColors.append(part[7:-1])
                    if part=='</color>':fontColors.pop()
                    if part[:12]=='<background:':backColors.append(part[12:-1])
                    if part=='</background>':backColors.pop()

                    if part=='<b>'  :fontWeight="bold" 
                    if part=='</b>' :fontWeight="normal"
                    if part=='<i>'  :fontSlant="italic" 
                    if part=='</i>' :fontSlant="roman"   
                    if part=='<u>'  :fontUnderline=True  
                    if part=='</u>' :fontUnderline=False 
                    if part=='<h1>' :fontSizes.append(18)
                    if part=='</h1>':fontSizes.pop()
                    if part=='<h2>' :fontSizes.append(15)
                    if part=='</h2>':fontSizes.pop()
                    if part=='<h3>' :fontSizes.append(12)
                    if part=='</h3>':fontSizes.pop()
                    if part=='<h4>' :fontSizes.append(10)
                    if part=='</h4>':fontSizes.pop()
                    if part=='<center>' :align='center'
                    if part=='</center>':align='left'
                    
                    if part=='<code>':
                        fontNames.append('Terminal')
                        fontSizes.append(10)
                    if part=='</code>':
                        fontNames.pop()
                        fontSizes.pop()

                    if part=='<codei>':
                        backColors.append('lightgrey')
                        fontNames.append('Terminal')
                        fontSizes.append(10)
                    if part=='</codei>':
                        backColors.pop()
                        fontNames.pop()
                        fontSizes.pop()

                    if part=='<hr>' :
                        fontSizes.append(1)
                        backColors.append('black')
                    if part=='</hr>':
                        fontSizes.pop()
                        backColors.pop()
                else:
                    tagname=f"{idx}"
                    taglist=(tagname,)                    
                    self.insert(tk.END, part,taglist) 
                    fontName=fontNames[len(fontNames)-1]
                    fontSize=fontSizes[len(fontSizes)-1]
                    fontColor=fontColors[len(fontColors)-1]
                    backColor=backColors[len(backColors)-1]
                    hFont = tkf.Font(family=fontName ,size=fontSize,weight=fontWeight,slant=fontSlant,underline=fontUnderline)
                    self.tag_configure(idx,font=hFont)
                    self.tag_configure(idx,foreground=fontColor)
                    self.tag_configure(idx,background=backColor)
                    self.tag_configure(idx,justify=align)
        self.configure(state="disabled")

    def __str__(self):
        return str(self.frame)

if __name__=="__main__":
    # Create window
    root=tk.Tk()   
    root.configure(background='white')

    # Add widget RTFText
    RTF=RTFText(root,bg='white')#root,bg="white")
    RTF.pack(side=tk.TOP, fill=tk.BOTH,padx=(0,0),pady=(2,2))

    # Make some rtf/'html' to display
    rtf=("<family:verdana>Verdana <size:14>14pt</size> <size:18>18pt</size></family>\n"+
        "<color:red>red text</color>\n<background:yellow>yellow background</background>\n"+
        "<H1>Header</H1>\n<H2>Header</H2>\n<H3>Header</H3>\n<H4>Header </H4>\n"+
        "<b>Bold</b>\n<i>Italic</i>\n<u>Underscore</u>\n"+
        "<b>Bold <i>and italic</i> </b>\n"+
        "<center>Text can also be centered </center>\n"+
        "Page divider below:\n"+        
        "<hr>\n"+
        "</hr>\n"+
        "Page divider above\n"+
        "Unicode \u23E9 \n"+
        "")    

    # Set rtf to widget
    RTF.setRTF(rtf,pad=(8,8),bg='white', font=tkf.Font(family='Terminal', weight = 'normal', size = 9))
    
    # Display window and wait user actions
    root.mainloop()

 