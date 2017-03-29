#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
from setuptools import setup, find_packages

import sys
if sys.version_info[0] == 2:
    from io import open

here = os.path.abspath(os.path.dirname(__file__))

__version__ = None
__license__ = None
__author__ = None
exec(open('fdeunlock/_meta.py', 'r', encoding='utf-8').read())
author = re.search(r'^(?P<name>[^<]+) <(?P<email>.*)>$', __author__)

# https://packaging.python.org/
setup(
    name='fdeunlock',
    version=__version__,
    description='Check and unlock full disk encrypted systems via ssh',
    long_description=open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8').read(),
    url='https://gitlab.com/ypid/fdeunlock',
    author=author.group('name'),
    author_email=author.group('email'),
    # Basically redundant but when not specified `./setup.py --maintainer` will
    # return "UNKNOWN".
    maintainer=author.group('name'),
    maintainer_email=author.group('email'),
    license=__license__,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security :: Cryptography',
        'Topic :: System :: Boot :: Init',
        'Topic :: System :: Systems Administration',
    ),
    keywords='remote boot fde headless encryption security checksum initramfs ssh cryptsetup',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'paramiko',
        'pexpect',
        'appdirs',
        'hexdump',
    ],
    extras_require={
        'test': [
            'nose',
            'nose2',
            'testfixtures',
            'tox',
            'flake8',
            'pylint',
            'coverage',
            'yamllint',
        ],
        #  'docs': [],  # See docs/requirements.txt
    },
    entry_points={
        'console_scripts': [
            'fdeunlock = fdeunlock.cli:main',
        ],
    },
)
