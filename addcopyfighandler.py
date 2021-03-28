# -*- coding: utf-8 -*-
"""
Monkey-patch plt.figure() to support Ctrl+C for copying to clipboard as an image

@authors: Josh Burnett, Sylvain Finot
Modified from code found on Stack Exchange:
    https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
    https://stackoverflow.com/questions/34322132/copy-image-to-clipboard-in-python3

Different OSes and GUI libraries require different methods of clipboard interaction.

On Windows:
    - addcopyfighandler should work regardless of which graphical backend is being used by matplotlib
        (tkagg, gtk3agg, qt4agg, qt5agg, etc.)
    - Supported clipboard image file formats are PNG, SVG, JPG, and JPEG.

On Linux:
    - Requires either Qt or GTK libraries for clipboard interaction. Automatically detects which is being used from
        matplotlib.get_backend().
        - Qt support requires one of (PyQt4, PyQt5, PySide2).
        - GTK support requires pycairo, PyGObject and PIL/pillow to be installed.

"""

import platform
import matplotlib.pyplot as plt
from io import BytesIO

__version__ = (3, 0, 0)
oldfig = plt.figure

ostype = platform.system().lower()


if ostype == 'windows':
    from win32gui import GetWindowText, GetForegroundWindow
    import win32clipboard

    def copyfig(fig=None, format=None, *args, **kwargs):
        """
        Parameters
        ----------
        fig : matplotlib figure, optional
            If None, get the figure that has UI focus
        format : type of image to be pasted to the clipboard ('png', 'svg', 'jpg', 'jpeg')
            If None, uses matplotlib.rcParams["savefig.format"]
        *args : arguments that are passed to savefig
        **kwargs : keywords arguments that are passed to savefig

        Raises
        ------
        ValueError
            If the desired format is not supported.

        AttributeError
            If no figure is found
        """

        # Determined available values by digging into windows API
        format_map = {"png": "PNG",
                      "svg": "image/svg+xml",
                      "jpg": "JFIF",
                      "jpeg": "JFIF"}

        # If no format is passed to savefig get the default one
        if format is None:
            format = plt.rcParams["savefig.format"]
        format = format.lower()

        if format not in format_map:
            raise ValueError(f"Format {format} is not supported "
                             f"(supported formats: {', '.join(list(format_map.keys()))})")

        if fig is None:
            # Find the figure window that has UI focus right now (not necessarily
            # the same as plt.gcf() when in interactive mode)
            fig_window_text = GetWindowText(GetForegroundWindow())
            for i in plt.get_fignums():
                if plt.figure(i).canvas.get_window_title() == fig_window_text:
                    fig = plt.figure(i)
                    break

        if fig is None:
            raise AttributeError("No figure found!")

        # Store the image in a buffer using savefig(). This has the
        # advantage of applying all the default savefig parameters
        # such as resolution and background color, which would be ignored
        # if you simply grab the canvas.
        format_id = win32clipboard.RegisterClipboardFormat(format_map[format])
        with BytesIO() as buf:
            fig.savefig(buf, format=format, *args, **kwargs)
            data = buf.getvalue()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(format_id, data)
        win32clipboard.CloseClipboard()

elif ostype == 'linux':
    backend = plt.get_backend()
    if backend in ['Qt5Agg', 'Qt4Agg']:
        if backend == 'Qt4Agg':
            from PyQt4.QtGui import QApplication, QImage
            clipboard = QApplication.clipboard
        if backend == 'Qt5Agg':
            try:
                from PySide2.QtGui import QGuiApplication, QImage
                from PySide2.QtWidgets import QApplication
            except ImportError:
                from PyQt5.QtGui import QGuiApplication, QImage
                from PyQt5.QtWidgets import QApplication
            clipboard = QGuiApplication.clipboard

        def copyfig(fig=None, format=None, *args, **kwargs):
            """
            Parameters
            ----------
            fig : matplotlib figure, optional
                If None, get the figure that has UI focus
            format : type of image to be pasted to the clipboard ('png', 'jpg', 'jpeg', 'tiff')
                If None, uses matplotlib.rcParams["savefig.format"]
                If resulting format is not in ('png', 'jpg', 'jpeg', 'tiff'), will override to PNG.
            *args : arguments that are passed to savefig
            **kwargs : keywords arguments that are passed to savefig

            Raises
            ------
            AttributeError
                If no figure is found
            """

            if format is None:
                format = plt.rcParams["savefig.format"]
            format = format.lower()

            formats = ['png', 'jpg', 'jpeg', 'tiff']
            if format not in formats:
                format = 'png'

            if fig is None:
                # Find the figure window that has UI focus right now (not necessarily
                # the same as plt.gcf() when in interactive mode)
                fig_window_text = QApplication.activeWindow().windowTitle()
                for i in plt.get_fignums():
                    if plt.figure(i).canvas.get_window_title() == fig_window_text:
                        fig = plt.figure(i)
                        break

            if fig is None:
                raise AttributeError("No figure found!")

            # Store the image in a buffer using savefig(). This has the
            # advantage of applying all the default savefig parameters
            # such as resolution and background color, which would be ignored
            # if you simply grab the canvas.
            with BytesIO() as buf:
                fig.savefig(buf, format=format, *args, **kwargs)
                clipboard().setImage(QImage.fromData(buf.getvalue()))

    elif backend == 'GTK3Agg':
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        from gi.repository.Gtk import Clipboard
        from gi.repository import GLib, GdkPixbuf, Gdk
        from PIL import Image
        import subprocess

        clipboard = Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        def copyfig(fig=None, format=None, *args, **kwargs):
            """
            Parameters
            ----------
            fig : matplotlib figure, optional
                If None, get the figure that has UI focus
            format : type of image to be pasted to the clipboard ('png', 'jpg', 'jpeg', 'tiff')
                If None, uses matplotlib.rcParams["savefig.format"]
                If resulting format is not in ('png', 'jpg', 'jpeg', 'tiff'), will override to PNG.
            *args : arguments that are passed to savefig
            **kwargs : keywords arguments that are passed to savefig

            Raises
            ------
            AttributeError
                If no figure is found
            """

            if format is None:
                format = plt.rcParams["savefig.format"]
            format = format.lower()

            format_map = {
                'png': 'PNG',
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'tiff': 'TIFF',
            }

            if format not in format_map:
                format = 'png'

            if fig is None:
                # Find the figure window that has UI focus right now (not necessarily
                # the same as plt.gcf() when in interactive mode)
                pid = (
                    subprocess.run(['xprop', '-root', '_NET_ACTIVE_WINDOW'], capture_output=True)
                        .stdout.decode('UTF-8').strip().rsplit(' ', 1)[-1]
                )
                fig_window_text = (
                    subprocess.run(['xprop', '-id', pid, 'WM_NAME'], capture_output=True)
                        .stdout.decode('UTF-8').strip().split(' = ')[-1].strip('"')
                )

                for i in plt.get_fignums():
                    if plt.figure(i).canvas.get_window_title() == fig_window_text:
                        fig = plt.figure(i)
                        break

            # Store the image in a buffer using savefig(). This has the
            # advantage of applying all the default savefig parameters
            # such as resolution and background color, which would be ignored
            # if you simply grab the canvas.
            with BytesIO() as buf:
                fig.savefig(buf, format=format, *args, **kwargs)
                im = Image.open(buf, formats=[format_map[format]])

                w, h = im.size
                data = GLib.Bytes.new(im.tobytes())
                if im.mode == 'RGBA':
                    pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                             True, 8, w, h, w * 4)
                elif im.mode == 'RGB':
                    pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                             False, 8, w, h, w * 3)
                else:
                    raise ValueError(f'Unsupported image format ({im.mode}). Must be RGB or RGBA.')

                clipboard.set_image(pixbuf)
                clipboard.store()
    else:
        raise ValueError(f'Unsupported matplotlib backend ({backend}). On Linux must be Qt4Agg, Qt5Agg, or GTK3Agg.')

else:
    raise ValueError(f'addcopyfighandler: Supported OSes are Windows and Linux.  Current OS: {ostype}')


def newfig(*args, **kwargs):
    fig = oldfig(*args, **kwargs)

    def clipboard_handler(event):
        if event.key == 'ctrl+c':
            copyfig()

    fig.canvas.mpl_connect('key_press_event', clipboard_handler)
    return fig


plt.figure = newfig
