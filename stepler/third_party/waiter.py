"""
------
Waiter
------
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
import sys

from hamcrest import assert_that
import six
import waiting

from stepler.third_party import logger


@six.python_2_unicode_compatible
class ExpectationError(Exception):
    """Expectation error class."""

    def __init__(self, base_ex):
        self.base_ex = base_ex

    def __str__(self):
        return u"{}".format(self.base_ex)


@functools.wraps(assert_that)
def expect_that(*args, **kwargs):
    """Wrapper for hamcrest's ``assert_that``.

    It raises ExpectationError instead of AssetionError and can be used with
    wait function below to retrive more verbose messages about predicates
    failures.
    """
    try:
        assert_that(*args, **kwargs)
        return True
    except AssertionError as e:
        six.reraise(ExpectationError, ExpectationError(e), sys.exc_info()[-1])


@six.python_2_unicode_compatible
class TimeoutExpired(Exception):
    """Timeout expired exception."""
    def __init__(self, base_ex):
        self.base_ex = base_ex
        self.message = ''

    def __str__(self):
        return u"{}{}".format(self.base_ex, self.message)


@logger.log
def wait(predicate, args=None, kwargs=None, expected_exceptions=(),
         **wait_kwargs):
    """Wait that predicate execution returns non-falsy result.

    It catches all raised ExpectationError and uses last exception to construct
    TimeoutException. It also can pass arguments to predicate.

    Example:
        >>> def predicate(foo, bar='baz'):
        ...    expect_that(foo, equal_to(bar))
        ...    return bar
        >>> wait(predicate, args=(1,), kwargs={'bar': 2}, timeout_seconds=1)

        TimeoutExpired: Timeout of 1 seconds expired waiting for
        <function predicate at 0x7f7798622c08>

        Expected: <2>
             but: was <1>


        >>> wait(lambda: False, timeout_seconds=0.5)

        TimeoutExpired: Timeout of 0.5 seconds expired waiting for
        <function <lambda> at 0x7f2b54360848>
        No exception raised during predicate executing

    Args:
        predicate (function): predicate to wait execution result
        timeout_seconds (int): seconds to wait result
        sleep_seconds (float): polling time between predicate executions
        multiplier (int): coefficient to multiply polling time
        expected_exceptions (tuple): predicate exceptions which will be omitted
            during waiting.
        waiting_for (str): custom waiting message.

    Returns:
        tuple: result of predicate execution in format:
            (predicate result, "Error message" or None)

    Raises:
        TimeoutExpired: if predicate execution has falsy value after timeout
    """

    __tracebackhide__ = True
    raised_exceptions = []
    args = args or ()
    kwargs = kwargs or {}

    if isinstance(expected_exceptions, tuple):
        expected_exceptions += (ExpectationError,)
    elif (isinstance(expected_exceptions, type) and
          issubclass(expected_exceptions, Exception)):
        expected_exceptions = (expected_exceptions, ExpectationError,)
    else:
        raise ValueError('expected_exceptions should be tuple or '
                         'Exception subclass')

    @functools.wraps(predicate)
    def wrapper():
        try:
            return predicate(*args, **kwargs)
        except expected_exceptions as e:
            raised_exceptions.append(e)
            return False

    try:
        return waiting.wait(wrapper, **wait_kwargs)
    except waiting.TimeoutExpired as e:
        ex = TimeoutExpired(e)
        if raised_exceptions:
            ex.message += "\n{0}: {1}".format(
                type(raised_exceptions[-1]).__name__,
                raised_exceptions[-1])
        else:
            ex.message += "\nNo exception raised during predicate executing"
        raise ex
