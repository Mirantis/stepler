"""
Pytest plugin to add mark `@pytest.mark.testrail_id(<id>)`.

@author: schipiga@mirantis.com
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from collections import defaultdict
import unittest

import pytest


# TODO(schipiga): This plugin should be refactored
def pytest_addoption(parser):
    """Add option to pytest."""
    parser.addoption("--check-testrail-id", action="store_true",
                     help="Check that all tests has uniq testrail_id marker")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    """Add marker to test name, if test marked with `testrail_id` marker.

    If optional kwargs passed - test parameters should be a
    superset of this kwargs to mark be applied.
    Also kwargs can be passed as `params` argument.
    """
    ids = defaultdict(list)
    for item in items:
        markers = item.get_marker('testrail_id') or []
        suffix_string = ''
        for marker in markers:
            test_id = marker.args[0]
            params = marker.kwargs.get('params', marker.kwargs)
            if len(params) > 0:
                if not hasattr(item, 'callspec'):
                    raise Exception("testrail_id decorator with filter "
                                    "parameters requires parametrizing "
                                    "of test method")
                params_in_callspec = all(param in item.callspec.params.items()
                                         for param in params.items())
                if not params_in_callspec:
                    continue
            suffix_string = '[({})]'.format(test_id)
            ids[test_id].append(item)
            break
        else:
            ids[None].append(item)
        item.name += suffix_string
        if item.cls is not None and issubclass(item.cls, unittest.TestCase):
            setattr(item.cls, item.name, item.function)

    if config.getoption("--check-testrail-id"):
        errors = []
        witout_id = ids.pop(None, [])
        if witout_id:
            errors += ["Tests witout testrail_id:"]
            errors += ['  ' + x.nodeid for x in witout_id]
        for test_id, items in ids.items():
            if len(items) > 1:
                errors += ["Single testrail_id for many cases:"]
                errors += ['  ' + x.nodeid for x in items]
        if errors:
            print('')
            print('\n'.join(errors))
            pytest.exit('Errors with testrail_id')


def pytest_runtestloop(session):
    """Check testrail id."""
    if session.config.option.check_testrail_id:
        return True
