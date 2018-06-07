import sys
import locale
out             = sys.stdout.write

# "icons"
_ramico         = '⌁'
_diskico        = '▪'
_unmnico        = '▫'
_remvico        = '⇄'
_netwico        = '⇅'
_discico        = '◗'
_emptico        = '∅'           # empty set
_ellpico        = '…'           # ellipsis
_usedico        = '▉'
_cmonico        = '▒'           # cache mono
_freeico        = '░'
_warnico        = '⚠'
_brckico        = ('▕', '▏')    # start, end "brackets"


def fmtstr(text, colorstr=None, leftjust=False, trunc=True):
    ''' Formats and returns a given string according to specifications. '''
    if leftjust:  width = -colwidth
    else:         width =  colwidth
    if trunc:
        cwd = (colwidth * 2) if trunc == 'left' and plat != 'win' else colwidth
        if len(text) > cwd:
            text = truncstr(text, cwd, align=trunc)  # truncate w/ellipsis
    value = '%%%ss' % width %  text
    if opts.incolor and colorstr:
        return colorstr % value
    else:
        return value


def fmtval(value, colorstr=None, override_prec=None, spacing=True, trunc=True):
    ''' Formats and returns a given number according to specifications. '''
    # get precision
    if override_prec is None:
        override_prec = opts.precision
    fmt = '%%.%sf' % override_prec

    # format with decimal mark, separators
    result = locale.format(fmt, value, True)

    if spacing:
        result = '%%%ss' % colwidth % result

    if trunc:
        if len(result) > colwidth:   # truncate w/ellipsis
            result = truncstr(result, colwidth)

    # Add color if needed
    if opts.incolor and colorstr:
        return colorstr % result
    else:
        return result


def out(*args):
    'temporary output until move to 3.x'
    print(*args, end='')


def print_meminfo(meminfo, widelayout, incolor):
    ''' Memory information output function. '''
    # prep Mem numbers
    totl = meminfo.MemTotal
    cach = meminfo.Cached + meminfo.Buffers
    free = meminfo.MemFree
    used = meminfo.Used
    if opts.debug:
        print('totl:', totl)
        print('used:', used)
        print('free:', free)
        print('cach:', cach)

    usep = float(used) / totl * 100           # % used of total ram
    cacp = float(cach) / totl * 100           # % cache
    frep = float(free) / totl * 100           # % free
    rlblcolor = ansi.get_label_tmpl(usep, opts.width, opts.hicolor)

    # Prepare Swap numbers
    swpt = meminfo.SwapTotal
    if swpt:
        swpf = meminfo.SwapFree
        swpc = meminfo.SwapCached
        swpu = meminfo.SwapUsed
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
        out(fmtstr(_ramico + ' RAM', leftjust=True))
        if opts.showlbs:
            out(fmtstr(' '))
        out(fmtval(totl), fmtval(used, rlblcolor))
        out(fmtval(free, rlblcolor))

        # print graph
        out(' ')  # two extra spaces right
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print(' ', fmtval(cach, swap_color))
    else:
        out(fmtstr(_ramico + ' RAM', leftjust=True), fmtstr(' '))
        out(fmtval(totl), fmtval(used, rlblcolor), fmtval(free, rlblcolor))
        print(' ', fmtval(cach, swap_color))

        # print graph
        out(fmtstr(' ')) # one space
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print('\n') # extra line in narrow layout

    # Swap time:
    data = (
        (_usedico, swup, None,  None, pform.boldbar),    # used
        (_usedico, swcp, None,  None, pform.boldbar),    # cache
        (_freeico, swfp, None,  None, False),    # free
    )
    if widelayout:
        out(fmtstr(_diskico + ' SWAP', leftjust=True))
        if opts.showlbs:
            out(fmtstr(' '))
        if swpt:
            out(fmtval(swpt))
            out(fmtval(swpu, slblcolor), fmtval(swpf, slblcolor))
        else:
            print(fmtstr(_emptico, ansi.fdimbb))

        # print graph
        if swpt:
            out(' ')  # two extra spaces right
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            if swpc:
                out(' ', fmtval(swpc, swap_color))
            print()
    else:
        out(fmtstr(_diskico + ' SWAP', leftjust=True))
        if swpt:
            out(fmtstr(' '), fmtval(swpt))
            out(fmtval(swpu, slblcolor), fmtval(swpf, slblcolor))
            if swpc:
                out(' ', fmtval(swpc, swap_color))
            print()

            # print graph
            out(fmtstr(' '))  # one space
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            print()
        else:
            print(fmtstr(_emptico, ansi.fdimbb))
        print()
    print() # extra newline that separates mem and disk sections


def print_diskinfo(diskinfo, widelayout, incolor):
    'Disk information output function.'
    if opts.relative:
        base = max([ disk.ocap  for disk in diskinfo ])

    for disk in diskinfo:
        if disk.ismntd:     ico = _diskico
        else:               ico = _unmnico
        if disk.isrem:      ico = _remvico
        if disk.isopt:      ico = _discico
        if disk.isnet:      ico = _netwico
        if disk.isram:
            ico = _ramico
            disk.dev = ''

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
        if widelayout:
            out(fmtstr('%s %s' % (ico, disk.dev), leftjust=True))
            if opts.showlbs:
                out(fmtstr(disk.label, leftjust=True))
            if disk.cap:
                if disk.rw:
                    out(fmtval(disk.cap), fmtval(disk.used, lblcolor))
                    out(fmtval(disk.free, lblcolor))
                else:
                    out(fmtval(disk.cap), fmtstr(''))
                    out(fmtstr(_emptico, ansi.fdimbb))
            else:
                out(fmtstr(_emptico, ansi.fdimbb), fmtstr(''), fmtstr(''))

            if disk.cap:
                out(' ')
                if disk.rw:
                    ansi.rainbar(data, gwidth, incolor, hicolor=opts.hicolor,
                                 cbrackets=_brckico)
                else:
                    ansi.bargraph(data, gwidth, incolor, cbrackets=_brckico)

                if opts.relative and opts.width != gwidth:
                    out(' ' * (opts.width - gwidth - 1))
                out(' ', fmtstr(disk.mntp, leftjust=True, trunc='left'))
            print()
        else:
            out(fmtstr('%s %s' % (ico, disk.dev), leftjust=True))
            if opts.showlbs:
                out(fmtstr(disk.label, leftjust=True))
            if disk.cap:
                out(fmtval(disk.cap), fmtval(disk.used, lblcolor))
                out(fmtval(disk.free, lblcolor))
            else:
                out(fmtstr(_emptico, ansi.fdimbb), fmtstr(''), fmtstr(''))
            print(' ', fmtstr(disk.mntp, leftjust=True, trunc=False))

            if disk.cap:
                out(fmtstr(' '))
                if disk.rw:
                    ansi.rainbar(data, gwidth, incolor, hicolor=opts.hicolor,
                                 cbrackets=_brckico)
                else:
                    ansi.bargraph(data, gwidth, incolor, cbrackets=_brckico)
            print()
            print()
    print()


def set_outunit(unit):
    ''' Sets the output unit and precision for future calculations and returns
        the string representation of it.
    '''
    if   unit == '-b' or unit == '-bb':
        result = 1, 'Byte'
    elif unit == '-k':
        result = 1000, 'Kilobyte'  # "real" kb
    elif unit == '-kb':
        result = 1024, 'Kibibyte'  # binary kb
    elif unit == '-m':
        result = 1000000, 'Megabyte'
    elif unit == '-mb':
        result = 1048576, 'Mebibyte'
    elif unit == '-g':
        if opts.precision == -1:
            opts.precision = 3  # new defaults
        result = 1000000000, 'Gigabyte'

    elif unit == '-gb':                 # binary gigabytes
        if opts.precision == -1:
            opts.precision = 3
        result = 1073741824, 'Gibibyte'

    elif unit == '-t':
        if opts.precision == -1:
            opts.precision = 3
        result = 1000000000000, 'Terabyte'

    elif unit == '-tb':
        if opts.precision == -1:
            opts.precision = 3
        result = 1099511627776, 'Tebibyte'

    else:    # Default
        print('Warning: incorrect parameter: %s.' % unit)
        result = _outunit

    if opts.precision == -1:
        opts.precision = 0
    return result


def truncstr(text, width, align='right'):
    ''' Truncate a string, ending in ellipsis if necessary. '''
    before = after = ''
    if align == 'left':
        truncated = text[-width+1:]
        before = _ellpico.decode(pform.encoding) if plat == 'win' else _ellpico
    elif align:
        truncated = text[:width-1]
        after = _ellpico.decode(pform.encoding) if plat == 'win' else _ellpico

    text = (before + truncated + after)
    if plat == 'win':
        text = text.encode(pform.encoding)  # :(
    return text



