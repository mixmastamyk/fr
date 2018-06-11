from __future__ import print_function
#~ import subprocess


class Info(dict):
    ''' Dict that acts like an object. '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class DiskInfo(Info):
    ''' Grouping of information related to a filesystem. '''
    def __init__(self, **kwargs):

        self.dev     = None      # short device name
        self.fmt     = None      # fs formate
        self.isimg   = None      # is a disk image
        self.ismntd  = None      # is mounted
        self.isnet   = None      # network drive
        self.isopt   = None      # optical drive
        self.isram   = None      # ram disk
        self.isrem   = None      # removable
        self.label   = None      # fs, not partition label
        self.mntp    = None      # mount point
        self.rw      = None      # writable

        self.cap     = None      # capacity, converted to out unit
        self.free    = None      # free space
        self.ocap    = None      # orig capacity #
        self.oused   = None      # orig used #
        self.pcnt    = None      # percentage used
        self.used    = None      # used, converted to out unit

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])


class MemInfo(Info):
    ''' System memory information. '''
    def __init__(self, **kwargs):

        self.buffers    = None
        self.cached     = None
        self.memfree    = None
        self.memtotal   = None
        self.swapcached = None
        self.swapfree   = None
        self.swaptotal  = None
        self.swapused   = None
        self.used       = None

