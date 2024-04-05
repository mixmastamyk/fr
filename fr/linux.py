'''
    linux.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    Data gathering routines located here.
'''
import sys, os, locale
from os.path import basename, join, normpath
from fr.utils import DiskInfo, MemInfo


# defaults
diskdir     = '/dev/disk/by-label'
encoding    = 'utf8'
memfname    = '/proc/meminfo'
mntfname    = '/proc/mounts'
optical_fs  = ('iso9660', 'udf')
selectors   = ('/', 'tmpfs', ':')
col_lbls    = 'MNT CACHE'
col_lblw    = 'MOUNT CACHE'
coloravail  = True
hicolor     = None
boldbar     = None
TERM        = os.environ.get('TERM')
out         = sys.stdout.write
locale.setlocale(locale.LC_ALL, '')


# icons
if TERM == 'linux':             # Basic Linux console, use ascii
    hicolor  = False
    boldbar  = True
    _brckico = ('|', '|')
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
    _remvico = '='
    _unmnico = 'u'
    _usedico = '#'
    _warnico = '!'
elif TERM == 'xterm-256color':  # X11, etc.
    hicolor  = True
    boldbar  = False


class ColorNotAvail(Exception):
    ''' Error: color support not available.  Check $TERM. '''
    def __str__(self):
        return f'{self.__class__.__name__}: {self.__doc__}'


def check_optical(disk):
    ''' Try to determine if a device is optical technology.
        Needs improvement.
    '''
    dev = disk.dev
    if dev.startswith('sr') or ('cd' in dev):
        return True
    elif disk.fmt in optical_fs:
        return True
    else:
        return None


def check_removable(dev, opts):
    ''' Removable drives can be identified under /sys. '''
    try:  # get parent device from sys filesystem, look from right.  :-/
        parent = os.readlink(f'/sys/class/block/{dev}').rsplit("/", 2)[1]
        with open(f'/sys/block/{parent}/removable') as f:
            return f.read() == '1\n'

    except IndexError as err:
        if opts.debug:
            print('ERROR: parent block device not found.', err)
    except IOError as err:
        if opts.debug:
            print('ERROR:', err)


def decode_mntp(mntp):
    ''' Mount point strings have a unique encoding for whitespace. :-/
        https://stackoverflow.com/a/13576641/450917
        https://stackoverflow.com/a/6117124/450917
    '''
    import re
    replacements = {
        r'\\040': ' ',
        r'\\011': '\t',
        r'\\012': '\n',
        r'\\134': '\\',
    }
    pattern = re.compile('|'.join(replacements.keys()))
    return pattern.sub(lambda m: replacements[re.escape(m.group(0))], mntp)


def get_label_map(opts):
    ''' Find volume labels from filesystem and return in dict format. '''
    results = {}
    try:
        for entry in os.scandir(diskdir):
            target = normpath(join(diskdir, os.readlink(entry.path)))
            decoded_name = entry.name.encode('utf8').decode('unicode_escape')
            results[target] = decoded_name
        if opts.debug:
            print('\n\nlabel_map:', results)
    except FileNotFoundError:
        pass
    return results


def get_diskinfo(opts, show_all=False, local_only=False):
    ''' Returns a list holding the current disk info.
        Stats are divided by the outputunit.
    '''
    disks = []
    outunit = opts.outunit
    label_map = get_label_map(opts)

    # get mount info
    try:
        with open(mntfname) as infile:
            lines = infile.readlines()
            lines.sort()
    except IOError:
        return None

    # build list of disks
    for i, line in enumerate(lines):
        device, mntp, fmt, mntops, *_ = line.split()

        if device in ('cgroup',):       # never want these
            continue

        disk = DiskInfo()
        dev = basename(device)          # short name
        disk.isnet  = ':' in device     # cheesy but works
        if local_only and disk.isnet:
            continue
        disk.isimg = is_img = dev.startswith('loop')  # could be better
        is_tmpfs = device in ('tmpfs', 'devtmpfs')

        # lots of junk here, so we throw away most entries
        for selector in selectors:
            if selector in device:
                if show_all:
                    if is_tmpfs:
                        disk.isram = True
                else:  # skip these:
                    if (is_img or
                        is_tmpfs or
                        mntp == '/boot/efi'):
                            continue
                break   # found a useful entry, stop here
        else:           # no-break, nothing was found
            continue    # skip this one

        disk.dev = dev
        disk.fmt = fmt
        disk.mntp = mntp = decode_mntp(mntp) if '\\' in mntp else mntp
        disk.ismntd = bool(mntp)
        disk.isopt = check_optical(disk)
        if device[0] == '/':  # .startswith('/dev'):
            disk.isrem = check_removable(dev, opts)
        disk.label = label_map.get(device)

        # get disk usage information
        # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/sys/statvfs.h.html
        # convert to bytes, then output units
        stat = os.statvfs(mntp)
        disk.ocap  = stat.f_frsize * stat.f_blocks     # keep for later
        disk.cap   = disk.ocap / outunit
        disk.free  = stat.f_frsize * stat.f_bavail / outunit
        disk.oused = stat.f_frsize * (stat.f_blocks - stat.f_bfree) # for later
        disk.used  = disk.oused / outunit
        disk.pcnt  = disk.oused / disk.ocap * 100
        if mntops.startswith('rw'):             # read only
            disk.rw = True
        elif mntops.startswith('ro'):
            disk.rw = False
        else:
            disk.rw = not bool(stat.f_flag & os.ST_RDONLY)

        disks.append(disk)

    if show_all:    # look at /dev/disks again for the unmounted
        for devname in label_map:
            dev = basename(devname)
            exists = [ disk for disk in disks if disk.dev == dev ]
            if not exists:
                disk = DiskInfo(
                    cap=0, free=0, ocap=0, pcnt=0, used=0,
                    dev = dev,
                    ismntd = False, mntp = '',
                    isnet = False,
                    isopt = check_optical(DiskInfo(dev=dev, fmt=None)),
                    isram = False,   # no such thing?
                    isrem = check_removable(dev, opts),
                    label = label_map[devname],
                    rw = None,
                )
                disks.append(disk)
                disks.sort(key=lambda disk: disk.dev)  # sort again :-/

    if opts.debug:
        print()
        for disk in disks:
            print(disk.dev, disk)
            print()
    return disks


def get_meminfo(opts):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.  If mem info can't be read, returns None.
    '''
    meminfo = MemInfo()
    outunit = opts.outunit
    try:
        with open(memfname) as infile:
            lines = infile.readlines()
    except IOError:
        return None

    for line in lines:                      # format: 'MemTotal:  511456 kB\n'
        tokens = line.split()
        if tokens:
            name, value = tokens[0][:-1].lower(), tokens[1]  # rm :
            if len(tokens) == 2:
                continue
            unit = tokens[2].lower()

            # parse_result to bytes  TODO
            value = int(value)
            if   unit == 'kb': value = value * 1024  # most likely
            elif unit ==  'b': value = value
            elif unit == 'mb': value = value * 1024 * 1024
            elif unit == 'gb': value = value * 1024 * 1024 * 1024

            setattr(meminfo, name, value / outunit)

    cache = meminfo.cached + meminfo.buffers
    meminfo.used = meminfo.memtotal - meminfo.memfree - cache
    meminfo.swapused = (meminfo.swaptotal - meminfo.swapcached -
                        meminfo.swapfree)
    return meminfo
