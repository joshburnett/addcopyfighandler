# -*- coding: utf-8 -*-
"""
Monkey-patch plt.figure() to support Ctrl+C for copying to clipboard as an image

Importing this module (after importing matplotlib or pyplot) will add a handler
to all subsequently-created matplotlib figures
so that pressing Ctrl+C with a matplotlib figure window in the foreground will copy
the figure to the clipboard as an image.  The copied image is generated through
matplotlib.pyplot.savefig(), and thus is affected by the relevant matplotlib.rcParams
settings (savefig.dpi, savefig.format, etc.).

@authors: Josh Burnett, Sylvain Finot
Modified from code found on Stack Exchange:
    https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
    https://stackoverflow.com/questions/34322132/copy-image-to-clipboard-in-python3

Different OSes and GUI libraries require different methods of clipboard interaction.

On Windows:
    - addcopyfighandler should work regardless of which graphical backend is being used by matplotlib
        (tkagg, gtk3agg, qt5agg, etc.)
    - If matplotlib.rcParams['savefig.format'] is 'svg,' the figure will be copied to the clipboard
        as an SVG.
    - If Pillow is installed, all non-SVG format specifiers will be overridden and the
        figure will be copied to the clipboard as a Device-Independant Bitmap.
    - If Pillow is not installed, the supported format specifiers are 'png,' 'jpg,' 'jpeg,' and 'svg.'
        All other format specifiers will be overridden and the figure will be copied to the clipboard as PNG data.

On MacOS:
    - Only works with the QtAgg backend.

On Linux:
    - Requires either Qt or GTK libraries for clipboard interaction. Automatically detects which is being used from
        matplotlib.get_backend().
        - Qt support requires PyQt or PySide2.
        - GTK support requires pycairo, PyGObject and PIL/pillow to be installed.
    - The figure will be copied to the clipboard as a PNG, regardless of matplotlib.rcParams['savefig.format'].
"""

import platform
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO

__version__ = '3.0.0'
__version_info__ = tuple(int(i) if i.isdigit() else i for i in __version__.split('.'))

oldfig = plt.figure

ostype = platform.system().lower()

backend = plt.get_backend()


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
        format_map = {'png': 'PNG',
                      'svg': 'image/svg+xml',
                      'jpg': 'JFIF',
                      'jpeg': 'JFIF',
                      }

        # If no format is passed to savefig get the default one
        if format is None:
            format = plt.rcParams['savefig.format']
        format = format.lower()

        if format not in format_map:
            format = 'png'

        if fig is None:
            # Find the figure window that has UI focus right now (not necessarily
            # the same as plt.gcf() when in interactive mode)
            fig_window_text = GetWindowText(GetForegroundWindow())
            for i in plt.get_fignums():
                if plt.figure(i).canvas.manager.get_window_title() == fig_window_text:
                    fig = plt.figure(i)
                    break

        if fig is None:
            raise AttributeError('No figure found!')

        # Store the image in a buffer using savefig(). This has the
        # advantage of applying all the default savefig parameters
        # such as resolution and background color, which would be ignored
        # if we simply grab the canvas as displayed.
        with BytesIO() as buf:
            fig.savefig(buf, format=format, *args, **kwargs)

            if format != 'svg':
                try:
                    from PIL import Image
                    im = Image.open(buf)
                    with BytesIO() as output:
                        im.convert("RGB").save(output, "BMP")
                        data = output.getvalue()[14:]  # The file header off-set of BMP is 14 bytes
                        format_id = win32clipboard.CF_DIB  # DIB = device independent bitmap

                except ImportError:
                    data = buf.getvalue()
                    format_id = win32clipboard.RegisterClipboardFormat(format_map[format])
            else:
                data = buf.getvalue()
                format_id = win32clipboard.RegisterClipboardFormat(format_map[format])

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(format_id, data)
        win32clipboard.CloseClipboard()

elif backend == 'Qt5Agg' or backend == 'QtAgg':
    # Use Qt version from matplotlib.
    import importlib
    qtver = matplotlib.backends.qt_compat.QT_API
    QtGui = importlib.import_module(qtver + ".QtGui")
    QtWidgets = importlib.import_module(qtver + ".QtWidgets")
    QImage = QtGui.QImage
    QApplication = QtWidgets.QApplication
    clipboard = QtGui.QGuiApplication.clipboard

    def copyfig(fig=None, *args, **kwargs):
        """
        Parameters
        ----------
        fig : matplotlib figure, optional
            If None, get the figure that has UI focus
        *args : arguments that are passed to savefig
        **kwargs : keywords arguments that are passed to savefig

        Raises
        ------
        AttributeError
            If no figure is found
        """

        if fig is None:
            # Find the figure window that has UI focus right now (not necessarily
            # the same as plt.gcf() when in interactive mode)
            fig_window_text = QApplication.activeWindow().windowTitle()
            for i in plt.get_fignums():
                if plt.figure(i).canvas.manager.get_window_title() == fig_window_text:
                    fig = plt.figure(i)
                    break

        if fig is None:
            raise AttributeError('No figure found!')

        # Store the image in a buffer using savefig(). This has the
        # advantage of applying all the default savefig parameters
        # such as resolution and background color, which would be ignored
        # if we simply grab the canvas as displayed.
        with BytesIO() as buf:
            fig.savefig(buf, format='png', *args, **kwargs)
            clipboard().setImage(QImage.fromData(buf.getvalue()))

elif ostype == 'linux':
    if backend == 'GTK3Agg':
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        from gi.repository.Gtk import Clipboard
        from gi.repository import GLib, GdkPixbuf, Gdk
        from PIL import Image
        import subprocess

        clipboard = Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        def copyfig(fig=None, *args, **kwargs):
            """
            Parameters
            ----------
            fig : matplotlib figure, optional
                If None, get the figure that has UI focus
            *args : arguments that are passed to savefig
            **kwargs : keywords arguments that are passed to savefig

            Raises
            ------
            AttributeError
                If no figure is found
            """

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
                    if plt.figure(i).canvas.manager.get_window_title() == fig_window_text:
                        fig = plt.figure(i)
                        break

            # Store the image in a buffer using savefig(). This has the
            # advantage of applying all the default savefig parameters
            # such as resolution and background color, which would be ignored
            # if we simply grab the canvas as displayed.
            with BytesIO() as buf:
                fig.savefig(buf, format=format, *args, **kwargs)
                im = Image.open(buf, formats=['PNG'])

                w, h = im.size
                data = GLib.Bytes.new(im.tobytes())
                pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                                         True, 8, w, h, w * 4)

                clipboard.set_image(pixbuf)
                clipboard.store()
    else:
        raise ValueError(f'Unsupported matplotlib backend ({backend}). On Linux must be QtAgg, or GTK3Agg.')

else:
    raise ValueError(f'addcopyfighandler: Supported OSes are Windows and Linux, MacOS only with QtAgg backend.  Current OS: {ostype}')


def newfig(*args, **kwargs):
    fig = oldfig(*args, **kwargs)

    def clipboard_handler(event):
        if event.key == 'ctrl+c' or event.key == 'cmd+c':
            copyfig()

    fig.canvas.mpl_connect('key_press_event', clipboard_handler)
    return fig


plt.figure = newfig
