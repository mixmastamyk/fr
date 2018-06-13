'''
    darwin.py - (C) 2013, Jonathan Eunice
    derived from linux.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    TODO:
        - dark grey color is very black and hard to see.
        - get volume names
'''
import os, locale, re
from os.path import basename, join
from fr.utils import DiskInfo, MemInfo, run

diskdir     = '/Volumes'
devfilter   = (b'devfs', b'map')
diskcmd     = '/bin/df -k'
coloravail  = True
hicolor     = None
boldbar     = None
encoding    = 'utf8'
col_lblw    = 'MOUNT CACHE'
col_lbls    = 'MNT CACHE'
TERM        = os.environ.get('TERM')

if TERM == 'xterm-256color':
    hicolor     = True
    boldbar     = False
elif TERM == 'xterm':
    hicolor     = False
    boldbar     = True
else:
    coloravail = False

locale.setlocale(locale.LC_ALL, '')


def get_label_map(opts):
    label_map = {}

    try:  # get labels from filesystem
        for entry in os.scandir(diskdir):
            if entry.name.startswith('.'):
                continue
            # ~ target = normpath(join(diskdir, os.readlink(entry.path)))
            target = os.readlink(entry.path)
            # ~ decoded_name = entry.name #.encode('utf8').decode('unicode_escape')
            # ~ label_map[target] = decoded_name
            label_map[target] = entry.name
        if opts.debug:
            print('\n\nlabel_map:', label_map)
    except FileNotFoundError:
        pass

    return label_map


def get_diskinfo(opts, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info,
        stats divided by the ouptut unit.
    '''
    outunit = opts.outunit
    disks = []
    try:
        lines = run(diskcmd).splitlines()[1:]  # dump header
        for line in lines:
            tokens  = line.split()
            first_token = tokens[0]
            dev = basename(first_token)
            disk = DiskInfo()
            if first_token in devfilter:
                if show_all:
                    if first_token == b'map':  # fix alignment :-/
                        tokens[0] = first_token + b' ' + tokens[1]
                        dev = tokens[0]
                        del tokens[1]
                    disk.isram = True
                else:
                    continue

            disk.dev = dev.decode('utf8')
            # convert to bytes, then output units
            disk.ocap   = float(tokens[1]) * 1024
            disk.cap    = disk.ocap / outunit
            disk.free   = float(tokens[3]) * 1024 / outunit
            disk.pcnt   = int(tokens[4][:-1])
            disk.used   = float(tokens[2]) * 1024 / outunit

            disk.mntp   = tokens[8].decode('utf8')
            # TODO: better way to find label?
            disk.label  = '?'
            disk.label  = get_label_map(opts).get(disk.mntp, '')

            disk.ismntd = True
            disk.isnet  = ':' in tokens[0].decode('utf8')  # cheesy, works?
            if local_only and disk.isnet:
                continue
            disk.rw     = True
            # ~ if disk.free < 1:
                # ~ disk.rw = False

            # ~ disk.isopt  = None  # TODO: not sure how to get these
            # ~ disk.isrem  = None
            disks.append(disk)
    except IOError:
        return None

    if opts.debug:
        print()
        for disk in disks:
            print(disk.dev, disk)
            print()
    return disks


def get_meminfo(opts):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.  If mem info can't be read, returns None.
        For Darwin / Mac OS X, interrogates the output of the sysctl and
        vm_stat utilities rather than /proc/meminfo
    '''
    outunit = opts.outunit
    meminfo = MemInfo()
    ms = run('/usr/sbin/sysctl -a hw.memsize'.split(), shell=False)   # TODO
    su = run('/usr/sbin/sysctl -a vm.swapusage'.split(), shell=False) # combine
    vm = run('/usr/bin/vm_stat', shell=False)

    if opts.debug:
        print()
        print('ms:', ms)
        print('su:', su)
        print('vm:', vm.decode('ascii'))

    # Process memsize info
    memsize = int(ms.split()[1])

    # Process vm_stat
    vmLines = vm.split(b'\n')
    vmStats = MemInfo()
    try:
        PAGESIZE = int(vmLines[0].split()[-2])
    except IndexError:
        PAGESIZE = 4096

    for line in vmLines[1:]:
        if not line[0] == 80:  # b'P' Page..
            break
        tokens = line.split()
        name, value = tokens[1][:-1].decode('ascii'), tokens[-1][:-1]
        vmStats[name] = int(value) * PAGESIZE

    if opts.debug:
        print(vmStats)
        print()

    meminfo.memtotal = memsize / outunit
    meminfo.memfree  = vmStats.free / outunit
    meminfo.used     = (vmStats.wire + vmStats.active) / outunit
    meminfo.cached   = (vmStats.inactive + vmStats.speculative) / outunit
    meminfo.buffers  = 0

    # parse swap usage
    su_values = su.split()[3::3]            # every third token
    su_unit = chr(su_values[0][0]).lower()  # get unit, 'M'
    PAGESIZE = 1024
    if su_unit == b'm':
        PAGESIZE = 1024 * 1024

    su_values = [ float(val[:-1]) * PAGESIZE for val in su_values ]
    swaptotal, swapused, swapfree = su_values

    # swap set
    meminfo.swaptotal = swaptotal # or 1_000_000  # add these to test swap
    meminfo.swapused  = swapused  # or   600_000
    meminfo.swapfree  = swapfree  # or   400_000
    meminfo.swapcached = 1

    # ~ meminfo.swapused = (meminfo.swaptotal - meminfo.swapcached -
                        # ~ meminfo.swapfree)
    if opts.debug:
        print(meminfo)
    return meminfo

