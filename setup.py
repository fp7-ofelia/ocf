#!/usr/bin/env python
'''Setup file to create an Expedient package.

Created on Aug 23, 2010

@author: jnaous
'''
import sys, glob, os
sys.path.append("src/python")

from setuptools import setup, find_packages
from setuptools.command.test import test

def get_files(path, *extensions):
    """Recursively get all files"""
    found = []
    
    for dirpath, dirnames, filenames in os.walk(path):
        def get_path(f):
            if extensions:
                matches = False
                for ext in extensions:
                    if f.endswith(ext):
                        matches = True
                if not matches:
                    return
            return os.path.join(dirpath, f)
        found.extend(filter(None, map(get_path, filenames)))
    return found

def strip_src(f):
    if f and f.startswith("src/"):
        return f[4:]

DATA_DIRS = [
    ("src/config", "share/expedient"),
    ("src/doc", "share/expedient"),
    ("src/static", "share/expedient"),
    ("src/templates", "share/expedient"),
    ("src/wsgi", "share/expedient"),
]

EXTENSIONS = [".html", ".js", ".css", ".wsgi", ".rst", ".png", ".jpg",
             ".htm", ".pxm", ".conf", ".txt", ".xml"]


def get_data_files():
    data_files = []
    # get all the non-python files
    for d in DATA_DIRS:
        found = get_files(d[0], *EXTENSIONS)
        for f in found:
            data_files.append((
                os.path.join(
                    d[1],
                    os.path.dirname(strip_src(f))
                ),
                [f],
            ))
            
    return data_files

def run_tests(*args):
    import subprocess, shlex
    subprocess.call(shlex.split(
        "python src/python/expedient/clearinghouse/manage.py test_expedient"
    ))

test.run_tests = run_tests

setup(
    name="expedient",
    version="0.2.5",
    description="Modular pluggable platform to manage GENI",
    author="Jad Naous",
    author_email="jnaous@stanford.edu",
    url="http://yuba.stanford.edu/~jnaous/expedient/",
    packages=find_packages("src/python"),
    package_dir={"": "src/python"},
    install_requires=[
        'django>=1.2.0,<1.3',
        'django_extensions',
        'django_evolution',
        'django-autoslug',
        'django-registration>=0.7,<0.8',
        'decorator',
        'M2Crypto',
        'PIL',
        'python-dateutil',
        'pycrypto',
        'paramiko',
        'django-renderform',
        'webob',
        'pyOpenSSL',
        'MySQL-python>=1.2.1p2',
        'pyquery',
    ],
    extras_require={
        "docs": ["Sphinx", "pygments", "epydoc"],
    },
    include_package_data=True,
    data_files=get_data_files(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "expedient_manage = expedient.clearinghouse.manage:main",
            "expedient_bootstrap_localsettings = expedient.clearinghouse.commands.utils:bootstrap_local_settings",
            "expedient_bootstrap_mysql = expedient.clearinghouse.commands.utils:bootstrap_expedient_mysql",
        ],
    },
)
