"""
------------------------
Custom hamcrest matchers
------------------------
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

from hamcrest import equal_to
from hamcrest.core import matcher as _matcher
from hamcrest.core import string_description as _description


def expect_that(actual, matcher, reason=''):
    """Return boolean matching result with error message if it was false.

    Note:
        It's especially useful with ``stepler.third_party.waiter``:

        .. code:: python

           def predicate():
               return expect_that(1, 2):

           waiter.wait(predicate, timeout=2)

           # -->
           AssertionError: predicate returned false with timeout 1.99 seconds.
           Expected: <1>
                but: was <2>

    Arguments:
        actual (object): actual object
        matcher (object): matched object

    Returns:
        tuple: (True, None) if success and (False 'Error message') if failure
    """
    if not isinstance(matcher, _matcher.Matcher):
        matcher = equal_to(matcher)

    if not matcher.matches(actual):
        description = _description.StringDescription()
        description.append_text(reason)             \
                   .append_text('\nExpected: ')     \
                   .append_description_of(matcher)  \
                   .append_text('\n     but: ')
        matcher.describe_mismatch(actual, description)
        description.append_text('\n')

        return (False, str(description))
    else:
        return (True, None)
