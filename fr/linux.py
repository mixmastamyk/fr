'''
    linux.py - (C) 2012-18, Mike Miller
    License: GPLv3+.

    TODO: fix: R/W check is done by current user instead of writable mount.
'''
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
#~ diskcmd     = '/bin/cat df.txt'  # for testing
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
                disk.isnet  = ':' in tokens[0]  # cheesy but works
                if local_only and disk.isnet:
                    continue
                dev = basename(tokens[0])
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
                disk.mntp   = ' '.join( tokens[5:] )
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
        if err:  # fall back to udisks 1
            err = get_udisks_info(disks, show_all, debug)
        if err and 'ServiceUnknown' in str(err):
            print _warnico + ' Udisks not avail.'
    else:
        if not dbus:
            print '\nWarning: Dbus not found!',

    if debug:
        print
        print 'Dbus found:', dbus, '\n'
        for disk in disks:
            print disk + ':', disks[disk]
    devices = sorted(disks.keys())
    return [ disks[device]  for device in devices ]


def get_udisks_info(disks, show_all, debug):
    ''' Obsolete version of Udisks. '''
    dbus_api = 'org.freedesktop.UDisks'
    dbus_dev = 'org.freedesktop.UDisks.Device'
    try:
        bus = dbus.SystemBus() # Get on the bus... and pay your fare...
        udisks = bus.get_object(dbus_api, '/' + dbus_api.replace('.','/'))
        udisks = dbus.Interface(udisks, dbus_api)

        isnet = False  # only local drives enumerated here
        for devpath in udisks.EnumerateDevices():
            devobj = bus.get_object(dbus_api, devpath)
            devobj = dbus.Interface(devobj, dbus.PROPERTIES_IFACE)

            dev = basename(devpath)
            lbl = unicode(devobj.Get(dbus_dev, 'IdLabel'))
            ismntd = bool(devobj.Get(dbus_dev, 'DeviceIsMounted'))
            ispart = devobj.Get(dbus_dev, 'DeviceIsPartition')
            dtype = devobj.Get(dbus_dev, 'IdType')
            ptype = devobj.Get(dbus_dev, 'PartitionType')
            psize = devobj.Get(dbus_dev, 'PartitionSize')
            isopt = bool(devobj.Get(dbus_dev, 'DeviceIsOpticalDisc'))
            #~ isrem = devobj.Get(dbus_dev, 'DeviceIsRemovable')# !reliable
            isrem = not devobj.Get(dbus_dev, 'DeviceIsSystemInternal')

            rw = False
            if ismntd:
                firstmnt = devobj.Get(dbus_dev, 'DeviceMountPaths')[0]
                if firstmnt == '/':   rw = True
                else:                 rw = os.access(firstmnt, os.W_OK)

                thisone = dict(dev=dev, label=lbl, rw=rw,
                               ismntd=ismntd, isopt=isopt, isrem=isrem,
                               isram=False, isnet=isnet)
                if dev in disks:
                    disks[dev].update(thisone)
                else:
                    disks[dev] = Info(**thisone)

                disks[dev].setdefault('mntp', '')
                disks[dev].setdefault('pcnt', 0)
            else:
                if show_all:
                    if dtype != 'swap' and ptype != '0x05': # extended part.
                        disk = Info(dev=dev, cap=0, used=0, free=0,
                                pcnt=0, ocap=0, mntp='', label=lbl,
                                rw=rw, ismntd=ismntd, isrem=isrem,
                                isopt=isopt, isram=0, isnet=isnet)
                        disks[dev] = disk

            if debug:
                print devpath, dtype, ptype, psize,
                print 'rem:', isrem, ' opt:', isopt,
                print ' part:', ispart, ' rw:', rw, ' mnt:', ismntd
        err = None
    except dbus.exceptions.DBusException as err:
        pass
    return err


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
        udevices = tuple(udisks2.GetManagedObjects().iteritems())
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
                        firstmnt = ''.join([ chr(c) for c in mounts[0] if c ])
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
        memf = file(memfname, 'r')
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
            if   unit == 'kb': value = value * 1024  # most likely
            elif unit ==  'b': value = value
            elif unit == 'mb': value = value * 1024 * 1024
            elif unit == 'gb': value = value * 1024 * 1024 * 1024
            setattr(meminfo, name, value / float(outunit))

    cach = meminfo.Cached + meminfo.Buffers
    meminfo.Used = meminfo.MemTotal - meminfo.MemFree - cach
    meminfo.SwapUsed = (meminfo.SwapTotal - meminfo.SwapCached -
                        meminfo.SwapFree)
    return meminfo

