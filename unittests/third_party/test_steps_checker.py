"""
-----------------------
Steps checked unittests
-----------------------
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

from hamcrest import assert_that, contains, empty, is_not  # noqa: H301
import pytest

from stepler.third_party import steps_checker


def func_block():
    """Doctring."""
    # Comment
    foo = 1
    # checker: disable
    bar = foo
    # checker: enable
    return bar


def func_block2():
    """Doctring."""
    # Comment
    foo = 1
    # checker: disable
    bar = foo
    return bar


def func_block3():
    """Doctring."""
    # Comment
    foo = 1
    # checker: enable
    bar = foo
    return bar


def func_inline1():
    foo = 1  # checker: disable
    return foo


def func_inline2():
    foo = \
        1  # checker: disable
    return foo


def func_inline3():
    dict.fromkeys(
        []
    )  # checker: disable
    return


@pytest.mark.parametrize(['func', 'matcher'], [
    (func_block, contains([5, 7])),
    (func_block2, empty()),
    (func_block3, empty()),
    (func_inline1, contains([2, 2])),
    (func_inline2, contains([2, 3])),
    (func_inline3, contains([2, 4])),
])
def test_exclude_lines(func, matcher):
    validator = steps_checker.FuncValidator(func)
    result = validator._get_excluded_lines()
    assert_that(result, matcher)


def test_tokenize():
    validator = steps_checker.FuncValidator(func_block)
    tokens = validator._get_tokens()
    assert_that(tokens, is_not(empty()))
