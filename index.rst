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

GETTING STARTED
===============

In this section we will cover the user interface and the standard procedure. Edge cases are treated in the next section.

User interface
--------------

To start CROPR, simply double click on the executable file you downloaded. The following menu should pop-up:

.. image:: imgs/UI_main_menu.png

Loading a file
--------------

To load an image, you can either hit the "Import Image" button on the top bar and navigate to your file.
Another solution paste an image from the
clipboard by hitting the <Control + V> command.

Output directory
----------------

You can chose where the output files will be saved by pressing the "Output directory" button on
the top bar and browsing to the destination folder of your choice. By default the destination
folder is the one the input image has been loaded from, so if you chose the Paste method you might want to
make sure you save the output to a directory you know.

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

Isolating views
---------------

A typical blueprints shall look like the following:

..Image to INsert ..
(Obviously the views can placed differently)

Once the blueprint is imported and the output folder is chosen, you can see below the pointer which view to isolate first. The order
is always the following:

- Side > Front > Top > Rear

To isolate the view, simply define by two cliks a large bounding box around the view. After the second click, CROPR will automatically
resize the bounding box to fit the countour, and you can move on to the next view:

.image_bounding_box

Notice how the text under the pointer is updated.

Repeat this operation for each view:

..image_repeat_fast_forward_example..

After the last view, you have one last click to confirm:

..image_last_click..

Then, a pop-up message will confirm everything went well and where you can find the output files.


Skipping view
-------------

Some blueprint do not include all views, or sometime you may only be interested by only a fraction of the available views.
CROPR enables you to skip isolating a view by hitting the <Escape> button.

..image_escape_exemple_


Undo
----

Sometime, you want to undo the action you just did. Simply hit <Control + Z> to jump back to the previous view.

EDGE CASES
==========

In some cases, the blueprint you imported is not as clean as we wish it should be: annotations such as ground level or dimensions are present, 
or some views overlap each other. There are different way to deal with these deviations:

Ground mode
-----------

A feature often present in cars blueprint is the ground location. While this can be useful to align the different views, it actually
becomes a hinder for CROPR when finding the contours of the view.

..image_wrong_result..

To work around this issue, activate the ground mode by hitting the <G> key. Notice the background color changes as well.

..image_to_ground_mode..