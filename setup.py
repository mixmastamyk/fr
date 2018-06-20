#!/usr/bin/env python
import os
from os.path import join
from setuptools import setup
from fr.meta import (pkgname, version, email, license, authors, description,
                     repo_url, trove_classifiers)

# readme is needed at upload time, not install time
try:
    with open('readme.rst', encoding='utf8') as f:
        long_description = f.read()
except IOError:
    long_description = ''


# install helper script?
scripts = [join(pkgname, pkgname)]
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
    classifiers   = trove_classifiers,
)
