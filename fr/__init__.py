import sys
import locale

from . import ansi


_outunit = 1000000, 'Megabyte'  # 1 Megabyte default
opts, pform = None, None
out = sys.stdout.write
if sys.platform[:3] == 'win':  # :-(
    def out(*args, end=''):
        print(*args, end=end)


# default icons
_ramico  = '⌁'
_diskico = '▪'
_cmonico = '▒'           # cache mono
_discico = '◗'
_ellpico = '…'           # ellipsis
_emptico = '∅'          # empty set
_freeico = '░'
_gearico = '⚙'
_imgico  = '🗎'          # '⦾'
_netwico = '⇅'
_remvico = '⇄'
_unmnico = '▫'
_usedico = '▉'
_warnico = '⚠'
_brckico = ('▕', '▏')    # start, end "brackets"


def load_config(options):
    ''' Load options, platform, and icons. '''
    global opts, pform
    opts = options
    pform = options.pform

    for pvar in dir(pform):
        if pvar.startswith('_') and pvar.endswith('ico'):
            globals()[pvar] = getattr(pform, pvar)


def fmtstr(text='', colorstr=None, align='>', trunc=True, width=0, end=' '):
    ''' Formats, justifies, and returns a given string according to
        specifications.
    '''
    colwidth = width or opts.colwidth

    if trunc:
        if len(text) > colwidth:
            text = truncstr(text, colwidth, align=trunc)  # truncate w/ellipsis

    value = f'{text:{align}{colwidth}}'
    if opts.incolor and colorstr:
        return colorstr % value + end
    else:
        return value + end


def fmtval(value, colorstr=None, precision=None, spacing=True, trunc=True,
           end=' '):
    ''' Formats and returns a given number according to specifications. '''
    colwidth = opts.colwidth
    # get precision
    if precision is None:
        precision = opts.precision
    fmt = '%%.%sf' % precision

    # format with decimal mark, separators
    result = locale.format(fmt, value, True)

    if spacing:
        result = '%%%ss' % colwidth % result

    if trunc:
        if len(result) > colwidth:   # truncate w/ellipsis
            result = truncstr(result, colwidth)

    # Add color if needed
    if opts.incolor and colorstr:
        return colorstr % result + end
    else:
        return result + end


def get_units(unit, binary=False):
    ''' Sets the output unit and precision for future calculations and returns
        an integer and the string representation of it.
    '''
    result = None

    if unit == 'b':
        result = 1, 'Byte'

    elif binary:    # 2^X
        if   unit == 'k':
            result = 1024, 'Kibibyte'
        elif unit == 'm':
            result = 1048576, 'Mebibyte'
        elif unit == 'g':
            if opts.precision == -1:
                opts.precision = 3
            result = 1073741824, 'Gibibyte'
        elif unit == 't':
            if opts.precision == -1:
                opts.precision = 3
            result = 1099511627776, 'Tebibyte'

    else:           #  10^x
        if   unit == 'k':
            result = 1000, 'Kilobyte'
        elif unit == 'm':
            result = 1000000, 'Megabyte'
        elif unit == 'g':
            if opts.precision == -1:
                opts.precision = 3      # new defaults
            result = 1000000000, 'Gigabyte'
        elif unit == 't':
            if opts.precision == -1:
                opts.precision = 3
            result = 1000000000000, 'Terabyte'

    if not result:
        print('Warning: incorrect parameter: %s.' % unit)
        result = _outunit

    if opts.precision == -1:  # auto
        opts.precision = 0
    return result


def print_diskinfo(diskinfo, widelayout, incolor):
    'Disk information output function.'
    sep = ' '
    if opts.relative:
        import math
        base = max([ disk.ocap  for disk in diskinfo ])

    for disk in diskinfo:
        if disk.ismntd:     ico = _diskico
        else:               ico = _unmnico
        if disk.isrem:      ico = _remvico
        if disk.isopt:      ico = _discico
        if disk.isnet:      ico = _netwico
        if disk.isram:      ico = _ramico
        if disk.isimg:      ico = _imgico
        if disk.mntp == '/boot/efi':    # TODO mv this icon setting to pform
                            ico = _gearico

        if opts.relative and disk.ocap and disk.ocap != base:
            # increase log size reduction by raising to 4th power:
            gwidth = int((math.log(disk.ocap, base)**4) * opts.width)
        else:
            gwidth = opts.width

        # check color settings
        if disk.rw:
            ffg = ufg = None        # auto colors
        else:
            ffg = ufg = ansi.dimbb  # dim or dark grey

        if disk.cap and disk.rw:
            lblcolor = ansi.get_label_tmpl(disk.pcnt, opts.width, opts.hicolor)
        else:
            lblcolor = None

        # print stats
        data = (
            (_usedico, disk.pcnt,     ufg,  None,  pform.boldbar), # Used
            (_freeico, 100-disk.pcnt, ffg,  None,  False),         # free
        )
        mntp = fmtstr(disk.mntp, align='<', trunc='left',
                      width=(opts.colwidth * 2) + 2)
        mntp = mntp.rstrip()  # prevent wrap

        if widelayout:
            out(fmtstr(ico + sep + disk.dev, align='<'))
            out(fmtstr(disk.label, align='<'))
            if disk.cap:
                if disk.rw:
                    out(f'{fmtval(disk.cap)}{fmtval(disk.used, lblcolor)}')
                    out(fmtval(disk.free, lblcolor))
                else:
                    out(f'{fmtval(disk.cap)}{fmtstr()}')
                    out(fmtstr(_emptico, ansi.fdimbb))
            else:
                out(fmtstr(_emptico, ansi.fdimbb))

            if disk.cap:
                if disk.rw:  # factoring this caused colored brackets
                    ansi.rainbar(data, gwidth, incolor,
                                 hicolor=opts.hicolor,
                                 cbrackets=_brckico)
                else:
                    ansi.bargraph(data, gwidth, incolor, cbrackets=_brckico)

                if opts.relative and opts.width != gwidth:
                    out(sep * (opts.width - gwidth - 1))
                out(sep + mntp)
            print()
        else:
            out(fmtstr(f'{ico} {disk.dev}', align="<"))
            out(fmtstr(disk.label, align='<'))
            if disk.cap:
                out(f'{fmtval(disk.cap)}{fmtval(disk.used, lblcolor)}')
                out(fmtval(disk.free, lblcolor))
            else:
                out(f'{fmtstr(_emptico, ansi.fdimbb)} {fmtstr()} {fmtstr()}')
            print(sep, mntp)

            if disk.cap:
                out(fmtstr(sep))
                if disk.rw:
                    ansi.rainbar(data, gwidth, incolor, hicolor=opts.hicolor,
                                 cbrackets=_brckico)
                else:
                    ansi.bargraph(data, gwidth, incolor, cbrackets=_brckico)
            print()
            print()
    print()


def print_meminfo(meminfo, widelayout, incolor):
    ''' Memory information output function. '''
    sep = ' '
    # prep Mem numbers
    totl = meminfo.memtotal
    cach = meminfo.cached + meminfo.buffers
    free = meminfo.memfree
    used = meminfo.used
    if opts.debug:
        print(f'\n  totl: {totl}, used: {used}, free: {free}, cach: {cach}\n')

    usep = float(used) / totl * 100           # % used of total ram
    cacp = float(cach) / totl * 100           # % cache
    frep = float(free) / totl * 100           # % free
    rlblcolor = ansi.get_label_tmpl(usep, opts.width, opts.hicolor)

    # Prepare Swap numbers
    swpt = meminfo.swaptotal
    if swpt:
        swpf = meminfo.swapfree
        swpc = meminfo.swapcached
        swpu = meminfo.swapused
        swfp = float(swpf) / swpt * 100       # % free of total sw
        swcp = float(swpc) / swpt * 100       # % cache
        swup = float(swpu) / swpt * 100       # % used
        slblcolor = ansi.get_label_tmpl(swup, opts.width, opts.hicolor)
    else:
        swpf = swpc = swpu = swfp = swcp = swup = 0 # avoid /0 error
        slblcolor = None
    if opts.hicolor:
        swap_color = ansi.csi8_blk % ansi.blu8
    else:
        swap_color = ansi.fbblue
    cacheico = _usedico if incolor else _cmonico

    # print RAM info
    data = (
        (_usedico, usep, None,  None, pform.boldbar),       # used
        (cacheico, cacp, ansi.blue,  None, pform.boldbar),  # cache
        (_freeico, frep, None,  None, False),               # free
    )
    if widelayout:
        out(fmtstr(_ramico + ' RAM', align='<'))
        out(fmtstr(sep))  # volume column
        out(f'{fmtval(totl)}{fmtval(used, rlblcolor)}')
        out(fmtval(free, rlblcolor))

        # print graph
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print('', fmtval(cach, swap_color))
    else:
        out(f'{fmtstr(_ramico + " RAM", align="<")}{fmtstr()}')
        out(f'{fmtval(totl)}{fmtval(used, rlblcolor)}{fmtval(free, rlblcolor)}')
        print(sep, fmtval(cach, swap_color))

        # print graph
        out(fmtstr())
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print() # extra line in narrow layout

    # Swap time:
    data = (
        (_usedico, swup, None,  None, pform.boldbar),   # used
        (_usedico, swcp, None,  None, pform.boldbar),   # cache
        (_freeico, swfp, None,  None, False),           # free
    )
    if widelayout:
        out(fmtstr(_diskico + ' SWAP', align='<'))
        out(fmtstr())  # label placeholder
        if swpt:
            out(fmtval(swpt))
            out(f'{fmtval(swpu, slblcolor)}{fmtval(swpf, slblcolor)}')
        else:
            print(fmtstr(_emptico, ansi.fdimbb))

        # print graph
        if swpt:
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            if swpc:
                out(' ' + fmtval(swpc, swap_color))
            print()
    else:
        out(fmtstr(_diskico + ' SWAP', align='<'))
        out(fmtstr())  # label placeholder
        if swpt:
            out(f'{fmtstr()}{fmtval(swpt)}')
            out(f'{fmtval(swpu, slblcolor)}{fmtval(swpf, slblcolor)}')
            if swpc:
                out('  ' + fmtval(swpc, swap_color))
            print()

            # print graph
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            print()
        else:
            print(fmtstr(_emptico, ansi.fdimbb))
        print()

    print()  # extra newline separates mem and disk sections



def truncstr(text, width, align='right'):
    ''' Truncate a string, with trailing ellipsis. '''
    before = after = ''
    if align == 'left':
        truncated = text[-width+1:]
        before = _ellpico
    elif align:
        truncated = text[:width-1]
        after = _ellpico

    text = f'{before}{truncated}{after}'
    return text



