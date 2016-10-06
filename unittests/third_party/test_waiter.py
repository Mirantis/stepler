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

import functools
import timeit

import pytest

from stepler.third_party import waiter


def test_waiter_works_immediately_if_predicate_result_true():
    """Verify that waiter gets result immediately if predicate returns true."""
    def predicate():
        return (True, None)

    result_time = timeit.timeit(
        lambda: waiter.wait(predicate, timeout=5), number=1)

    assert result_time < 1


def test_waiter_works_immediatelly_if_no_timeout():
    """Verify that waiter gets result immediately if not timeout."""
    def predicate():
        return (False, 'error')

    def wait():
        try:
            waiter.wait(predicate)
        except waiter.TimeoutError:
            pass

    result_time = timeit.timeit(wait, number=1)

    assert result_time < 1


def test_waiter_works_during_timeout_if_predicate_result_false():
    """Verify that waiter gets result nearby timeout."""
    timeout = 2

    def predicate():
        return (False, 'error')

    def wait():
        try:
            waiter.wait(predicate, timeout=timeout)
        except waiter.TimeoutError:
            pass

    result_time = timeit.timeit(wait, number=1)

    assert result_time > timeout - 1 and result_time < timeout


def test_waiter_big_rate_doesnot_overflow_timeout():
    """Verify that waiter gets result nearby timeout if rate is big."""
    timeout = 1

    def predicate():
        return (False, 'error')

    def wait():
        try:
            waiter.wait(predicate, timeout=timeout, rate=100)
        except waiter.TimeoutError:
            pass

    result_time = timeit.timeit(wait, number=1)

    assert result_time > timeout - 1 and result_time < timeout


def test_waiter_big_polling_time_doesnot_overflow_timeout():
    """Verify that waiter gets result nearby timeout if polling time is big."""
    timeout = 1

    def predicate():
        return (False, 'error')

    def wait():
        try:
            waiter.wait(predicate, timeout=timeout, polling_time=100)
        except waiter.TimeoutError:
            pass

    result_time = timeit.timeit(wait, number=1)

    assert result_time > timeout - 1 and result_time < timeout


def test_waiter_supports_skipped_exceptions():
    """Verify that waiter supports skipped exceptions."""
    def predicate():
        raise TypeError('error')

    with pytest.raises(waiter.TimeoutError):
        waiter.wait(predicate, skipped_exceptions=(TypeError,))


def test_waiter_raises_unskipped_exceptions():
    """Verify that waiter supports skipped exceptions."""
    def predicate():
        raise LookupError('error')

    with pytest.raises(LookupError):
        waiter.wait(predicate, skipped_exceptions=(TypeError,))


def test_waiter_exception_message_contains_predicate_exception_message():
    """Verify that waiter supports skipped exceptions."""
    predicate_error = 'predicate error'

    def predicate():
        raise TypeError(predicate_error)

    with pytest.raises(waiter.TimeoutError) as e:
        waiter.wait(predicate, skipped_exceptions=(TypeError,))
        assert predicate_error in str(e)


def test_waiter_exception_message_contains_predicate_result_message():
    """Verify that waiter supports skipped exceptions."""
    predicate_error = 'predicate error'

    def predicate():
        return (False, predicate_error)

    with pytest.raises(waiter.TimeoutError) as e:
        waiter.wait(predicate)
        assert predicate_error in str(e)


def test_waiter_raises_exception_if_predicate_doesnot_return_tuple():
    """Verify that waiter raises exception if predicate result isn't tuple."""
    def predicate():
        return False

    with pytest.raises(TypeError) as e:
        waiter.wait(predicate)
        assert 'should return tuple' in str(e)


def test_waiter_exception_message_correct_if_no_name_predicate():
    """Verify waiter exception message correct if no predicate ``__name__``."""
    def predicate(*args, **kwgs):
        return (False, 'error')

    with pytest.raises(waiter.TimeoutError) as e:
        waiter.wait(functools.partial(predicate, foo='bar'))
        assert 'functools.partial' in str(e)


def test_waiter_provides_wait_for_message_to_exception_message():
    """Verify that waiter provides ``wait_for`` message to exception."""
    wait_for_message = "something happens"

    def predicate(*args, **kwgs):
        return (False, "error")

    with pytest.raises(waiter.TimeoutError) as e:
        waiter.wait(functools.partial(predicate, foo='bar'),
                    wait_for=wait_for_message)
        assert wait_for_message in str(e)
