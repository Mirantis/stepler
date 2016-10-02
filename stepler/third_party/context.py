"""
--------------------------------
Custom context manager generator
--------------------------------
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
# limitations under the License.from functools import wraps

from functools import wraps

import six

__all__ = ["context"]


class ContextGenerator(object):
    """Helper for @context decorator."""

    def __init__(self, generator):
        self._generator = generator

    def __enter__(self):
        try:
            return self._generator.next()
        except StopIteration:
            raise RuntimeError("generator didn't yield")

    def __exit__(self, ext_type, ext_val, ext_tb):
        try:
            self._generator.next()
        except StopIteration:
            pass
        except:
            if not ext_type:
                raise  # finalization error if no root cause error inside cm
        else:
            raise RuntimeError("generator didn't stop")
        if ext_type:
            six.reraise(ext_type, ext_val, ext_tb)


def context(func):
    """
    Decorator to make context manager from generator with guaranteed
    finalization.

    Note:
        ``contextlib.contextmanager`` doesn't guarantee context manager
        finalization and requires usage of ``try-finally`` for that. But in
        fixtures it needs to rid of ``try-finally`` and to guarantee context
        manager finalization after ``yield``. This decorator makes that.

    Example:
        .. code:: python

           @pytest.fixture
           def create_server_context(server_steps):

               @context
               def _create_server_context(server_name, *args, **kwgs):
                   server = server_steps.create_server(server_name,
                                                       *args, **kwgs)
                   yield server
                   server_steps.delete_server(server)

               return _create_server_context

    See Also:
        #. Exception inside context manager:

           .. code:: python

              @context
              def x():
                  yield

              with x():
                  raise Exception('error')

           ``Exception: error`` will be raised.

        #. Exception in context manager finalization:

           .. code:: python

              @context
              def x():
                  yield
                  raise Exception('final')

              with x():
                  pass

           ``Exception: final`` will be raised.

        #. Exceptions inside context manager and in finalization:

           .. code:: python

              @context
              def x():
                  yield
                  raise Exception('final')

              with x():
                  raise Exception('error')

           ``Exception: error`` will be raise as root cause.
    """
    @wraps(func)
    def wrapper(*args, **kwgs):
        return ContextGenerator(func(*args, **kwgs))

    return wrapper
