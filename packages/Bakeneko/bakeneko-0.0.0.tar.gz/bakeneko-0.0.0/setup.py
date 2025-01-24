#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup, find_packages


setup(
    name = 'Bakeneko',
    author = 'Aki \'lethalbit\' Van Ness',
    author_email = 'nya@catgirl.link',
    license = 'BSD-3-Clause',
    zip_safe = True,

    setup_requires = [
        'wheel',
        'setuptools',
        'setuptools_scm'
    ],
    
    packages = find_packages(
        where = '.',
        exclude = (
            'tests', 'tests.*', 'examples', 'examples.*'
        )
    ),
)

