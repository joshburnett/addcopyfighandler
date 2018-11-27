# -*- coding: utf-8 -*-
"""
Monkey-patch plt.figure() to support Ctrl+C for copying to clipboard as an image

@author: Josh Burnett
Modified from code found on Stack Exchange:
    https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
"""


import matplotlib.pyplot as plt
from win32gui import GetWindowText, GetForegroundWindow

import io
import qtpy

__version__ = (1, 0, 1)

if qtpy.API == 'pyqt4':
    from PyQt4.QtGui import QApplication, QImage
    clipboard = QApplication.clipboard
elif qtpy.API == 'pyqt5':
    from PyQt5.QtGui import QGuiApplication, QImage
    clipboard = QGuiApplication.clipboard
    
oldfig = plt.figure


def copyfig(fig=None):
    # store the image in a buffer using savefig(), this has the
    # advantage of applying all the default savefig parameters
    # such as background color; those would be ignored if you simply
    # grab the canvas using Qt
    if fig is None:
        # find the figure window that has UI focus right now (not necessarily the same as plt.gcf())
        fig_window_text = GetWindowText(GetForegroundWindow())
        for i in plt.get_fignums():
            if plt.figure(i).canvas.get_window_title() == fig_window_text:
                fig = plt.figure(i)
                break
        
    buf = io.BytesIO()
    fig.savefig(buf)
    clipboard().setImage(QImage.fromData(buf.getvalue()))
    buf.close()


def newfig(*args, **kwargs):
    fig = oldfig(*args, **kwargs)

    def clipboard_handler(event):
        if event.key == 'ctrl+c':
            copyfig()

    fig.canvas.mpl_connect('key_press_event', clipboard_handler)
    return fig


plt.figure = newfig
