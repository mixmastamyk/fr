'''
    windows.py - (C) 2012-13, Mike Miller
    License: GPLv3+.
'''
import sys, os, locale, stat, platform
try:
    from winstats import ( _diskusage, get_drives, get_drive_type, get_fs_usage,
                           get_perf_data, get_perf_info, get_mem_info,
                           get_vol_info )
except ImportError:
    sys.exit('Error: winstats module not found.  C:\> pip install winstats')

try:
    import colorama
    colorama.init()
    coloravail = True
except ImportError:
    coloravail = False

from fr.utils import Info


version = platform.win32_ver()[1]
win7ver = '6.1.7600'
vistver = '6.0.6000'

hicolor  = False
boldbar  = True
col_lblw = 'CACHE'
col_lbls = 'CACHE'

# icons and graphics chars
encoding = 'cp437'
locale.setlocale(locale.LC_ALL, ('english_united-states', '437'))
locale.setlocale(locale.LC_NUMERIC, '')
_ramico  = '\xf0'       # three horz lines
_diskico = '\xfe'       # block
_unmnico = '\7f'        # empty house
_remvico = '\x1d'       # <->
_netwico = '\x17'       # ^V
_discico = '\xe8'       # cap phi
_emptico = '\xed'       # lc phi
_ellpico = '\xaf'       # >>
_usedico = '\xfe'       # block
_cmonico = '\x04'       # cache mono
_freeico = '\xf9'       # dot
_brckico = ('\xb3', '\xb3') # vert line

_drive_type_result = {
    0: ('unk', None),       # UNKNOWN
    1: ('err', None),       # NO_ROOT_DIR
    2: ('isrem', True),     # REMOVABLE
    3: ('isrem', False),    # FIXED
    4: ('isnet', True),     # REMOTE
    5: ('isopt', True),     # CDROM
    6: ('isram', True),     # RAMDISK
}


def get_diskinfo(outunit, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info,
        stats divided by the ouptut unit.
    '''
    disks = {}
    for drive in get_drives():
        drive += ':\\'
        disk = Info(dev=drive)
        try:  usage = get_fs_usage(drive)
        except WindowsError:  # disk not ready, request aborted, etc.
            if show_all:  usage = _diskusage(0, 0, 0)
            else:         continue
        disk.ocap   = usage.total
        disk.cap    = usage.total / outunit
        disk.used   = usage.used / outunit
        disk.free   = usage.free / outunit
        disk.label  = get_vol_info(drive).name
        if usage.total:
            disk.pcnt = float(usage.used) / usage.total * 100
        else:
            disk.pcnt = 0
        disk.mntp   = ''
        disk.ismntd = True
        disk.isnet  = None
        disk.isopt  = None
        disk.isram  = None
        disk.isrem  = None
        dtint, dtstr = get_drive_type(drive)
        setattr(disk, *_drive_type_result[dtint])
        #~ disk.rw = os.access(drive, os.W_OK) # doesn't work on optical
        if usage.total:    # this not giving correct result on Win7 RTM either
            disk.rw = stat.S_IMODE(os.stat(drive).st_mode) & stat.S_IWRITE
        else:
            disk.rw = False
        disks[drive] = disk

    if debug:  print disks
    keys = sorted(disks.keys())
    return [ disks[dev]  for dev in keys ]



def get_meminfo(outunit, debug=False):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.
    '''
    meminfo = Info()
    mstat = get_mem_info()  # from winstats
    pinf = get_perf_info()
    try:
        pgpcnt = get_perf_data(r'\Paging File(_Total)\% Usage', 'double')[0] / 100
    except WindowsError:
        pgpcnt = 0

    totl = mstat.TotalPhys
    meminfo.MemTotal = totl / float(outunit)
    used = totl * mstat.MemoryLoad / 100.0  # percent, more reliable
    meminfo.Used = used / float(outunit)
    left = totl - used

    # Cached
    cach = pinf.SystemCacheBytes
    if cach > left and version >= win7ver:
        # Win7 RTM bug :/ this cach number is bogus
        free = get_perf_data(r'\Memory\Free & Zero Page List Bytes', 'long')[0]
        cach = left - free
        meminfo.MemFree = free / float(outunit)
    else:
        meminfo.MemFree = (totl - used - cach) / float(outunit)
    meminfo.Buffers = 0

    meminfo.Cached = cach / float(outunit)

    # SWAP  these numbers are actually commit charge, not swap; fix
    #       should not contain RAM :/
    swpt = abs(mstat.TotalPageFile - totl)
    # these nums aren't quite right either, use perfmon instead :/
    swpu = swpt * pgpcnt
    swpf = swpt - swpu

    meminfo.SwapTotal = swpt / float(outunit)
    meminfo.SwapFree = swpf / float(outunit)
    meminfo.SwapUsed = swpu / float(outunit)
    meminfo.SwapCached = 0  # A linux stat for compat

    if debug:
        import locale
        fmt = lambda x: locale.format('%d', x, True)
        print
        print 'TotalPhys:', fmt(totl)
        print 'AvailPhys:', fmt(mstat.AvailPhys)
        print 'MemoryLoad:', fmt(mstat.MemoryLoad)
        print
        print 'used:', fmt(used)
        print 'left:', fmt(left)
        if 'free' in locals(): print 'PDH Free:', fmt(free)
        print 'SystemCacheBytes:', fmt(pinf.SystemCacheBytes)
        print
        print 'TotalPageFile:', fmt(mstat.TotalPageFile)
        print 'AvailPageFile:', fmt(mstat.AvailPageFile)
        print 'TotalPageFile fixed:', fmt(swpt)
        print 'AvailPageFile fixed:', fmt(swpf)

    return meminfo

