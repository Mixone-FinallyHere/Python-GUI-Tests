# coding: utf-8
import tkinter as tk
"""
Basic principles of tkinter gui.
"""

__author__ = "Mixone"
__date__ = "16/12/16"


def getRoot(title="Main Window"):
    """
    Setup a root window.
    :param title: window title
    :return: Tk main object
    """
    root = tk.Tk()
    root.title(title)
    return root


def getFrame(root):
    frame = tk.Frame(root)
    frame.pack()
    return frame


def setMainHeader(root, _text="Sample"):
    """
    Adds a main header to given root.
    :param root: Window to add header to
    :param _text: Header text
    :return: No return
    """
    tk.Label(root, text=_text).grid(column=1, row=0, columnspan=2)


def main():
    """
    Our main method.
    :return: No return
    """
    root = getRoot("Learning Tkinter")
    frame = getFrame(root)
    setMainHeader(frame, "Hello world!")
    root.mainloop()

if __name__ == "__main__":
    main()