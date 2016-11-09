"""
-------------------
Bugs file unittests
-------------------
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

from collections import namedtuple

import pytest

from stepler.third_party import bugs_file

BUGS = {
    1: {'url1': True, 'url2': False},
    2: {'url3': False, 'url4': True},
    3: {'url2': True, 'url3': True}
}

Case = namedtuple('Case', ('test_ids', 'test_bugs'))

cases = [
    Case(test_ids=[1], test_bugs={'url1'}),
    Case(test_ids=[2], test_bugs={'url4'}),
    Case(test_ids=[0], test_bugs=set()),
    Case(test_ids=[1, 2, 3], test_bugs={'url1', 'url2', 'url3', 'url4'}),
]


@pytest.mark.parametrize('case', cases)
def test_bugs_separated_correct(case):
    """Verify that bugs are separated correctly."""
    assert bugs_file._get_test_bugs(BUGS, case.test_ids) == case.test_bugs
