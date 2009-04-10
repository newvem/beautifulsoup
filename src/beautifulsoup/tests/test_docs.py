# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of beautifulsoup
#
# beautifulsoup is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# beautifulsoup is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with beautifulsoup.  If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

# pylint: disable-msg=E0611,W0142

__metaclass__ = type
__all__ = [
    'additional_tests',
    ]

import atexit
import doctest
import os
from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)
import unittest

DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def additional_tests():
    "Run the doc tests (README.txt and docs/*, if any exist)"
    doctest_files = [
        os.path.abspath(resource_filename('beautifulsoup', 'README.txt'))]
    if resource_exists('beautifulsoup', 'docs'):
        for name in resource_listdir('beautifulsoup', 'docs'):
            if name.endswith('.txt'):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename('beautifulsoup', 'docs/%s' % name)))
    kwargs = dict(module_relative=False, optionflags=DOCTEST_FLAGS)
    atexit.register(cleanup_resources)
    return unittest.TestSuite((
        doctest.DocFileSuite(*doctest_files, **kwargs)))
