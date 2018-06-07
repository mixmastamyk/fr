'''
    linux.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    TODO: fix: R/W check is done by current user instead of writable mount.
'''
from __future__ import print_function
import os, locale
from os.path import basename
from fr.utils import Info, run

try:
    import dbus
except ImportError:
    dbus = None

devfilter   = ( ('none', 'tmpfs', 'udev', 'cgroup_root') +
                 tuple('loop%d' % i  for i in range(10)) )
diskcmd     = '/bin/df --portability'
memfname    = '/proc/meminfo'
coloravail  = True
hicolor     = None
boldbar     = None
encoding    = 'utf8'
col_lblw    = 'MOUNT CACHE'
col_lbls    = 'MNT CACHE'
TERM        = os.environ.get('TERM')

if TERM == 'linux':  # basic console, use ascii
    _ramico     = 'r'
    _diskico    = 'd'
    _unmnico    = 'u'
    _remvico    = 'm'
    _netwico    = 'n'
    _discico    = 'o'
    _emptico    = '0'
    _ellpico    = '~'
    _usedico    = '#'
    _freeico    = '-'
    _warnico    = '!'
    _brckico    = ('[', ']')
    hicolor     = False
    boldbar     = True
elif TERM == 'xterm-256color':
    hicolor     = True
    boldbar     = False

locale.setlocale(locale.LC_ALL, '')
def out(*args):
    'temporary output until move to 3.x'
    print(*args, end='')


def get_diskinfo(outunit, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info,
        stats divided by the ouptut unit.

        Udisks doesn't provide free/used info, so it is currently gathered
        via the df command.
    '''
    disks = {}
    try:
        lines = run(diskcmd).splitlines()[1:]  # dump header
        for i, line in enumerate(lines):
            if line:
                tokens  = line.split()
                disk = Info()
                disk.isnet  = b':' in tokens[0]  # cheesy but works
                if local_only and disk.isnet:
                    continue
                dev = basename(tokens[0]).decode('utf8')
                if dev in devfilter:
                    if show_all:
                        if dev == 'tmpfs':
                            dev += str(i)           # give a name
                            disk.isram = True
                        else:
                            disk.isram = False   # uncertain now with loop
                    else:
                        continue
                disk.dev = dev
                disk.mntp   = ' '.join(t.decode('utf8') for t in tokens[5:])
                if (not show_all) and disk.mntp == '/boot/efi':
                    continue  # skip

                # convert to bytes, then output units
                disk.ocap   = float(tokens[1]) * 1024
                disk.cap    = disk.ocap / outunit
                disk.free   = float(tokens[3]) * 1024 / outunit
                disk.label  = '' # dummy values for now
                disk.pcnt   = int(tokens[4][:-1])
                disk.used   = float(tokens[2]) * 1024 / outunit
                disk.ismntd = True
                disk.isopt  = None
                disk.isram  = None
                disk.isrem  = None
                disk.rw     = True

                disks[dev] = disk
    except IOError:
        return None

    if dbus:  # request volume details, add to disks
        err = get_udisks2_info(disks, show_all, debug)
        if err and 'ServiceUnknown' in str(err):
            out('\n' + _warnico + ' Udisks not avail.')
    else:
        if not dbus:
            out('\n' + _warnico + 'Warning: Dbus not found!')

    if debug:
        out('\nDbus found:', dbus, '\n')
        for disk in disks:
            print(str(disk) + ':', disks[disk])

    #~ print('***** keys:', disks.keys())
    devices = sorted(disks.keys())
    return [ disks[device]  for device in devices ]


def get_udisks2_info(disks, show_all, debug):
    ''' Current version of Udisks. '''
    try:
        dbus_api = 'org.freedesktop.UDisks2'
        dbus_base = 'org.freedesktop.UDisks2.'
        dbus_dev_blk = dbus_base + 'Block'
        dbus_dev_drv = dbus_base + 'Drive'
        dbus_dev_fss = dbus_base + 'Filesystem'
        dbus_mgr = 'org.freedesktop.DBus.ObjectManager'

        bus = dbus.SystemBus()
        udisks2 = bus.get_object(dbus_api, '/' + dbus_api.replace('.','/'))
        udisks2 = dbus.Interface(udisks2, dbus_mgr)
        isnet = None    # only local drives enumerated here
        udisk_drives = {}

        # first look at drives
        udevices = tuple(udisks2.GetManagedObjects().items())
        for devpath, obj in udevices:
            if dbus_dev_drv in obj:
                disk_info = obj.get(dbus_dev_drv, {})
                udisk_drives[devpath] = {
                    'isejt': bool(disk_info['Ejectable']),
                    'isopt': bool(disk_info['Optical']),
                    'isrem': bool(disk_info['Removable']),
                }

        # get filesystem info
        # TODO: figure devpath, drive_path duplication below?
        for devpath, obj in udevices:
            if dbus_dev_fss in obj:
                dev = basename(devpath)
                if (not show_all) and dev in devfilter:
                    continue

                block_info = obj.get(dbus_dev_blk, {})
                #~ print('_:')
                #~ print('*****************:', devpath)
                #~ from pprint import pprint
                #~ pprint(block_info)
                #~ print('_:')
                drive_path = str(block_info['Drive'])
                lbl = str(block_info['IdLabel'])
                rw = False

                # get mount point
                ismntd, firstmnt = None, None
                fsys_info = obj.get(dbus_dev_fss, {})
                if fsys_info:
                    mounts = fsys_info.get('MountPoints')
                    if mounts:
                        # convert from array of bytes to string w/o null :/
                        firstmnt = ''.join(chr(c) for c in mounts[0] if c)
                        if firstmnt == '/boot/efi' and not show_all:
                            continue  # skip
                        ismntd = True

                if ismntd: # mounted, check read-write
                    if firstmnt == '/':
                        rw = True  # force True
                    else:
                        rw = os.access(firstmnt, os.W_OK)
                    thisone = dict( label=lbl, drive=drive_path, isnet=isnet,
                                    ismntd=ismntd, firstmnt=firstmnt, rw=rw,
                              )
                    thisone.update(**udisk_drives.get(drive_path, {}))
                    if dev in disks:
                        disks[dev].update(thisone)
                    else:
                        disks[dev] = Info(**thisone)

                    disks[dev].setdefault('mntp', firstmnt or '')
                    disks[dev].setdefault('pcnt', 0)
                else:
                    if show_all:
                        if True:    # dtype != 'swap' and ptype != '0x05':
                                    # extended part.
                            disk = Info(dev=dev, cap=0, used=0, free=0,
                                    pcnt=0, ocap=0, mntp='', label=lbl,
                                    rw=rw, ismntd=ismntd, isram=0, isnet=isnet,
                                    **udisk_drives.get(drive_path, {}))
                            disks[dev] = disk
        err = None
    except dbus.exceptions.DBusException as err:
        pass
    return err


def get_meminfo(outunit, debug=False):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.  If mem info can't be read, returns None.
    '''
    meminfo = Info()
    if os.access(memfname, os.R_OK):
        memf = open(memfname, 'r')
    else:
        return None

    for line in memf:  # format: 'MemTotal:  511456 kB\n'
        tokens = line.split()
        if tokens:
            name, value = tokens[0][:-1], tokens[1]  # rm :
            if len(tokens) > 2:
                unit = tokens[2].lower()
            # parse_result to bytes
            value = int(value)
            if   unit == 'kb': value = value * 1024  # most likely  - NOT
            elif unit ==  'b': value = value
            elif unit == 'mb': value = value * 1024 * 1024
            elif unit == 'gb': value = value * 1024 * 1024 * 1024
            setattr(meminfo, name, value / float(outunit))

    cach = meminfo.Cached + meminfo.Buffers
    meminfo.Used = meminfo.MemTotal - meminfo.MemFree - cach
    meminfo.SwapUsed = (meminfo.SwapTotal - meminfo.SwapCached -
                        meminfo.SwapFree)
    return meminfo

