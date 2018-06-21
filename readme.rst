
fr - Free Resource Printer
==========================

``fr`` is a command-line tool to print free resources in delicious
flavors.
In short,
``fr`` is to ``free`` as ``htop`` is to ``top``.

``fr`` was written due to unhappiness with the bare-bones, hard-to-read
``free`` command.
I wanted something a bit more… graphical.
Instead of this::

                 total       used       free     shared    buffers     cached
    Mem:       4045216    2159764    1885452          0     192404     942944
    -/+ buffers/cache:    1024416    3020800
    Swap:            0          0          0

You'll see something more like this::

    Free Resources in Blocks of 1 Megabyte (1,000,000 bytes)

    DEVICE   VOLUME    CAPACITY       USED       FREE                 MOUNT CACHE
    ⌁ RAM                 4,142      1,421      1,461  ▉▉▉▉▉▉▉░░░░░░▏       1,261
    ▪ SWAP                    0

    ▪ sda1   Ubuntu      18,617      7,000     10,671  ▉▉▉▉░░░░░░░░░▏ /
    ▪ sda5   Data        88,107     85,218      2,889  ▉▉▉▉▉▉▉▉▉▉▉▉░▏ /media/Data
    ◗ sr0    PREDATOR    45,206     45,206          0  ▉▉▉▉▉▉▉▉▉▉▉▉▉▏ /media/PREDATOR


... in fruity colors if you so choose.
Yes,
color can be turned off
(``NO_COLOR`` environment variable is supported),
units chosen,
network mounts filtered,
etc, etc.

``fr`` 3.x has been tested on
Ubuntu 18.04 Bionic "Tch-tch-tch-tch…",
Windows 7,
and
MacOS 10.13 "High Sierra,"
so far.


.. note::

    Version 3.x of ``fr`` has been ported and works only under Python 3.6 and
    over.
    To use with an earlier version of Python,
    try ``fr`` 1.x,
    which supports Python 2.7 and earlier platforms.


.. ~ .. raw:: html

   .. ~ <hr width=50 size=10>
   .. ~ <b>Works?</b>



Install
------------


Linux
~~~~~~~~~

As of ``fr`` version 3.x,
Dbus and Udisks are no longer required or used on Linux.
Rather,
data is read from the
``/proc``, ``/dev``, and potentially ``/sys``
filesystems.

To install system-wide as root::

    sudo -H pip3 install fr

Per user (add ``/home/$USER/.local/bin`` to ``PATH``)::

    pip3 install --user fr


|

Windows
~~~~~~~~~

Support is still experimental.
Could use some help as Win7 in a VM is all I have access to these days.

Run as Admin::

    pip3 install fr[win]    # installs winstats, colorama

or a user install, but need to add the install folder to ``PATH``::

    pip3 install --user fr[win]


|

Mac OS X
~~~~~~~~~

Yes, it supports that too.
Support is experimental as well::

    [sudo] pip3 install [--user] fr

And off you go.

FYI, the Unicode block characters look a bit better with Source Code Pro as the
terminal font.

Could use some help here also,
borrowing a Mac is my only option.
Currently runs
``sysctl``, ``vm_stat``, and ``df`` under the hood,
hoping there are better options?


Limitations
~~~~~~~~~~~~~

Optical, Network, Removable
+++++++++++++++++++++++++++++

Both Windows and Mac OS are not currently able to detect whether extended
properties of filesystems.
The port to Python 3 seems to have broken Windows in that regard,
which used to work.

Unicode
+++++++++

I've given up on Unicode icons (for now) on the Windows console and went back
to ASCII.
Perhaps it should print out "conventional/high" memory too.

The Linux console (the real boot up console, pre-X) has a very limited
character set and therefore uses ASCII as well.

Colors
+++++++++

Windows and the Linux (non-X11) console are limited to sixteen colors.
Apparently Windows 10 has been upgraded support more,
but I haven't yet found documentation on how to utilize it.


Use
------------

Run it ;)

::

    fr

And of course there are a number of options,
spit out when this is typed::

    fr -h


.. note::

    Output will be in a compact format when the width of the
    terminal/console is under 90 characters.
    Give it more and it will expand to fill available space.


|

License
~~~~~~~~~

`GPL, version 3+ <http://www.gnu.org/licenses/gpl.html>`_.

|

Release Notes
~~~~~~~~~~~~~~~

- 3.0b5 - MacOS, filter /private/… by default.
- 3.0b4 - Readme fixes for PyPI.
- 3.0a0 - Major rewrite to support Python 3.6,
  refactor shitty thirteen year-old code,
  remove deps on Dbus and Udisks.
  Still needs a lot of work.
