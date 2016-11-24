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

import ast
import functools

import pytest

from stepler import config

__all__ = [
    'skip_test',
]


PREDICATES = 'predicates'


@pytest.fixture(autouse=True)
def skip_test(request):
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
    """
    requires = request.node.get_marker('requires')
    if not requires:
        return

    if len(requires.args) == 1:
        requires = requires.args[0]
    else:
        requires = map(lambda req: '({})'.format(req), requires.args)
        requires = ' and '.join(requires)

    predicates = Predicates(request)
    tree = ast.parse(requires, mode='eval')

    tree = RewritePredicates().visit(tree)
    ast.fix_missing_locations(tree)
    code = compile(tree, '<ast>', mode='eval')

    if not eval(code, {PREDICATES: predicates}):
        pytest.skip('Skipped due to a mismatch to condition: {!r}\n'
                    'Calculated conditions: {}'.format(
                        requires, predicates.get_calculated_conditions()))


class RewritePredicates(ast.NodeTransformer):
    """Class to rewrite requires to predicate instance attributes."""

    def visit_Name(self, node):
        return ast.copy_location(
            ast.Attribute(
                value=ast.Name(
                    id=PREDICATES, ctx=ast.Load()),
                attr=node.id,
                ctx=node.ctx),
            node)


class Predicates(object):
    """Namespace for predicates to skip a test."""

    def __init__(self, request):
        """Initialize."""
        self._request = request
        self._calls = []

    def store_call(f):
        """Decorator to store each method call with result."""
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            self = args[0]
            result = f(*args, **kwargs)
            self._calls.append([f.__name__, result])
            return result
        return wrapper

    def get_calculated_conditions(self):
        """Get all calculated conditions (names and results).

        Returns:
            str: string with all calculated conditions
        """
        return ', '.join(['{}={}'.format(*call) for call in self._calls])

    def _get_fixture(self, fixture_name):
        return self._request.getfixturevalue(fixture_name)

    def _network_type(self):
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_network_type()

    @store_call
    def computes_count_gte(self, count):
        """Define whether computes enough."""
        hypervisor_steps = self._get_fixture('hypervisor_steps')
        return len(hypervisor_steps.get_hypervisors()) >= count

    @property
    @store_call
    def ceph_enabled(self):
        """Define whether CEPH enabled."""

    @property
    @store_call
    def vlan(self):
        """Define whether neutron configures with vlan."""
        return self._network_type == config.NETWORK_TYPE_VLAN

    @property
    @store_call
    def vxlan(self):
        """Define whether neutron configures with vxlan."""
        return self._network_type == config.NETWORK_TYPE_VXLAN
