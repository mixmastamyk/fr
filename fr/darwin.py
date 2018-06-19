'''
    darwin.py - (C) 2012-18, Mike Miller
                    2013, Jonathan Eunice
    License: GPLv3+.

    Data gathering routines located here.

    TODO:
        - dark grey color is black and very hard to see.
'''
import os, locale
from os.path import basename
from fr.utils import DiskInfo, MemInfo, Info, run

devfilter   = (b'devfs', b'map')
diskcmd     = '/bin/df -k'.split()
diskdir     = '/Volumes'
syscmd      = '/usr/sbin/sysctl hw.memsize vm.swapusage'.split()
vmscmd      = '/usr/bin/vm_stat'
encoding    = 'utf8'
col_lbls    = 'MNT CACHE'
col_lblw    = 'MOUNT CACHE'
coloravail  = True
hicolor     = None
boldbar     = None
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
    ''' TODO: need better way to find label? '''
    label_map = {}

    try:  # get labels from filesystem
        for entry in os.scandir(diskdir):
            if entry.name.startswith('.'):
                continue
            target = os.readlink(entry.path)
            label_map[target] = entry.name
        if opts.debug:
            print('\nlabel_map:', label_map)
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
        label_map = get_label_map(opts)
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

            # convert to bytes, then output units
            disk.dev    = dev.decode('utf8')
            disk.ocap   = float(tokens[1]) * 1024
            disk.cap    = disk.ocap / outunit
            disk.free   = float(tokens[3]) * 1024 / outunit
            disk.pcnt   = int(tokens[4][:-1])
            disk.used   = float(tokens[2]) * 1024 / outunit

            disk.mntp   = tokens[8].decode('utf8')
            disk.label  = label_map.get(disk.mntp, '')
            disk.ismntd = bool(disk.mntp)
            disk.isnet  = ':' in tokens[0].decode('utf8')  # cheesy, works?
            if local_only and disk.isnet:
                continue
            if disk.ismntd:
                if disk.mntp == '/':
                    disk.rw = True
                else:
                    disk.rw = os.access(disk.mntp, os.W_OK)

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

    sysinf = parse_sysctl(run(syscmd))
    vmstat = parse_vmstat(run(vmscmd))
    if opts.debug:
        print('\n')
        print('sysinf', sysinf)
        print('vmstat:', vmstat)
        print()

    # mem set
    meminfo.memtotal = sysinf['hw.memsize'] / outunit
    meminfo.memfree  = vmstat.free / outunit
    meminfo.used     = (vmstat.wire + vmstat.active) / outunit
    meminfo.cached   = (vmstat.inactive + vmstat.speculative) / outunit
    meminfo.buffers  = 0  # TODO: investigate

    # swap set
    swaptotal, swapused, swapfree = sysinf['vm.swapusage']
    meminfo.swaptotal = swaptotal / outunit
    meminfo.swapused  = swapused  / outunit
    meminfo.swapfree  = swapfree  / outunit
    meminfo.swapcached = 0

    # alternative to calculating used:
    # ~ meminfo.swapused = (meminfo.swaptotal - meminfo.swapcached -
                        # ~ meminfo.swapfree)
    if opts.debug:
        print('meminfo:', meminfo)
    return meminfo


def parse_sysctl(text):
    ''' Parse sysctl output. '''
    lines = text.splitlines()
    results = {}
    for line in lines:
        key, _, value = line.decode('ascii').partition(': ')

        if key == 'hw.memsize':
            value = int(value)

        elif key == 'vm.swapusage':
            values = value.split()[2::3]            # every third token
            su_unit = values[0][-1].lower()         # get unit, 'M'
            PAGESIZE = 1024
            if su_unit == 'm':
                PAGESIZE = 1024 * 1024

            value = [ (float(val[:-1]) * PAGESIZE) for val in values ]

        results[key] = value
    return results


def parse_vmstat(text):
    ''' Parse vmstat output. '''
    lines = text.splitlines()
    results = Info()  # TODO use MemInfo

    try:
        PAGESIZE = int(lines[0].split()[-2])
    except IndexError:
        PAGESIZE = 4096

    for line in lines[1:]:      # dump header
        if not line[0] == 80:   # b'P' startswith Page...
            break
        tokens = line.split()
        name, value = tokens[1][:-1].decode('ascii'), tokens[-1][:-1]
        results[name] = int(value) * PAGESIZE

    return results
