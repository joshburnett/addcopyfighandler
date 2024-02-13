addcopyfighandler: Add a Ctrl+C handler to matplotlib figures for copying the figure to the clipboard
======================================================================================================

Importing this module (after importing matplotlib or pyplot) will add a handler
to all subsequently-created matplotlib figures
so that pressing Ctrl+C with a matplotlib figure window selected will copy
the figure to the clipboard as an image.  The copied image is generated through
matplotlib.pyplot.savefig(), and thus is affected by the relevant rcParams
settings (savefig.dpi, savefig.format, etc.).

Windows and Linux are currently supported. Pull requests implementing macOS support are welcome.

Uses code & concepts from:
- https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
- https://stackoverflow.com/questions/34322132/copy-image-to-clipboard-in-python3


## Windows-specific behavior:

- addcopyfighandler should work regardless of which graphical backend is being used by matplotlib
    (tkagg, gtk3agg, qtagg, etc.).
- If `matplotlib.rcParams['savefig.format']` is `'svg'`, the figure will be copied to the clipboard
    as an SVG.
- If Pillow is installed, all non-SVG format specifiers will be overridden, and the
    figure will be copied to the clipboard as a Device-Independant Bitmap.
- If Pillow is not installed, the supported format specifiers are `'png'`, `'jpg'`, `'jpeg'`, and `'svg'`.
    All other format specifiers will be overridden, and the figure will be copied to the clipboard as PNG data.


## Linux-specific behavior:

- Requires either Qt or GTK libraries for clipboard interaction. Automatically detects which is being used from
    `matplotlib.get_backend()`.
    - Qt support requires `PyQt5`, `PyQt6`, `PySide2` or `PySide6`.
    - GTK support requires `pycairo`, `PyGObject` and `PIL` or `pillow` to be installed.
      - Only GTK 3 is supported, as GTK 4 has totally changed the way clipboard data is handled and I can't figure
        it out. I'm totally open to someone else solving this and submitting a PR if they want. I don't use GTK.
- The figure will be copied to the clipboard as a PNG, regardless of `matplotlib.rcParams['savefig.format']`. Alas, SVG output is not currently supported. Pull requests that enable SVG support would be welcomed.


Releases
--------
### 3.1.0: 2024-02-13

- Add support for PyQt6 and PySide6 on Linux (already supported on Windows)

### 3.0.0: 2021-03-28

- Add Linux support (tested on Ubuntu). Requires PyQt5, PySide2, or PyObject libraries; relevant library chosen based on matplotlib graphical backend in use. No SVG support.
- On Windows, non SVG-formats will now use the Pillow library if installed, storing the figure to the clipboard as a device-indepenent bitmap (as previously handled in v2.0). This is compatible with a wider range of Windows applications.

### 2.1.0: 2020-08-27

- Remove Pillow.
- Add support for png & svg file formats.

### 2.0.0: 2019-06-07

- Remove Qt requirement. Now use Pillow to grab the figure image, and win32clipboard to manage the Windows clipboard.


### 1.0.2: 2018-11-27

- Force use of Qt4Agg or Qt5Agg. Some installs will default to TkAgg backend, which this module
doesn't support. Forcing the backend to switch when loading this module saves the user from having
to manually specify one of the Qt backends in every analysis.


### 1.0.1: 2018-11-27

- Improve setup.py: remove need for importing module, add proper installation dependencies
- Change readme from ReST to Markdown


### 1.0: 2017-08-09

- Initial release

