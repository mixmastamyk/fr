'''
    linux.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    TODO: fix: R/W check is done by current user instead of writable mount.
'''
import sys, os, locale
from os.path import basename, join, normpath
from fr.utils import Info, run

try:
    import dbus
except ImportError:
    dbus = None

selectors   = ('/', 'tmpfs', ':')
diskcmd     = '/bin/df --portability'
memfname    = '/proc/meminfo'
coloravail  = True
hicolor     = None
boldbar     = None
encoding    = 'utf8'
col_lblw    = 'MOUNT CACHE'
col_lbls    = 'MNT CACHE'
TERM        = os.environ.get('TERM')
out         = sys.stdout.write
locale.setlocale(locale.LC_ALL, '')

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



def get_diskinfo(outunit, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info.

        Udisks doesn't provide free/used info, so it is currently gathered
        via the df command.
        Stats are divided by the outputunit.
    '''
    disks = []
    # get labels from filesystem
    label_map = {}
    try:
        basedir = '/dev/disk/by-label'
        for entry in os.scandir(basedir):
            target = normpath(join(basedir, os.readlink(entry.path)))
            decoded_name = entry.name.encode('utf8').decode('unicode_escape')
            label_map[target] = decoded_name
        if debug:
            print('\n\nlabel_map:', label_map)
    except FileNotFoundError:
        pass

    # get mount info
    with open('/proc/mounts') as f:
        lines = f.readlines()
        lines.sort()

    # build list of disks
    for i, line in enumerate(lines):
        tokens = line.split()
        device = tokens[0]
        mntp = tokens[1]
        mntops = tokens[3]
        if device in ('cgroup',):  # never want these
            continue

        disk = Info()
        disk.isnet  = ':' in device  # cheesy but works
        if local_only and disk.isnet:
            continue
        dev = basename(device)
        disk.isram = False

        # lots of junk here, so we throw away most entries
        for selector in selectors:
            if selector in device:
                if show_all:
                    if device == 'tmpfs':
                        disk.isram = True
                else:
                    if (dev.startswith('loop') or
                        dev.startswith('tmpfs') or
                        mntp == '/boot/efi'  ):
                        continue

                break   # found a useful entry
        else:           # not found
            continue    # dump junk

        disk.dev = dev
        # https://stackoverflow.com/a/13576641/450917
        disk.mntp = mntp = mntp.replace(r'\040', ' ')
        disk.ismntd = bool(mntp)

        # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/sys/statvfs.h.html
        stat = os.statvfs(mntp)

        # convert to bytes, then output units
        disk.ocap  = stat.f_frsize * stat.f_blocks     # keep for later
        disk.cap   = disk.ocap / outunit
        disk.free  = stat.f_frsize * stat.f_bavail / outunit
        disk.oused = stat.f_frsize * (stat.f_blocks - stat.f_bfree)
        disk.used  = disk.oused / outunit              # keep for later

        disk.pcnt  = disk.oused / disk.ocap * 100      # TODO: an issue?

        disk.isrem = None           # removable ?
        if dev.startswith('sr') or 'cd' in dev:    # optical ?
            disk.isopt = True
        else:
            disk.isopt = None

        if mntops.startswith('rw'): # read only?
            disk.rw = True
        elif mntops.startswith('ro'):
            disk.rw = False
        else:
            disk.rw = not bool(stat.f_flag & os.ST_RDONLY)

        disk.label = label_map.get(device, '')
        disks.append(disk)

    if debug:
        print()
        for disk in disks:
            print(disk.dev, disk)
            print()
    return disks


def get_diskinfo_old(outunit, show_all=False, debug=False, local_only=False):
    ''' Returns a list holding the current disk info.

        Udisks doesn't provide free/used info, so it is currently gathered
        via the df command.
        Stats are divided by the outputunit.
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
            out('\n' + _warnico + ' Warning: Udisks not avail.')
    else:
        if not dbus:
            out('\n' + _warnico + ' Warning: Dbus not found!')


    def print_stat(fs):
        print('fs:', fs)
        statvfs = os.statvfs(fs)

        print(f'  size: {statvfs.f_frsize * statvfs.f_blocks:n}')   # Total size of filesystem in bytes
        print(f'''  used: {
            statvfs.f_frsize * (statvfs.f_blocks - statvfs.f_bfree)
        :n}''')    # Actual number of free bytes
        print(f'  aval: {statvfs.f_frsize * statvfs.f_bavail:n}')   # Number of free bytes that ordinary users
        print()                                                     # are allowed to use (excl. reserved space)

    if debug:
        print('\nDbus found:', dbus, '\n')

    for i, (dev, disk) in enumerate(disks.items()):

        # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/sys/statvfs.h.html
        stat = os.statvfs(disk.mntp)

        disk.isnet  = None    # TODO, fix net check
        if local_only and disk.isnet:
            continue

        if dev in devfilter:
            if show_all:
                if dev == 'tmpfs':
                    dev += str(i)
                    disk.isram = True
                else:
                    disk.isram = False
            else:
                continue
        disk.dev = dev

        #~ # convert to bytes, then output units
        disk.ocap   = stat.f_frsize * stat.f_blocks  # keep for later
        disk.cap    = disk.ocap / outunit
        disk.free   = stat.f_frsize * stat.f_bavail / outunit
        disk.oused  = stat.f_frsize * (stat.f_blocks - stat.f_bfree)
        disk.used   = disk.oused / outunit  # keep for later

        disk.pcnt   = disk.oused / disk.ocap * 100  # TODO: an issue

        disk.isram  = None  # TODO ???
        disk.isrem  = None
        disk.rw     = not bool(stat.f_flag & os.ST_RDONLY)
        disk.isopt  = None

        if debug:
            print('\n', str(dev) + ':')
            from pprint import pprint
            pprint(disk)

    devices = sorted(disks.keys())
    return [ disks[device]  for device in devices ]


def get_udisks2_info(disks, show_all, debug):
    ''' Current version of Udisks. '''
    dbus_api = 'org.freedesktop.UDisks2'
    dbus_base = 'org.freedesktop.UDisks2.'
    dbus_dev_blk = dbus_base + 'Block'
    dbus_dev_drv = dbus_base + 'Drive'
    dbus_dev_fss = dbus_base + 'Filesystem'
    dbus_mgr = 'org.freedesktop.DBus.ObjectManager'
    try:
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
                rw = not bool(block_info['ReadOnly'])  # mount or user access?

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
                                    ismntd=ismntd, rw=rw,
                              ) # firstmnt=firstmnt,
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

