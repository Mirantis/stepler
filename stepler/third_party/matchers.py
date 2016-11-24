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

# TODO(gdyuldin): remove this file after checking

import functools
import warnings

from stepler.third_party import waiter


@functools.wraps(waiter.expect_that)
def expect_that(*args, **kwargs):
    warnings.warn("Uses of `expect_that` from stepler.third_party.matchers is "
                  "deprecated. You should use expect_that from "
                  "stepler.third_party.waiting", DeprecationWarning)
    return waiter.expect_that(*args, **kwargs)
