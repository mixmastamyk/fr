'''
    fr - (C) 2012-18, Mike Miller
    License: GPLv3+.

    Output routines located here.
'''
import sys
import locale

from . import ansi


# defaults
_outunit = 1000000, 'Megabyte'  # 1 Megabyte default
opts, pform = None, None
dim_templ, swap_clr_templ = None, None
out = sys.stdout.write

if sys.platform[:3] == 'win':  # :-(
    def out(*args, end=''):
        print(*args, end=end)

# icons
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
    ''' Load options, platform, colors, and icons. '''
    global opts, pform
    opts = options
    pform = options.pform
    global_ns = globals()

    # get colors
    if pform.hicolor:
        global_ns['dim_templ'] = ansi.dim8t
        global_ns['swap_clr_templ'] = ansi.csi8_blk % ansi.blu8
    else:
        global_ns['dim_templ'] = ansi.dim4t
        global_ns['swap_clr_templ'] = ansi.fbblue

    # load icons into module namespace
    for varname in dir(pform):
        if varname.startswith('_') and varname.endswith('ico'):
            global_ns[varname] = getattr(pform, varname)



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
    try:
        result = locale.format_string(fmt, value, True)  #  >= Py 3.7
    except AttributeError:  # olden tymes
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
        print(f'Warning: incorrect parameter: {unit}.')
        result = _outunit

    if opts.precision == -1:  # auto
        opts.precision = 0
    return result


def print_diskinfo(diskinfo, widelayout, incolor):
    ''' Disk information output function. '''
    sep = ' '
    if opts.relative:
        import math
        base = max([ disk.ocap for disk in diskinfo ])

    for disk in diskinfo:
        if disk.ismntd:     ico = _diskico
        else:               ico = _unmnico
        if disk.isrem:      ico = _remvico
        if disk.isopt:      ico = _discico
        if disk.isnet:      ico = _netwico
        if disk.isram:      ico = _ramico
        if disk.isimg:      ico = _imgico
        if disk.mntp == '/boot/efi':
                            ico = _gearico

        if opts.relative and disk.ocap and disk.ocap != base:
            # increase log size reduction by raising to 4th power:
            gwidth = int((math.log(disk.ocap, base)**4) * opts.width)
        else:
            gwidth = opts.width

        # check color settings, ffg: free foreground, ufg: used forground
        if disk.rw:
            ffg = ufg = None        # auto colors
        else:
            # dim or dark grey
            ffg = ufg = (ansi.dim8 if opts.hicolor else ansi.dim4)

        cap = disk.cap
        if cap and disk.rw:
            lblcolor = ansi.get_label_tmpl(disk.pcnt, opts.width, opts.hicolor)
        else:
            lblcolor = None

        # print stats
        data = (
            (_usedico, disk.pcnt,     ufg,  None,  pform.boldbar),  # Used
            (_freeico, 100-disk.pcnt, ffg,  None,  False),          # free
        )
        mntp = fmtstr(disk.mntp, align='<', trunc='left',
                      width=(opts.colwidth * 2) + 2)
        mntp = mntp.rstrip()  # prevent wrap
        if disk.label is None:
            label = fmtstr(_emptico, dim_templ, align='<')
        else:
            label = fmtstr(disk.label, align='<')

        if widelayout:
            out(
                fmtstr(ico + sep + disk.dev, align='<') + label
            )
            if cap:
                out(fmtval(cap))
                if disk.rw:
                    out(
                        fmtval(disk.used, lblcolor) +
                        fmtval(disk.free, lblcolor)
                    )
                else:
                    out(
                        fmtstr() +
                        fmtstr(_emptico, dim_templ)
                    )
            else:
                out(fmtstr(_emptico, dim_templ))

            if cap:
                if disk.rw:  # factoring this caused colored brackets
                    ansi.rainbar(data, gwidth, incolor,
                                 hicolor=opts.hicolor,
                                 cbrackets=_brckico)
                else:
                    ansi.bargraph(data, gwidth, incolor, cbrackets=_brckico)

                if opts.relative and opts.width != gwidth:
                    out(sep * (opts.width - gwidth))
                out(sep + mntp)
            print()
        else:
            out(
                fmtstr(ico + sep + disk.dev, align="<") + label
            )
            if cap:
                out(
                    fmtval(cap) +
                    fmtval(disk.used, lblcolor) +
                    fmtval(disk.free, lblcolor)
                )
            else:
                out(fmtstr(_emptico, dim_templ) + fmtstr() + fmtstr())
            print(sep, mntp)

            if cap:
                out(fmtstr())
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
        swpf = swpc = swpu = swfp = swcp = swup = 0         # avoid /0 error
        slblcolor = None
    cacheico = _usedico if incolor else _cmonico

    # print RAM info
    data = (
        (_usedico, usep, None,  None, pform.boldbar),       # used
        (cacheico, cacp, ansi.blue,  None, pform.boldbar),  # cache
        (_freeico, frep, None,  None, False),               # free
    )
    if widelayout:
        out(
            fmtstr(_ramico + ' RAM', align='<') +
            fmtstr() +                                      # volume col
            fmtval(totl) +
            fmtval(used, rlblcolor) +
            fmtval(free, rlblcolor)
        )
        # print graph
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print('', fmtval(cach, swap_clr_templ))
    else:
        out(
            fmtstr(_ramico + ' RAM', align="<") +
            fmtstr() +                                      # volume col
            fmtval(totl) +
            fmtval(used, rlblcolor) +
            fmtval(free, rlblcolor) +
            sep + sep +
            fmtval(cach, swap_clr_templ) + '\n' +
            fmtstr()                                        # blank space
        )
        # print graph
        ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                     cbrackets=_brckico)
        print()                             # extra line in narrow layout

    # Swap time:
    data = (
        (_usedico, swup, None, None, pform.boldbar),        # used
        (_usedico, swcp, None, None, pform.boldbar),        # cache
        (_freeico, swfp, None, None, False),                # free
    )
    if widelayout:
        out(fmtstr(_diskico + ' SWAP', align='<') + fmtstr())   # label
        if swpt:
            out(
                fmtval(swpt) +
                fmtval(swpu, slblcolor) +
                fmtval(swpf, slblcolor)
            )
        else:
            print(fmtstr(_emptico, dim_templ))

        # print graph
        if swpt:
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            if swpc:
                out(' ' + fmtval(swpc, swap_clr_templ))
            print()
    else:
        out(fmtstr(_diskico + ' SWAP', align='<'))
        if swpt:
            out(
                fmtstr() +                                  # volume col
                fmtval(swpt) +
                fmtval(swpu, slblcolor) +
                fmtval(swpf, slblcolor)
            )
            if swpc:
                out('  ' + fmtval(swpc, swap_clr_templ))
            print()
            out(fmtstr())  # blank space

            # print graph
            ansi.rainbar(data, opts.width, incolor, hicolor=opts.hicolor,
                         cbrackets=_brckico)
            print()
        else:
            print(' ' + fmtstr(_emptico, dim_templ, align='<'))
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

    return f'{before}{truncated}{after}'
