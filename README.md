addcopyfighandler: Adds a Ctrl+C handler to matplotlib figures for copying the figure to the clipboard
======================================================================================================
        
Simply importing this module (after importing matplotlib) will add a handler
so that pressing Ctrl+C with a matplotlib figure window selected will copy
the figure to the clipboard as an image.

Original concept code taken from:
https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures


Releases
--------

### 1.0: 2017-08-09

- Initial release


### 1.0.1: 2018-11-27

- Improve setup.py: remove need for importing module, add proper installation dependencies
- Change readme from ReST to Markdown