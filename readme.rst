
fr - Free Resource Printer
==========================

``fr`` is a command-line tool to print free resources in delicious
flavors.
``fr`` is to ``free`` as ``htop`` is to ``top``.

It was written because of unhappiness with the bare-bones, hard-to-read
``free`` command.
I wanted something a bit more... graphical.
Instead of this::

                 total       used       free     shared    buffers     cached
    Mem:       4045216    2159764    1885452          0     192404     942944
    -/+ buffers/cache:    1024416    3020800
    Swap:            0          0          0

You'll see something like this::

    Free Resources in Blocks of 1 Megabyte (1,000,000 bytes)

    DEVICE   VOLUME    CAPACITY       USED       FREE                 MOUNT CACHE
    ⌁ RAM                 4,142      1,421      1,461  ▉▉▉▉▉▉▉░░░░░░▏       1,261
    ▪ SWAP                    0

    ▪ sda1   Ubuntu      18,617      7,000     10,671  ▉▉▉▉░░░░░░░░░▏ /
    ▪ sda5   Data        88,107     85,218      2,889  ▉▉▉▉▉▉▉▉▉▉▉▉░▏ /media/Data
    ◗ sr0    PREDATOR    45,206     45,206          0  ▉▉▉▉▉▉▉▉▉▉▉▉▉▏ /media/PREDATOR


... in fruity colors.
Yes, colors can be turned off, units chosen, etc.
``fr`` has been tested on Ubuntu (1.2X on Precise-Trusty, 1.3X Zesty),
CentOS 6, Windows (XP, 7),
and Mac OS X (10.9.x) so far.
It runs only under Python 2.X at this time.

|

Install
------------

You'll need `pip <http://www.pip-installer.org/en/latest/index.html>`_,
but not virtualenv.

Linux
~~~~~~~~~

As Dbus/Udisks are not installed by default on Precise+ Server
(and possibly others),
they can be if you'd like to print volume labels::

    sudo apt install python3-dbus udisks2
    sudo apt install python3-pip  # Need ``pip``?


For Red Hat: ``s/apt/dnf/``.
Or follow the
`manual instructions <http://stackoverflow.com/a/12234724/450917>`_.

Next, run this::

    sudo pip install fr

If you'd like the development version instead::

    sudo pip install https://bitbucket.org/mixmastamyk/fr/get/default.zip



|

Windows
~~~~~~~~~

After eight years this script finally supports Windows,
though support is experimental.  ;)

Need ``pip``?
Instructions for
`installing on Windows <http://stackoverflow.com/a/14407505/450917>`_.
Put ``"%ProgramFiles%\PythonXX\Scripts"`` in your ``PATH``.

Next, run these as Admin::

    pip install colorama        # want color?
    pip install fr[win]         # installs necessary winstats

I've given up on Unicode icons (for now) on the Windows console and went back
to cp437 for that old-timey DOS feel.
Perhaps it should print out "conventional/high" memory too.

|

Mac OS X
~~~~~~~~~

Yes, it supports that too, though support is experimental::

    sudo pip install -U fr

And off you go.


|

Use
------------


Run it ;)

::

    fr

And of course there are a number of options::

    fr -h

Note:  Output will be in a compact format unless the width of the console
is at least 90 characters.
Give it more and it will expand to fill available space.

|

License
~~~~~~~~~

Licensed under the `GPL, version 3+ <http://www.gnu.org/licenses/gpl.html>`_.

|

Release Notes
~~~~~~~~~~~~~~~

- 1.38 - enh: Linux - warn when dbus module not found.
- 1.37 - enh: Support NO_COLOR environment variable.
- 1.36 - enh: Don't show loop devices (snaps) or /boot/efi by default on linux.
- 1.35 - fix: One more try.  ;)
- 1.34 - fix: wide unicode chars breaking alignment, new narrow chars.
         (Broke recently, related to ambiguous width characters.)
- 1.33 - fix: warning icon under linux console.
- 1.32 - fix: udisk1 compatibility, improve udisks missing warning,
- 1.31 - fix: usb drive detection, icon
- 1.30 - enh: Linux: Supports and prefers Udisks2
- 1.24 - fix: extra linefeed on some systems.
- 1.23 - fix: swap cache colors
- 1.22 - fix: swap colors
- 1.21 - add: -l local flag to skip remote filesystems.
- 1.20 - fix: pipeline UnicodeEncodeError.
- 1.19 - fix: don't print ansi reset at end of bar when color off.
- 1.18 - fix: swap bar should be match bold setting.
- 1.17 - Windows: fix crash on XP, crash on ctypes+colorama
- 1.16 - Posix: don't install fr.cmd.
- 1.15 - Darwin: fix widelayout (term size), mount point.
- 1.14 - Fix: cache colors differed on 256 colors.
- 1.12 - Darwin: fix subprocess call.
- 1.11 - Darwin: support TERM=xterm.
- 1.10 - Now supports Mac OS X (aka "Darwin")
- 1.01 - Handle negative swap size on WinXP, swap numbers unreliable. :/
