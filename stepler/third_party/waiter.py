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

import time

from stepler import config
from stepler.third_party import logger


class TimeoutExpired(Exception):
    """Exception to raise when a timeout expires while waiting for result."""


@logger.log  # step can include several wait calls, and we want to log all
def wait(predicate, timeout_seconds=0, sleep_seconds=config.POLLING_TIME,
         multiplier=1, waiting_for=None, expected_exceptions=()):
    """Wait that predicate execution returns non-falsy result.

    Warning:
        predicate should return tuple: ``(predicate execution result,
        "Error message" or None)``

    Notes:
        - It attaches **error message of predicate result** to raised
          exception.

        - It makes early exit from waiting cycle if it sees, that polling time
          is higher than the time to the end of timeout, because it's obvious
          that next polling will not occur.

        - It provides to increase polling time by multiplying it to
          ``multiplier`` in each waiting cycle.

        - It includes real timeout to error message, but not function defined.

        - It hides own error traceback in output.

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

    predicate_name = getattr(predicate, '__name__', str(predicate))
    predicate_result_error = (
        "{} should return tuple (predicate result, 'Error message' or None)"
        "".format(predicate_name))

    result = message = None
    start = time.time()
    limit = start + timeout_seconds
    first = True

    while time.time() < limit or first:
        first = False

        try:
            result = predicate()

        except expected_exceptions as e:
            message = str(e)

        else:
            if not isinstance(result, tuple):
                raise TypeError(predicate_result_error)

            else:
                result, message = result

            if result:
                return result

        if sleep_seconds > limit - time.time():
            break

        time.sleep(sleep_seconds)
        sleep_seconds *= multiplier

    wait_error = 'Timeout of {:.3f} second(s) expired waiting for {}.'.format(
        time.time() - start, waiting_for or predicate_name)

    if message:
        wait_error += ' {} message: {}'.format(predicate_name, message)

    raise TimeoutExpired(wait_error)
