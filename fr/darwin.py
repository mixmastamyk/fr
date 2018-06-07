'''
    darwin.py - (C) 2013, Jonathan Eunice
    derived from linux.py - (C) 2012-13, Mike Miller
    License: GPLv3+.
'''
import os, locale, re
from os.path import basename
from fr.utils import Info, run

devfilter   = ('none', 'tmpfs', 'udev', 'devfs', 'map')
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


def get_diskinfo(outunit, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info,
        stats divided by the ouptut unit.
    '''
    disks = {}
    try:
        lines = run(diskcmd).splitlines()[1:]  # dump header
        for i, line in enumerate(lines):
            if line:
                tokens  = line.split()
                dev = basename(tokens[0])
                disk = Info()
                disk.isram  = None
                if dev in devfilter:
                    if show_all:
                        if tokens[0] == 'map':
                            tokens = [ ' '.join(tokens[0:2]) ] + tokens[2:]
                            dev = basename(tokens[0])
                        dev += str(i)
                        disk.isram = True
                    else:
                        disk.isram = False; continue
                disk.dev = dev
                # convert to bytes, then output units
                disk.ocap   = float(tokens[1]) * 1024
                disk.cap    = disk.ocap / outunit
                disk.free   = float(tokens[3]) * 1024 / outunit
                disk.label  = '' # dummy values for now
                disk.mntp   = ' '.join( tokens[8:] )
                disk.pcnt   = int(tokens[4][:-1])
                disk.used   = float(tokens[2]) * 1024 / outunit
                disk.ismntd = True
                disk.isnet  = ':' in tokens[0]  # cheesy but works
                if local_only and disk.isnet:
                    continue
                disk.isopt  = None
                disk.isrem  = None
                disk.rw     = True

                disks[dev] = disk
    except IOError:
        return None

    if debug:  print disks
    devices = sorted(disks.keys())
    return [ disks[device]  for device in devices ]


def get_meminfo(outunit, debug=False):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.  If mem info can't be read, returns None.
        For Darwin / Mac OS X, interrogates the output of the sysctl and
        vm_stat utilities rather than /proc/meminfo
    '''
    meminfo = Info()
    ms = run('/usr/sbin/sysctl -a hw.memsize'.split(), shell=False)
    su = run('/usr/sbin/sysctl -a vm.swapusage'.split(), shell=False)
    vm = run('/usr/bin/vm_stat', shell=False)

    # Process memsize info info
    memsize = int(ms.split()[1])

    # Process vm_stat
    vmLines = vm.split('\n')
    LINE_RE = re.compile(r'^(.+)\: +(\d+)')
    PAGESIZE = 4096

    vmStats = Info()
    for row in vmLines[1:8]:
        m = LINE_RE.search(row.strip())
        if m:
            name = m.group(1).split()[1]
            vmStats[name] = int(m.group(2)) * PAGESIZE
        else:
            raise ValueError("Can't parse '{0}'".format(row))

    meminfo.MemTotal = memsize / outunit
    meminfo.MemFree  = vmStats.free / outunit
    meminfo.Used     = (vmStats.wired + vmStats.active) / outunit
    meminfo.Cached   = (vmStats.inactive + vmStats.speculative) / outunit
    meminfo.Buffers  = 0

    # Parse vm.swapusage line from sysctl
    SWAPUSAGE_RE = re.compile(
     r'vm\.swapusage: total = ([\d\.]+)M  used = ([\d\.]+)M  free = ([\d\.]+)M'
    )
    m = SWAPUSAGE_RE.search(su.strip())
    if m:
        meminfo.SwapTotal = int(float(m.group(1)))
        meminfo.SwapUsed  = int(float(m.group(2)))
        meminfo.SwapFree  = int(float(m.group(3)))
        meminfo.SwapCached = 0
    else:
        raise ValueError("Can't parse vm.swapusage line from sysctl '{0}'"
                        ).format(su)

    if debug:  print meminfo
    return meminfo

