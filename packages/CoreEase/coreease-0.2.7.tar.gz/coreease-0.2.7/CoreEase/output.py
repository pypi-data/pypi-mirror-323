import os
import tkinter.messagebox
from .system import ConsoleWidth
def ClearConsole():
    os.system("cls")
def Print(string):
    print(string)
def Input(string):
    input(string)
def EnumeratedPrint(list):
    for x,y in enumerate(list):
        print(x + y)
def CenteredPrint(string,filler):
    console_w = ConsoleWidth()
    print(string.center(console_w, filler))
def CenteredPrintTempLine(string,filler):
    console_w = ConsoleWidth()
    print(string.center(console_w, filler), end="\r")
def CenteredInput(string):
    console_w = ConsoleWidth()
    console_lp = console_w // 2 - (len(string)+2)
    x = input(" " * console_lp + string + " " * 5)
    return x
def EnumeratedCenteredPrint(list):
    console_w = ConsoleWidth()
    for x,y in enumerate(list):
        print(x + y.center(console_w, " "))
def CreateMessageboxInfo(title, message):
    tkinter.messagebox.showinfo(title, message)
def CreateMessageboxWarning(title, message):
    tkinter.messagebox.showwarning(title, message)
def CreateMessageboxError(title, message):
    tkinter.messagebox.showerror(title, message)