CROPR
========
.. image:: imgs/CROPR_intro.png

Welcome! If you're reading this it means you purchased or are considering purchasing CROPR.
This documentation will guide you on how to handle the application.

CROPR is a small stand-alone application that speeds up the preprocessing of vehicle blueprints
before using them as reference images: each view is cropped from the original blueprint and scaled accordingly
so it fit the other views dimensions.

Features
--------

Under the hood of CROPR is a very basic edge detector function: since 99% of the blueprints are
in black and white, the application uses a threshold value to detect the contour of each view.

Some edge cases exists, which is why CROPR has the following features:
- Ignore ground
- Mask
- Threshold adjustment
- Zoom
- Manual mode (no contour detection)

Installation
------------

No installation needed, simply run the executable file you downloaded

Contribute
----------

- https://gum.co/ZEyTk


Support
-------

If you are having issues, please let us know: support@thibautbourbon.com

License
-------

The project is licensed under the GPL license.

USER GUIDE
==========

User interface
--------------

To start CROPR, simply double click on the executable file you downloaded. The following menu should pop-up:
.. image:: imgs/UI_main_menu.png


Commands
--------

Most of the commands are context based are visible under the mouse pointer:

- <Scroll button> - Scroll up/down
- <Shift> + <Scroll button> - Scroll left/right
- <Num +> / <Num -> - Zoom in/out (NOTE: the image default size is the maximum size)
- <G> - Ground mode
- <M> - Mask mode
- <C> - Contrast mode
- <N> - Manual mode
- <Control Z> - Undo
- <Control V> - Paste image
- <Esc> - skip
- <Space bar> - confirm


