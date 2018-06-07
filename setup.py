#!/usr/bin/env python
import os
from distutils.core import setup

# grab metadata
version = '1.00'
with open('fr/fr') as f:
    for line in f:
        if line.lstrip().startswith('__version__'):
            try:
                version = line.split("'")[1]
            except IndexError:  pass
            break

# readme is needed at upload time, not install time
try:
    with open('readme.rst') as f:                  # no unicode for older vers.
        long_description = f.read().decode('utf8') #.encode('ascii', 'replace')
except IOError:
    long_description = ''

# install helper script?
scripts = ['fr/fr']
if os.name == 'nt':
    scripts.append('fr.cmd')


setup(
    name          = 'fr',
    version       = version,
    description   = 'A command-line tool to print free resources in' +
                    ' delicious flavors.',
    author        = 'Mike Miller',
    author_email  = 'mixmastamyk@bitbucket.org',
    url           = 'https://bitbucket.org/mixmastamyk/fr',
    download_url  = 'https://bitbucket.org/mixmastamyk/fr/get/default.tar.gz',
    license       = 'GPLv3',
    packages      = ['fr'],
    scripts       = scripts,
    extras_require = {
        'win': ['winstats'],
        'color': ['colorama'],
    },

    long_description = long_description,
    classifiers     = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
