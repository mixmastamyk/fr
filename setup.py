#!/usr/bin/env python
import os
from os.path import join
from setuptools import setup
from fr.meta import (pkgname, version, email, license, authors, description,
                     repo_url, trove_classifiers)

# readme is needed at upload time, not install time
try:
    with open('readme.rst', encoding='utf8') as f:
        long_desc = f.read()
except IOError:
    long_desc = ''


# install helper script for windows?
extras_require    = {}
scripts = [join(pkgname, pkgname)]
if os.name == 'nt':
    scripts.append('fr.cmd')
    extras_require['win'] = ['winstats', 'colorama']


setup(
    name              = pkgname,
    version           = version,
    description       = description,
    author            = authors,
    author_email      = email,
    url               = repo_url,
    download_url      = '',
    license           = license,
    packages          = [pkgname],
    scripts           = scripts,
    python_requires   = '>3.6.0',
    extras_require    = extras_require,

    long_description  = long_desc,
    classifiers       = trove_classifiers,
)
