addcopyfighandler: Add a Ctrl+C handler to matplotlib figures for copying the figure to the clipboard
======================================================================================================

Simply importing this module (after importing matplotlib or pyplot) will add a handler
so that pressing Ctrl+C with a matplotlib figure window selected will copy
the figure to the clipboard as an image.

Original concept code taken from:
https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures

Advanced Control
--------
to control dpi, image-format, or other savefig key words, set their value after importing like so:
import addcopyfighandler
addcopyfighandler.image_file_format = "png"
addcopyfighandler.image_dpi = 250
addcopyfighandler.other_savefig_kwargs = {"pad_inches":0.5,"transparent":True}


Releases
--------
### 2.1.1: 2020-08-27

- add user input method for image-format and dpi control

### 2.1.0: 2020-08-27

- Remove Pillow
- Add support for png, svg, jpg, jpeg fileformat.

### 2.0.0: 2019-04-15

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

