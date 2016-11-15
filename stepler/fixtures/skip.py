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
def skip_test(request, hypervisor_steps):
    """Autouse function fixture to skip test by predicate.

    Usage:
        .. code:: python

           @pytest.mark.requires("ceph_enabled")
           @pytest.mark.requires("more_computes_than(4)")
           @pytest.mark.requires("more_computes_than(2) and ceph_enabled")

        It supports any logical and arithmetical operations and their
        combinations.

    Args:
        request (object): pytest request
        hypervisor_steps (object): instantiated hypervisors steps
    """
    requires = request.node.get_marker('requires')
    if not requires:
        return

    if len(requires.args) == 1:
        requires = requires.args[0]
    else:
        requires = map(lambda req: '({})'.format(req), requires.args)
        requires = ' and '.join(requires)

    predicates = Predicates({'hypervisors_steps': hypervisor_steps})
    predicates = {attr: getattr(predicates, attr) for attr in dir(predicates)
                  if not attr.startswith('_')}

    if not eval(requires, predicates):
        pytest.skip(
            'Skipped due to a mismatch to condition: {!r}'.format(requires))


# TODO(schipiga): populate predicates when it will be possible
class Predicates(object):
    """Namespace for predicates to skip a test."""

    def __init__(self, env):
        """Initialize."""
        self._env = env

    def computes_count_gte(self, count):
        """Define whether computes enough."""
        return len(self._env['hypervisors_steps'].get_hypervisors()) >= count

    @property
    def ceph_enabled(self):
        """Define whether CEPH enabled."""
