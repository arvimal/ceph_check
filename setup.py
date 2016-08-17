# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ceph_check'
    'author': 'Vimal A.R',
    'url': 'https://github.com/arvimal/ceph_check'
    'author_email': 'arvimal@yahoo.in'
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['ceph_check'],
    'scripts': [],
    'name': 'ceph_check'
}

setup(**config)
