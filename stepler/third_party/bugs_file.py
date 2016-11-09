"""
------------------------------------------
Pytest plugin to skip tests from bugs file
------------------------------------------

Note:

    Bugs file should be valid json file with format:

    .. code:: json

       {
           "<idempotent-id>": {
               "bug_url1": true,
               "bug_url2": false,
               "bug_url3": true
           },
       }

    Where ``true / false`` indicates that bug is ``resolved / not resolved``.
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


def pytest_addoption(parser):
    """Add option to pytest."""
    parser.addoption("--bugs-file", action="store",
                     help="Path to json file with bugs for tests.")


def pytest_collection_modifyitems(config, items):
    """Hook to skip test with opened bugs."""
    if config.option.bugs_file:
        with open(config.option.bugs_file) as f:
            bugs = json.load(f)

            for item in items:
                test_ids = [marker.args[0] for marker in
                            item.get_marker('idempotent_id') or []]

                test_bugs = set()
                for test_id in test_ids:
                    for bug_link, is_resolved in bugs.get(test_id, {}):
                        if not is_resolved:
                            test_bugs.add(bug_link)

                if test_bugs:
                    message = ('Skipped due to open bug(s): ' +
                               ', '.join(test_bugs))
                    item.add_marker(pytest.mark.skip(reason=message))
