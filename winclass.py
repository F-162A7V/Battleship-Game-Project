__author__ = "F-162A7V"



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


class customRadio():
    def __init__(self,parentwin,w,name,optlist,tgt,offset=0):
        if type(offset) != tuple:
            offset = (0, 0)
        self.w = w
        self.parentwin = parentwin
        #self.label = ttk.Label(self.parentwin.root, text=name)
        #self.label.pack(padx=offset[0], pady=(offset[1] - 10))
        self.offset = offset
        self.optlist = optlist
        self.mvar = tk.StringVar()
        self.mvar.set(optlist[0])
        for x in optlist:
            tk.Radiobutton(self.parentwin.root, text=x, variable=self.mvar, value=x, command=tgt).grid()

