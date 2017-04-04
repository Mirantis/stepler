"""
----------------
Waiter unittests
----------------
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

import logging

from hamcrest import (assert_that, calling, raises, is_,
                      string_contains_in_order)  # noqa H301
import pytest

from stepler.third_party import waiter

lambda_predicate = lambda: False


def simple_predicate():
    return False


def expect_predicate():
    return waiter.expect_that(1, is_(2))


def test_trusty_predicate():
    """Verify correct working with trusty predicate."""
    result = waiter.wait(lambda: True, timeout_seconds=0)
    assert_that(result, is_(True))


@pytest.mark.parametrize(
    'predicate, message',
    [(lambda_predicate, 'No exception raised during predicate executing'),
     (simple_predicate, 'No exception raised during predicate executing'),
     (expect_predicate, r'Expected: <2>\s+but: was <1>')])
def test_waiter_raises_timeout_expired(predicate, message):
    """Check that falsy predicates exception and message."""
    assert_that(
        calling(waiter.wait).with_args(
            predicate, timeout_seconds=0),
        raises(waiter.TimeoutExpired, message))


def test_pass_args_to_predicate():
    """Test passing args to predicate."""

    def predicate(foo, bar=None):
        return waiter.expect_that(foo, is_(bar))

    assert_that(
        calling(waiter.wait).with_args(
            predicate, timeout_seconds=0, args=[1], kwargs={'bar': 2}),
        raises(waiter.TimeoutExpired, r'Expected: <2>\s+but: was <1>'))


def test_log_wait_calls(caplog):
    """Check that logs contains waiting start and end records"""
    with caplog.at_level(logging.DEBUG):
        waiter.wait(
            lambda: True,
            timeout_seconds=0,
            waiting_for="expected_predicate to be True")
    assert_that(caplog.text,
                string_contains_in_order(
                    "Function 'wait' starts",
                    "'waiting_for': 'expected_predicate to be True'",
                    "Function 'wait' ended", ))


@pytest.mark.parametrize(
    'expected_exceptions',
    [AttributeError,
     (AttributeError, ValueError)])
def test_expected_exceptions(expected_exceptions):
    """"Check expected_exceptions arg"""

    def predicate():
        raise AttributeError("AttributeError was thrown.")

    assert_that(
        calling(waiter.wait).with_args(
            predicate,
            timeout_seconds=0,
            expected_exceptions=expected_exceptions),
        raises(waiter.TimeoutExpired,
               'AttributeError: AttributeError was thrown.'))


def test_not_in_expected_exceptions():
    """Check that exception is thrown if it is not in expected_exception"""

    def predicate():
        raise AttributeError("AttributeError was thrown.")

    assert_that(
        calling(waiter.wait).with_args(
            predicate,
            timeout_seconds=0,
            expected_exceptions=ValueError),
        raises(AttributeError, 'AttributeError was thrown.'))
