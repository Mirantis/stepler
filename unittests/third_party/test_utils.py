"""
---------------
Utils unittests
---------------
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

from hamcrest import (assert_that, contains)  # noqa H301
import pytest

from stepler.third_party import utils


@pytest.mark.parametrize(['iterable', 'chunk_size', 'expected'], (
    ('abc', 2, [['a', 'b'], ['c']]),
    ('abc', 3, [['a', 'b', 'c']]),
    ('abc', 5, [['a', 'b', 'c']]),
    (['a', 'b', 'c'], 2, [['a', 'b'], ['c']]),
    (('a', 'b', 'c'), 2, [['a', 'b'], ['c']]),
    ((x for x in ('a', 'b', 'c')), 2, [['a', 'b'], ['c']]), ))
def test_grouper(iterable, chunk_size, expected):
    """Verify correct grouping."""
    result = utils.grouper(iterable, chunk_size)
    assert_that(list(result), contains(*expected))
