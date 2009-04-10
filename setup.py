#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
from beautifulsoup import __version__

setup(
    name='beautifulsoup',
    version=__version__,
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='Leonard Richardson',
    maintainer_email='leonardr@segfault.org',
    long_description="""Beautiful Soup parses arbitrarily invalid XML/HTML and provides a variety of methods and Pythonic idioms for iterating and searching the parse tree.""",
    license='New-style BSD',
    install_requires=[
        'setuptools',
        'zope.interface',
        ],
    url='https://launchpad.net/beautifulsoup',
    download_url= 'https://launchpad.net/beautifulsoup/+download',
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Python Software Foundation License",
                 "Programming Language :: Python",
                 "Topic :: Text Processing :: Markup :: HTML",
                 "Topic :: Text Processing :: Markup :: XML",
                 "Topic :: Text Processing :: Markup :: SGML",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    extras_require=dict(
        docs=['Sphinx',
              'z3c.recipe.sphinxdoc']
    ),
    setup_requires=['eggtestinfo', 'setuptools_bzr'],
    test_suite='beautifulsoup.tests',
    )
