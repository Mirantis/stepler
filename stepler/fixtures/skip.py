"""
--------------------
Skip autouse fixture
--------------------
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

import pytest

__all__ = [
    'skip_test',
]


@pytest.fixture(autouse=True)
def skip_test(request):
    """Autouse function fixture to skip test by predicate.

    Usage:
        .. code:: python

           @pytest.mark.requires("ceph_enabled")
           @pytest.mark.requires("more_computes_than(4)")
           @pytest.mark.requires("more_computes_than(2) and ceph_enabled")

        Supported logical operations ``and``, ``or``, ``not`` and their
        combinations.

    Args:
        request (object): pytest request
    """
    requires = request.node.get_marker('requires')
    if not requires:
        return

    # TODO(schipiga): configure with real env config, when it will be possible
    predicates = Predicates(None)
    predicates = {attr: getattr(predicates, attr) for attr in dir(predicates)
                  if not attr.startswith('_')}

    if not eval(requires, predicates):
        pytest.skip(
            'Skipped due to a mismatch to condition: {!r}'.format(requires))


# TODO(schipiga): populate predicates when it will be possible
class Predicates(object):
    """Namespace for predicates to skip a test."""

    _env = None

    def __init__(cls, env):
        """Initialize."""
        cls._env = env

    @classmethod
    def more_computes_than(self, count):
        """Define whether computes enough."""

    @property
    def ceph_enabled(self):
        """Define whether CEPH enabled."""
