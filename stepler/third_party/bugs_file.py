"""
------------------------------------------
Pytest plugin to skip tests with bugs file
------------------------------------------

Note:

    Bugs file should be valid json file with format:

    .. code:: json

       {
           <idempotent-id>: {
               <bug_url_1>: true,
               <bug_url_2>: false,
               <bug_url_3>: true
           }
       }

    Where ``true / false`` indicates that bug is ``opened / closed``.
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

import json

import pytest

__all__ = [
    'pytest_addoption',
    'pytest_collection_modifyitems',
]


def pytest_addoption(parser):
    """Add ``--bugs-file`` option to pytest."""
    parser.addoption("--bugs-file", action="store",
                     help="Path to json file with bugs of tests.")


def pytest_collection_modifyitems(config, items):
    """Hook to skip tests with opened bugs."""
    if not config.option.bugs_file:
        return

    with open(config.option.bugs_file) as f:
        bugs = json.load(f)

    for item in items:
        test_ids = [marker.args[0] for marker in
                    item.get_marker('idempotent_id') or []]

        test_bugs = _get_test_bugs(bugs, test_ids)

        if test_bugs:
            message = 'Skipped due to opened bug(s): ' + ', '.join(test_bugs)
            item.add_marker(pytest.mark.skip(reason=message))


def _get_test_bugs(bugs, test_ids):
    test_bugs = set()
    for test_id in test_ids:
        for bug_link, is_opened in bugs.get(test_id, {}).items():
            if is_opened:
                test_bugs.add(bug_link)
    return test_bugs
