#!/usr/bin/env python
import os
from distutils.core import setup

#~ # grab metadata
#~ version = '1.00'
#~ with open('fr/fr') as f:
    #~ for line in f:
        #~ if line.lstrip().startswith('__version__'):
            #~ try:
                #~ version = line.split("'")[1]
            #~ except IndexError:  pass
            #~ break
from fr.meta import (pkgname, version, email, license, authors, description,
                     repo_url)

# readme is needed at upload time, not install time
try:
    with open('readme.rst', encoding='utf8') as f:
        long_description = f.read()
except IOError:
    long_description = ''

# install helper script?
scripts = [pkgname + '/' + pkgname]
if os.name == 'nt':
    scripts.append('fr.cmd')


setup(
    name          = pkgname,
    version       = version,
    description   = description,
    author        = authors,
    author_email  = email,
    url           = repo_url,
    download_url  = '',
    license       = license,
    packages      = [pkgname],
    scripts       = scripts,
    extras_require = {
        'win': ['winstats', 'colorama'],
    },
    python_requires='>3.6.0',

    long_description = long_description,
    classifiers     = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
