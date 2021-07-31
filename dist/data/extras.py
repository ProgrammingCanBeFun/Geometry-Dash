import pygame
import json
import sys
import tkinter
from tkinter import messagebox


def terminate():
    pygame.quit()
    sys.exit()


def get_data(filename='data/level_data.json'):
    with open(filename, 'r') as f:
        return json.load(f)


def show_alert(message: str, title="Alert"):
    root = tkinter.Tk()
    root.withdraw()

    # Message Box
    messagebox.showinfo(title, message)


def reverse(item: int or float or bool):
    if type(item) == bool:
        item = not item
    elif type(item) == int or float:
        item *= 1
    else:
        raise TypeError
    return item


colors = {
    "Yellow": [255, 255, 0],
    "Red": [255, 0, 0],
    "Orange": [255, 165, 0],
    "Light Orange": [255, 201, 14],
    "Green": [0, 255, 0],
    "Blue": [0, 0, 255],
    "White": [255, 255, 255],
    "Black": [0, 0, 0],
    "Gray": [115, 115, 155],
    "Dark Blue": [0, 0, 115],
    "Pink": [255, 192, 203]
}
