'''
    Project metadata is specified here.

    This module *should not* import anything from the project or third-party
    modules, to avoid dependencies in setup.py or circular import issues.
'''
from time import localtime as _localtime


pkgname         = 'fr'
__version__     = version = '3.01'
__author__      = authors = ', '.join([
                                'Mike Miller',
                                #~ 'and contributors',
                            ])
copyright       = '© 2005-%s' % _localtime().tm_year
description     = 'A program to print resources in delicious flavors.'
email           = ''
license         = license = 'GPLv3'

# online repo information
repo_account    = 'mixmastamyk'
repo_name       = 'fr'
repo_provider   = 'github.com'
repo_url        = 'https://%s/%s/%s' % (repo_provider, repo_account, repo_name)
trove_classifiers = [
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
]

#~ class defaults:
    #~ name        = 'foo'
