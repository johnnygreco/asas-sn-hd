#!/usr/bin/env python 
import tkinter as tk
import numpy as np
import pandas as pd
import ashd
from tkinter import messagebox
display = ashd.Display()

class App(object):
    def __init__(self, master, cat_fn, size=300):
        frame = tk.Frame(master)
        frame.pack()

        self.master = master
        self.current_idx = 0
        self.cat =  pd.read_csv(cat_fn)
        self.size = size

        self.prev_button = tk.Button(frame, 
                                     text='Previous', 
                                     command=self.prev_idx)
        self.prev_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(frame,
                                     text='Next',
                                     command=self.next_idx)
        self.next_button.pack(side=tk.LEFT)

        self.cols = ['ra', 'dec', 'a', 'b', 'theta']
        ell_par = self._get_ell_par()
        display.ds9_cutout(ell_par[0], ell_par[1], size=size, ell_par=ell_par)

    def _get_ell_par(self):
        ra, dec, a, b, theta = self.cat.ix[self.current_idx, self.cols]
        return [ra, dec, a, b, theta*180/np.pi]

    def prev_idx(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            ell_par = self._get_ell_par()
            display.ds9_cutout(ell_par[0], ell_par[1], size=self.size, 
                               ell_par=ell_par)

    def next_idx(self):
        self.current_idx += 1
        if self.current_idx > (len(self.cat)-1):
            msg = 'Congrats, visual inspection complete!'
            w = tk.Tk()
            w.withdraw()
            messagebox.showinfo('ASAS-SN HD Message', msg, parent=w)
            w.destroy()
            self.quit()
        else:
            ell_par = self._get_ell_par()
            display.ds9_cutout(ell_par[0], ell_par[1], size=self.size, 
                               ell_par=ell_par)

    def quit(self):
        self.master.destroy()

if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('cat_fn', type=str)
    args = parser.parse_args()
    root = tk.Tk()
    app = App(root, args.cat_fn)
    root.mainloop()
