"""
------------------------------------
Retrieve fixture by name inside test
------------------------------------
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

import pytest

__all__ = [
    'F',
]


@pytest.fixture
def F(request):
    """Function fixture to retrieve a fixture by name inside a test.

    It may be useful for tests parametrized with fixture's names:

    .. code:: python

        @pytest.fixture
        def fix1():
            def _():
                pass
            return _

        @pytest.fixture
        def fix2():
            def _():
                pass
            return _

        @pytest.mark.parametrize('action', ['fix1', 'fix2'])
        def test(F, action):
            F(action)()

    Args:
        request (obj): pytest request

    Returns:
        _F: fixture retriever
    """
    return _F(request.getfixturevalue)


class _F(object):

    def __init__(self, get_fixture):
        self._get_fixture = get_fixture

    def __call__(self, fixture_name):
        return self._get_fixture(fixture_name)
