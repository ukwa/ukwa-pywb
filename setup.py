#!/usr/bin/env python
# vim: set sw=4 et:

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import glob

__version__ = '1.1'


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        # should work with setuptools <18, 18 18.5
        self.test_suite = ' '

    def run_tests(self):
        import pytest
        import sys
        import os
        errcode = pytest.main(['--cov', 'ukwa_pywb', '-vv', 'ukwa_pywb/test/'])
        sys.exit(errcode)

setup(
    name='ukwa_pywb',
    version=__version__,
    author='UKWA British Library',
    license='Apache 2.0',
    packages=find_packages(exclude=['test']),
    url='https://github.com/ukwa/ukwa-pywb',
    description='UK Web Archive pywb Deployment',
    long_description=open('README.md').read(),
    setup_requires=[
        'babel',
        ],
    install_requires=[
        'babel',
        'uwsgi',
        'fakeredis<1.0',
        'secure-cookie',
        'pywb'
    ],
    message_extractors = {
        '.': [
            ('templates/**.html', 'jinja2', {'extensions': 'jinja2.ext.autoescape,jinja2.ext.with_'})
        ],
    },
    zip_safe=True,
    entry_points="""
        [console_scripts]
        ukwa_pywb = ukwa_pywb.ukwa_app:main
    """,
    cmdclass={'test': PyTest},
    test_suite='',
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
