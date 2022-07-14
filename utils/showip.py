#!/usr/bin/python3
  
import socket
from tkinter import *

LOCALHOST = '127.0.0.1'
def getip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 80))
        IP = str(s.getsockname()[0])
    except Exception:
        IP = LOCALHOST
    finally:
        s.close()
    return IP

def isLinkUp():
    if getip() == LOCALHOST:
        return False
    else:
        return True

def update():
    localIP.config(text=getip())
    rootWindow.title(getip())
    rootWindow.after(30000, update)

def main():
    rootWindow = Tk()
    rootWindow.title(getip())
    localIP = Label(rootWindow, font = ('fixed', 20),)
    localIP.grid(sticky = N, row = 2, column = 1, padx = 5, pady = (20,20))
    localIP.config(text=getip())
    rootWindow.after(30000, update)
    rootWindow.mainloop()

if __name__ == '__main__':
    main()
