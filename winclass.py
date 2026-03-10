import sys
import tkinter as tk
from tkinter import ttk



class Window():
    def __init__(self,name,geometr):
        self.root = tk.Tk("window")
        self.root.geometry(geometr)
        self.root.title(name)


class customEntry():
    def __init__(self,parentwin,h,w,offset=0,shw="",lbl=''):
        self.h = h
        self.w = w
        self.parentwin = parentwin
        self.offset = offset
        self.shw = shw
        self.lbl = lbl
        self.text_var = tk.StringVar()
        if type(offset) != tuple:
            offset = (0, 10)
        self.label = ttk.Label(self.parentwin.root, text=lbl)
        self.label.pack(padx=offset[0], pady=(offset[1] - 10))
        self.entry = ttk.Entry(self.parentwin.root, show=shw,textvariable=self.text_var)
        self.entry.pack(padx=offset[0], pady=offset[1])

class customButton():
    def __init__(self,parentwin,w,name,command,offset=0):
        if type(offset) != tuple:
            offset = (0, 0)
        self.w = w
        self.offset = offset
        self.b1 = ttk.Button(parentwin.root,text=name,width=w,command=command)
        self.b1.pack(padx=offset[0],pady=offset[1])



#win = Window("Client","200x300")
#namefield = customEntry(win,25,25,lbl="Enter Name:")
#passfield = customEntry(win,25,25,(0,25),"*",lbl="Enter Password:")
#win.root.mainloop()