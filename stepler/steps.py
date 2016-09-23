"""
Base steps.

@author: schipiga@mirantis.com
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

__all__ = [
    'BaseSteps',
    'step',
    'STEPS'
]

# predefined permitted calls
STEPS = [
    'next',
    'range',
    'set_trace'
]


def step(func):
    """Decorator to append step name to storage."""
    STEPS.append(func.__name__)
    return func


class BaseSteps(object):
    """Base steps."""

    def __init__(self, client):
        """Constructor."""
        self._client = client
