'''
    Project metadata is specified here.

    This module *should not* import anything from the project or third-party
    modules, to avoid dependencies in setup.py or circular import issues.
'''
from time import localtime as _localtime


pkgname         = 'fr'
__version__     = version = '3.00a0'
__author__      = authors = ', '.join([
                                'Mike Miller',
                                #~ 'and contributors',
                            ])
copyright       = '© 2005-%s' % _localtime().tm_year
description     = 'A program to print available free resources in delicious flavors.'
email           = ''
license         = license = 'GPLv3'

# online repo information
repo_account    = 'mixmastamyk'
repo_name       = 'fr'
repo_provider   = 'github.com'
#~ repo_provider   = 'bitbucket.org'
repo_url        = 'https://%s/%s/%s' % (repo_provider, repo_account, repo_name)


#~ class defaults:
    #~ name        = 'foo'
