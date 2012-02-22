#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
import os.path
try:
    import py2exe
except:
    py2exe=None

from libbe import _version, version

rev_id = _version.version_info["revision"]
rev_date = _version.version_info["date"]

data_files = []

man_path = os.path.join('doc', 'man', 'be.1')
if os.path.exists(man_path):
    data_files.append(('share/man/man1', [man_path]))

setup(
    name='Bugs Everywhere (BEurtle fork)',
	console=['be.py'],
    version=version.version()+" ("+rev_date+")",
    description='Bugtracker supporting distributed revision control',
    url='http://bugseverywhere.org/',
    packages=['libbe',
              'libbe.command',
              'libbe.storage',
              'libbe.storage.util',
              'libbe.storage.vcs',
              'libbe.ui',
              'libbe.ui.util',
              'libbe.util'],
    scripts=['be', 'be.bat'],
    data_files=data_files,
    install_requires=['pyyaml', 'jinja2', 'cherrypy'],
    )
