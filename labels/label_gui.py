import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
import os, sys

CH = sys.argv[1]                          # HHE, HHN or HHZ
FILELIST = f'labels/{CH}_files.txt'
OUTFILE  = f'labels/{CH}_labels.csv'

img_paths = [l.strip().split()[-1] for l in open(FILELIST)]
idx = 0
labels = {}

root = tk.Tk()
root.title(f"Label {CH} — 0=OK, 1=BAD")

def load():
    global img, tk_img
    img = Image.open(img_paths[idx])
    img.thumbnail((900, 700))
    tk_img = ImageTk.PhotoImage(img)
    panel.config(image=tk_img)
    info.config(text=f"{idx+1}/{len(img_paths)}  {os.path.basename(img_paths[idx])}")

def save(label):
    labels[img_paths[idx]] = label
    next_img()

def next_img():
    global idx
    idx += 1
    if idx >= len(img_paths):
        pd.Series(labels, name='label').to_csv(OUTFILE)
        messagebox.showinfo("Done", f"Saved {len(labels)} labels to {OUTFILE}")
        root.quit()
    else:
        load()

panel = tk.Label(root)
panel.pack()

info = tk.Label(root, font=('Arial', 14))
info.pack()

btn_ok = tk.Button(root, text='0 OK',  command=lambda: save(0), width=10, height=2, bg='green')
btn_bad= tk.Button(root, text='1 BAD', command=lambda: save(1), width=10, height=2, bg='red')
btn_ok.pack(side='left', fill='x', expand=True)
btn_bad.pack(side='right', fill='x', expand=True)

load()
root.mainloop()