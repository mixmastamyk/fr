'''
    ansilib, a library of common console color functions.
    (C) 2005-18, Mike Miller - Released under the GPL, version 3+.

    This module is quite old and could be partially replaced with a package
    dependency containing ansi routines.
'''
import sys

out = sys.stdout.write
if sys.platform[:3] == 'win':  # don't bypass streams :-(
    def out(*args, end=''):
        print(*args, end=end)


if True:  # foldable init
    # 16 colors - fg
    black       = 30
    red         = 31
    green       = 32
    yellow      = 33
    orange      = 33
    blue        = 34
    purple      = 35
    cyan        = 36
    grey        = 37

    # bg
    blackbg     = 40
    redbg       = 41
    greenbg     = 42
    orangebg    = 43
    bluebg      = 44
    purplebg    = 45
    cyanbg      = 46
    greybg      = 47

    # attrs
    norm        = 0
    bold        = 1
    dim         = 2
    underline   = 4
    reverse     = 7
    strike      = 9
    dim4        = '%s;%s' % (bold, black)  # dark grey - works in more places

    csi4        = '\x1b[0;%sm'
    csi4b       = '\x1b[1;%sm'
    csi4_blk    = csi4b + '%%s\x1b[0m'
    yel         = yellow
    pal4        = [green, green, green, green, green, yel, yel, yel, yel, red]
    rst4        = green

    # A list of ansi escape sequences in template form.
    fbblue      = '\x1b[01;34m%s\x1b[00m'
    dim4t       = '\x1b[1;30m%s\x1b[0m'

    # A list of ansi escape sequences in template form.
    #~ fred        = '\x1b[00;31m%s\x1b[00m'
    #~ fbred       = '\x1b[01;31m%s\x1b[00m'
    #~ fgreen      = '\x1b[00;32m%s\x1b[00m'
    #~ fbgreen     = '\x1b[01;32m%s\x1b[00m'
    #~ forange     = '\x1b[00;33m%s\x1b[00m'
    #~ fbyellow    = '\x1b[01;33m%s\x1b[00m'
    #~ fblue       = '\x1b[00;34m%s\x1b[00m'
    #~ fpurple     = '\x1b[00;35m%s\x1b[00m'
    #~ fbpurple    = '\x1b[01;35m%s\x1b[00m'
    #~ fcyan       = '\x1b[00;36m%s\x1b[00m'
    #~ fbcyan      = '\x1b[01;36m%s\x1b[00m'
    #~ fgrey       = '\x1b[00;37m%s\x1b[00m'
    #~ fwhite      = '\x1b[01;37m%s\x1b[00m'
    # fgrey       = '\x1b[00;38m%s\x1b[00m'
    # fwhite      = '\x1b[01;38m%s\x1b[00m'

    #~ redrev      = '\x1b[00;05;37;41m%s\x1b[00m'
    #~ grerev      = '\x1b[00;05;37;42m%s\x1b[00m'
    #~ yelrev      = '\x1b[01;05;37;43m%s\x1b[00m'

    #~ rev         = '\x1b[07m%s\x1b[00m'
    #~ fbold       = '\x1b[01m%s\x1b[00m'
    #~ fdim        = '\x1b[02m%s\x1b[00m'

    # Readline encoded escape sequences:
    #~ greenprompt  = '\001\x1b[01;32m\002%s\001\x1b[00m\002'
    #~ yellowprompt = '\001\x1b[01;33m\002%s\001\x1b[00m\002'
    #~ redprompt    = '\001\x1b[01;31m\002%s\001\x1b[00m\002'

    # 256 color support
    csi8        = '\x1b[0;38;5;%03dm'
    csi8b       = '\x1b[1;38;5;%03dm'
    csi8_blk    = csi8b + '%%s\x1b[0m'
    blu8        = 27
    darkred     = 52
    grn8        = 34
    grnyl8      = 76
    orng8       = 172
    orngrd8     = 166
    red8        = 160
    yell8       = 184
    dim8        = '38;5;240'
    dim8t       = '\x1b[38;5;240m%s\x1b[0m'

    pal8 = [grn8, grn8, grn8, grn8, grn8, grnyl8, yell8, orng8, orngrd8, red8]
    map8 = {blue: blu8, red: red8, green: grn8, dim: dim}
    rst8 = grn8


def colorstart(fgcolor, bgcolor, weight):
    ''' Begin a text style. '''
    if weight:
        weight = bold
    else:
        weight = norm
    if bgcolor:
        out('\x1b[%s;%s;%sm' % (weight, fgcolor, bgcolor))
    else:
        out('\x1b[%s;%sm' % (weight, fgcolor))


def colorend(cr=False):
    ''' End color styles.  Resets to default terminal colors. '''
    if cr:
        out('\x1b[0m\n')
    else:
        out('\x1b[0m')


def cprint(text, fg=grey, bg=blackbg, w=norm, cr=False, encoding='utf8'):
    ''' Print a string in a specified color style and then return to normal.
        def cprint(text, fg=white, bg=blackbg, w=norm, cr=True):
    '''
    colorstart(fg, bg, w)
    out(text)
    colorend(cr)


def bargraph(data, maxwidth, incolor=True, cbrackets=('\u2595', '\u258F')):
    ''' Creates a monochrome or two-color bar graph. '''
    threshold = 100.0 // (maxwidth * 2)  # if smaller than 1/2 of one char wide
    position = 0
    begpcnt = data[0][1] * 100
    endpcnt = data[-1][1] * 100

    if len(data) < 1: return        # Nada to do
    maxwidth = maxwidth - 2         # because of brackets
    datalen = len(data)

    # Print left bracket in correct color:
    if cbrackets and incolor:       # and not (begpcnt == 0 and endpcnt == 0):
        if begpcnt < threshold: bkcolor = data[-1][2]  # greenbg
        else:                   bkcolor = data[0][2]   # redbg
        cprint(cbrackets[0], data[0][2], bkcolor, None, None)
    else:
        out(cbrackets[0])

    for i, part in enumerate(data):
        # unpack data
        char, pcnt, fgcolor, bgcolor, bold = part
        width = int(round(pcnt/100.0 * maxwidth, 0))
        position = position + width

        # and graph
        if incolor and not (fgcolor is None):
            cprint(char * width, fgcolor, bgcolor, bold, False)
        else:
            out((char * width))

        if i == (datalen - 1):   # correct last one
            if position < maxwidth:
                if incolor:     # char
                    cprint(char * (maxwidth-position), fgcolor, bgcolor,
                           bold, False)
                else:
                    out(char * (maxwidth-position))
            elif position > maxwidth:
                out(chr(8) + ' ' + chr(8))  # backspace

    # Print right bracket in correct color:
    if cbrackets and incolor:
        if endpcnt < threshold: bkcolor = data[0][3]    # redbg
        else:                   bkcolor = data[1][3]    # greenbg
        cprint(cbrackets[1], data[-1][2], bkcolor, None, None)
    else:
        out(cbrackets[1])


def get_palette(hicolor):
    if hicolor:
        return csi8, csi8b, csi8_blk, pal8, rst8, len(pal8)
    else:
        return csi4, csi4b, csi4_blk, pal4, rst4, len(pal4)


def get_label_tmpl(value, maxwidth, hicolor):
    csi, csib, blk, pal, rst, plen = get_palette(hicolor)
    # not happy with calculating this again...
    pos = int(maxwidth * (value / 100.0)) - 1
    colorind = get_color_index(pos, 0, maxwidth, plen)
    return blk % pal[colorind]


def get_color_index(pos, offset, maxwidth, plen):
    bucket = float(maxwidth) / plen
    return min(int((pos+offset)/bucket), (plen-1))


def rainbar(data, maxwidth, incolor=True, hicolor=True,
            cbrackets=('\u2595', '\u258F')):
    ''' Creates a "rainbar" style bar graph. '''
    if not data: return             # Nada to do
    datalen = len(data)
    endpcnt = data[-1][1]
    maxwidth = maxwidth - 2         # because of brackets

    # setup
    csi, csib, _, pal, rst, plen = get_palette(hicolor)

    empty = data[-1][0]
    bucket = float(maxwidth) / plen
    position = 0

    # Print left bracket in correct color:
    if incolor:
        out((csi % pal[0]) + cbrackets[0])  # start bracket
    else:
        out(cbrackets[0])

    for i, part in enumerate(data):
        char, pcnt, fgcolor, bgcolor, bold = part
        if fgcolor and hicolor:
            fgcolor = map8[fgcolor]
        if not bold:
            csib = csi

        lastind = None
        width = int(maxwidth * (pcnt / 100.0))
        offset = position
        position += width

        if incolor:
            for j in range(width):
                # faster?
                colorind = fgcolor or min(int((j+offset)/bucket), (plen-1))
                #~ colorind=fgcolor or get_color_index(j, offset,maxwidth,plen)
                if colorind == lastind:
                    out(char)
                else:
                    color = fgcolor or pal[colorind]
                    out((csib % color) + char)
                lastind = colorind
        else:
            out((char * width))

        if i == (datalen - 1):          # check if last one correct
            if position < maxwidth:
                rest = maxwidth - position
                if incolor:
                    out((csib % pal[-1]) + (empty * rest))
                else:
                    out(char * rest)
            elif position > maxwidth:
                out(chr(8) + ' ' + chr(8))  # backspace

    # Print right bracket in correct color:
    if incolor:
        lastcolor = darkred if (hicolor and endpcnt > 1) else pal[-1]
        out((csi % lastcolor) + cbrackets[1])    # end bracket
        colorend()
    else:
        out(cbrackets[1])
