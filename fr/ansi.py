'''
    ansilib, a library of common console color functions.
    (C) 2005-12, Mike Miller - Released under the GPL, version 3+.
'''
import sys, os

if True:  # fold init
    # fg
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
    dimbb       = '%s;%s' % (bold, black) # works in more places


    # A list of ansi escape sequences.
    fred        = '[00;31m%s[00m'
    fbred       = '[01;31m%s[00m'
    fgreen      = '[00;32m%s[00m'
    fbgreen     = '[01;32m%s[00m'
    forange     = '[00;33m%s[00m'
    fbyellow    = '[01;33m%s[00m'
    fblue       = '[00;34m%s[00m'
    fbblue      = '[01;34m%s[00m'
    fpurple     = '[00;35m%s[00m'
    fbpurple    = '[01;35m%s[00m'
    fcyan       = '[00;36m%s[00m'
    fbcyan      = '[01;36m%s[00m'
    fgrey       = '[00;37m%s[00m'
    fwhite      = '[01;37m%s[00m'
    #fgrey       = '[00;38m%s[00m'
    #fwhite      = '[01;38m%s[00m'

    redrev      = '[00;05;37;41m%s[00m'
    grerev      = '[00;05;37;42m%s[00m'
    yelrev      = '[01;05;37;43m%s[00m'

    rev         = '[07m%s[00m'
    fbold       = '[01m%s[00m'
    fdim        = '[02m%s[00m'
    fdimbb      = '[1;30m%s[0m'

    # Readline encoded escape sequences:
    greenprompt  = '\001[01;32m\002%s\001[00m\002'
    yellowprompt = '\001[01;33m\002%s\001[00m\002'
    redprompt    = '\001[01;31m\002%s\001[00m\002'

    # 256...
    darkred = 52

    # 256 color support
    csi8 = '\x1b[0;38;5;%03dm'
    csi8b = '\x1b[1;38;5;%03dm'
    csi8_blk = csi8b + '%%s\x1b[0m'
    grn8 = 34
    grnyl8 = 76
    yell8 = 184
    orng8 = 172
    orngrd8 = 166
    red8 = 160
    blu8 = 27
    pal8 = [grn8, grn8, grn8, grn8, grn8, grnyl8, yell8, orng8, orngrd8, red8]
    map8 = { blue: blu8, red: red8, green: grn8, dim: dim }
    rst8 = grn8

    # 16 colors
    csi4 = '\x1b[0;%sm'
    csi4b = '\x1b[1;%sm'
    csi4_blk = csi4b + '%%s\x1b[0m'
    yel = yellow
    pal4 = [green, green, green, green, green, yel, yel, yel, yel, red]
    rst4 = green


def colorstart(fgcolor, bgcolor, weight):
    '''Begin a text style.'''
    if weight:          weight = bold
    else:               weight = norm
    if bgcolor:
        sys.stdout.write('[%s;%s;%sm' % (weight, fgcolor, bgcolor))
    else:
        sys.stdout.write('[%s;%sm' % (weight, fgcolor))


def colorend(cr=False):
    '''End color styles.  Resets to default terminal colors.'''
    sys.stdout.write('[0m')
    if cr: sys.stdout.write('\n')
    sys.stdout.flush()


def cprint(text, fg=grey, bg=blackbg, w=norm, cr=False, encoding='utf8'):
    ''' Print a string in a specified color style and then return to normal.
        def cprint(text, fg=white, bg=blackbg, w=norm, cr=True):
    '''
    colorstart(fg, bg, w)
    sys.stdout.write(text)
    colorend(cr)


def bargraph(data, maxwidth, incolor=True, cbrackets=(u'\u2595', u'\u258F')):
    'Creates a bar graph.'
    threshold = 100.0 / (maxwidth * 2)  # if smaller than 1/2 of one char wide
    position = 0
    begpcnt = data[0][1] * 100
    endpcnt = data[-1][1] * 100

    if len(data) < 1: return        # Nada to do
    maxwidth = maxwidth - 2         # because of brackets
    datalen = len(data)

    # Print left bracket in correct color:
    if cbrackets and incolor: # and not (begpcnt == 0 and endpcnt == 0):
        if begpcnt < threshold: bkcolor = data[-1][2]  # greenbg
        else:                   bkcolor = data[0][2]   # redbg
        cprint(cbrackets[0], data[0][2], bkcolor, None, None)
    else:
        sys.stdout.write(cbrackets[0])

    for i, part in enumerate(data):
        # unpack data
        char, pcnt, fgcolor, bgcolor, bold = part
        width = int( round(pcnt/100.0 * maxwidth, 0) )
        position = position + width

        # and graph
        if incolor and not ( fgcolor is None):
            cprint(char * width, fgcolor, bgcolor, bold, False)
        else:
            sys.stdout.write((char * width))

        if i == (datalen - 1):   # correct last one
            if position < maxwidth:
                if incolor: # char
                    cprint(char * (maxwidth-position), fgcolor, bgcolor,
                           bold, False)
                else:
                    sys.stdout.write(char * (maxwidth-position))
            elif position > maxwidth:
                sys.stdout.write(chr(8) + ' ' + chr(8))  # backspace

    # Print right bracket in correct color:
    if cbrackets and incolor:
        if endpcnt < threshold: bkcolor = data[0][3] # redbg
        else:                   bkcolor = data[1][3] # greenbg
        cprint(cbrackets[1], data[-1][2], bkcolor, None, None)
    else:
        sys.stdout.write(cbrackets[1])


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
            cbrackets=(u'\u2595', u'\u258F')):
    'Creates a "rainbar" graph.'
    if not data: return             # Nada to do
    datalen = len(data)
    endpcnt = data[-1][1] # * 100
    maxwidth = maxwidth - 2         # because of brackets

    # setup
    out = sys.stdout
    csi, csib, _, pal, rst, plen = get_palette(hicolor)

    empty = data[-1][0]
    bucket = float(maxwidth) / plen
    position = 0

    # Print left bracket in correct color:
    if cbrackets and incolor:
        out.write((csi % pal[0]) + cbrackets[0])  # start bracket
    else:
        out.write(cbrackets[0])

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
                # faster:
                colorind = fgcolor or min(int((j+offset)/bucket), (plen-1))
                #~ colorind = fgcolor or get_color_index(j, offset, maxwidth, plen)
                if colorind == lastind:
                    out.write(char)
                else:
                    color = fgcolor or pal[colorind]
                    out.write((csib % color) + char)
                lastind = colorind
        else:
            out.write((char * width))

        if i == (datalen - 1):          # check if last one correct
            if position < maxwidth:
                rest = maxwidth - position
                if incolor: # char
                    out.write((csib % pal[-1]) + (empty * rest))
                else:
                    out.write(char * rest)
            elif position > maxwidth:
                out.write(chr(8) + ' ' + chr(8))  # backspace

    # Print right bracket in correct color:
    if cbrackets and incolor:
        lastcolor = darkred if (hicolor and endpcnt > 1) else pal[-1]
        out.write((csi % lastcolor) + cbrackets[1])    # end bracket
        colorend()
    else:
        out.write(cbrackets[1])


# -------------------------------------------------------------------
# modified from gentoo portage "output" module
# Copyright 1998-2004 Gentoo Foundation
def set_xterm_title(mystr):
    'set the title of an xterm'
    if os.environ.has_key('TERM') and sys.stderr.isatty():
        terms = ['xterm', 'Eterm', 'aterm', 'rxvt', 'screen', 'kterm',
                 'rxvt-unicode']
        term = os.environ['TERM']
        if term in terms:
            sys.stderr.write('\x1b]2;'+str(mystr)+'\x07')
            sys.stderr.flush()

# -------------------------------------------------------------------
# from avkutil.py - Andrei Kulakov <ak@silmarill.org>
def get_term_size():
    '''Return terminal size as tuple (width, height).'''
    x, y = 0, 0
    if sys.platform.startswith('win'):
        #~ http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
        res = None
        try:
            from ctypes import windll, create_string_buffer
            stderr = -12
            h = windll.kernel32.GetStdHandle(stderr)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        except Exception as err:
            print 'ERROR:', err.__class__.__name__, str(err)
        if res:
            import struct
            (bufx, bufy, curx, cury, wattr, left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            x = right - left + 1
            y = bottom - top + 1
    else:  # Mac, Linux
        import struct, fcntl, termios
        try:
            y, x = struct.unpack('hhhh', fcntl.ioctl(0,
                termios.TIOCGWINSZ, '\000'*8))[0:2]
        except IOError:
            pass
    return x, y

