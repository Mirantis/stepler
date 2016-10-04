"""
----------------
Logger for steps
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

from functools import wraps
from logging import getLogger
from time import time

from stepler.third_party.utils import get_unwrapped_func

LOGGER = getLogger(__name__)


def log(func):
    """Decorator to log function with arguments and execution time."""
    @wraps(func)
    def wrapper(*args, **kwgs):
        # reject self from log if it is present
        args = list(args)
        largs = args[:]
        if largs:
            arg = largs[0]
            im_func = getattr(
                getattr(arg, func.__name__, None), 'im_func', None)
            if get_unwrapped_func(im_func) is get_unwrapped_func(func):
                largs.remove(arg)

        LOGGER.debug(
            'Function {!r} starts with args {!r} and kwgs {!r}'.format(
                func.__name__, largs, kwgs))
        start = time()
        try:
            result = func(*args, **kwgs)
        finally:
            LOGGER.debug('Function {!r} ended in {:.4f} sec'.format(
                func.__name__, time() - start))
        return result

    return wrapper
