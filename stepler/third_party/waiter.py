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


class TimeoutError(Exception):
    """Custom exception to be raised with waiter."""


def wait(predicate, timeout=0, polling_time=config.POLLING_TIME, rate=1,
         skipped_exceptions=(), wait_for=None):
    """Wait that predicate execution returns non-falsy result.

    Warning:
        **predicate should return tuple: (predicate execution result,
        "Error message" or None)**

    Notes:
        - It attaches **error message of predicate result** to raised
          exception.

        - It makes early exit from waiting cycle if it sees, that polling time
          is higher than the time to the end of timeout, because it's obvious
          that next polling will not occur.

        - It provides to increase polling time by multiplying it to ``rate``
          in each waiting cycle.

        - It includes real timeout to error message, but not function defined.

        - It hides own error traceback in output.

    Args:
        predicate (function): predicate to wait execution result
        timeout (int): seconds to wait result
        polling_time (float): polling time between predicate executions
        rate (int): coefficient to multiply polling time
        skipped_exceptions (tuple): predicate exceptions which will be omitted
            during waiting.
        wait_for (str): custom waiting message.

    Returns:
        tuple: result of predicate execution in format:
            (predicate result, "Error message" or None)

    Raises:
        AssertionError: if predicate execution is false after timeout
    """
    __tracebackhide__ = True

    predicate_name = getattr(predicate, '__name__', str(predicate))
    predicate_result_error = (
        "{} should return tuple (predicate result, 'Error message' or None)"
        "".format(predicate_name))

    result = message = None
    start = time.time()
    limit = start + timeout
    first = True

    while time.time() < limit or first:
        first = False

        try:
            result = predicate()

        except skipped_exceptions as e:
            message = str(e)

        else:
            if not isinstance(result, tuple):
                raise TypeError(predicate_result_error)

            else:
                result, message = result

            if result:
                return result

        if polling_time > limit - time.time():
            break

        time.sleep(polling_time)
        polling_time *= rate

    wait_error = 'Timeout of {:.3f} second(s) expired waiting for {}.'.format(
        time.time() - start, wait_for or predicate_name)

    if message:
        wait_error += ' {} message: {}'.format(predicate_name, message)

    raise TimeoutError(wait_error)
