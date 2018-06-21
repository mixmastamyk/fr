'''
    windows.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    Data gathering routines located here.
'''
import sys, os, locale
import platform
import stat

from fr.utils import DiskInfo, MemInfo

try:
    from winstats import (_diskusage, get_drives, get_drive_type, get_fs_usage,
                          get_perf_data, get_perf_info, get_mem_info,
                          get_vol_info)
except ImportError:
    sys.exit('Error: winstats module not found.  C:\> pip3 install winstats')

# icons and graphics chars?
locale.setlocale(locale.LC_NUMERIC, '')
#~ locale.setlocale(locale.LC_ALL, ('english_united-states', '437'))
#~ os_encoding = locale.getpreferredencoding()
#~ print('\n***********  encoding:', os_encoding)  # cp1252

# pkg below seems to work, but most chars not available under win7 fonts
#~ import win_unicode_console       # must go before colorama
#~ win_unicode_console.enable()
#~ win_unicode_console.disable()
try:
    import colorama
    colorama.init()
    coloravail = True
except ImportError:
    coloravail = False

version  = platform.win32_ver()[1]
win7ver  = '6.1.7600'
vistver  = '6.0.6000'
hicolor  = False
boldbar  = True
col_lblw = 'CACHE'
col_lbls = 'CACHE'

# cp 437, doesn't work any more.  :-/
# cp 1252 - blah
#~ _brckico = ('\x7c', '\xb3') # vert line
#~ _cmonico = '\x04'       # cache mono
#~ _discico = '\xe8'       # cap phi
#~ _diskico = '\xfe'       # block
#~ _ellpico = '\xaf'       # >>
#~ _emptico = '\xed'       # lc phi
#~ _freeico = '\xf9'       # dot
#~ _imgico  = 'i'
#~ _netwico = '\x17'       # ^V
#~ _ramico  = '\xf0'       # three horz lines
#~ _remvico = '\x1d'       # <->
#~ _unmnico = '\7f'        # empty house
#~ _usedico = '\xfe'       # block

# ascii  :-/
_brckico = ('[', ']')
_cmonico = '/'
_discico = 'o'
_diskico = 'd'
_ellpico = '~'
_emptico = '0'
_freeico = '-'
_gearico = 's'
_imgico  = 'i'
_netwico = 'n'
_ramico  = 'r'
_remvico = '>'
_unmnico = 'u'
_usedico = '#'

try:
    os.EX_OK
except AttributeError:  # set exit codes
    os.EX_OK = 0
    os.EX_IOERROR = 74

_drive_type_result = {
    0: ('unk', None),       # UNKNOWN
    1: ('err', None),       # NO_ROOT_DIR
    2: ('isrem', True),     # REMOVABLE
    3: ('isrem', False),    # FIXED
    4: ('isnet', True),     # REMOTE
    5: ('isopt', True),     # CDROM
    6: ('isram', True),     # RAMDISK
}


class ColorNotAvail(Exception):
    ''' Error: color support not available.  Install colorama:
        pip3 install colorama
    '''
    def __str__(self):
        return f'{self.__class__.__name__}: {self.__doc__}'


def get_diskinfo(opts, show_all=False, local_only=False):
    ''' Returns a list holding the current disk info,
        stats divided by the ouptut unit.
    '''
    disks = []
    outunit = opts.outunit

    for drive in get_drives():
        drive += ':\\'
        disk = DiskInfo(dev=drive)
        try:
            usage = get_fs_usage(drive)
        except WindowsError:  # disk not ready, request aborted, etc.
            if show_all:
                usage = _diskusage(0, 0, 0)
            else:
                continue
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
        disk.ismntd = True  # TODO needs work

        # type is not working on Win7 under VirtualBox?
        dtint, dtstr = get_drive_type(drive)
        setattr(disk, *_drive_type_result[dtint])

        disk.rw = os.access(drive, os.W_OK)  # doesn't work on optical
        if usage.total:    # this not giving correct result on Win7 RTM either
            disk.rw = stat.S_IMODE(os.stat(drive).st_mode) & stat.S_IWRITE
        else:
            disk.rw = False
        disks.append(disk)

    if opts.debug:
        for disk in disks:
            print(disk.dev, disk, '\n')
    return disks


def get_meminfo(opts):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.
    '''
    meminfo = MemInfo()
    outunit = opts.outunit
    mstat = get_mem_info()  # from winstats
    pinf = get_perf_info()
    try:
        pgpcnt = get_perf_data(r'\Paging File(_Total)\% Usage',
                                'double')[0] / 100
    except WindowsError:
        pgpcnt = 0

    totl = mstat.TotalPhys
    meminfo.memtotal = totl / float(outunit)
    used = totl * mstat.MemoryLoad / 100.0  # percent, more reliable
    meminfo.used = used / float(outunit)
    left = totl - used

    # Cached
    cache = pinf.SystemCacheBytes
    if cache > left and version >= win7ver:
        # Win7 RTM bug :/ this cache number is bogus
        free = get_perf_data(r'\Memory\Free & Zero Page List Bytes', 'long')[0]
        cache = left - free
        meminfo.memfree = free / float(outunit)
    else:
        meminfo.memfree = (totl - used - cache) / float(outunit)
    meminfo.buffers = 0

    meminfo.cached = cache / float(outunit)

    # SWAP  these numbers are actually commit charge, not swap; fix
    #       should not contain RAM :/
    swpt = abs(mstat.TotalPageFile - totl)
    # these nums aren't quite right either, use perfmon instead :/
    swpu = swpt * pgpcnt
    swpf = swpt - swpu

    meminfo.swaptotal = swpt / float(outunit)
    meminfo.swapfree = swpf / float(outunit)
    meminfo.swapused = swpu / float(outunit)
    meminfo.swapcached = 0  # A linux stat for compat

    if opts.debug:
        import locale
        fmt = lambda val: locale.format('%d', val, True)
        print()
        print('TotalPhys:', fmt(totl))
        print('AvailPhys:', fmt(mstat.AvailPhys))
        print('MemoryLoad:', fmt(mstat.MemoryLoad))
        print()
        print('used:', fmt(used))
        print('left:', fmt(left))
        if 'free' in locals():
            print('PDH Free:', fmt(free))
        print('SystemCacheBytes:', fmt(pinf.SystemCacheBytes))
        print()
        print('TotalPageFile:', fmt(mstat.TotalPageFile))
        print('AvailPageFile:', fmt(mstat.AvailPageFile))
        print('TotalPageFile fixed:', fmt(swpt))
        print('AvailPageFile fixed:', fmt(swpf))

    return meminfo
