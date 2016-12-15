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
           @pytest.mark.requires("computes_count > 4")
           @pytest.mark.requires("computes_count > 4 and ceph_enabled")

        It supports any logical and arithmetical operations and their
        combinations.

    Args:
        request (object): pytest request
    """
    marker = request.node.get_marker('requires')
    if not marker:
        return

    predicates = Predicates(request)

    for requires in marker.args:

        tree = ast.parse(requires, mode='eval')

        tree = RewritePredicates().visit(tree)
        tree = ast.fix_missing_locations(tree)
        code = compile(tree, '<ast>', mode='eval')

        if not eval(code, {PREDICATES: predicates}):
            pytest.skip('Skipped due to a mismatch to condition: {!r}\n'
                        'Calculated conditions: {}'.format(
                            requires, predicates._get_calculated_conditions()))

        predicates._clear_calls()


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

    def _store_call(f):
        """Decorator to store each method call with result."""
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            self._calls.append([f.__name__, result])
            return result
        return wrapper

    def _clear_calls(self):
        """Clear calls history."""
        self._calls[:] = []

    def _get_calculated_conditions(self):
        """Get all calculated conditions (names and results).

        Returns:
            str: string with all calculated conditions
        """
        return ', '.join(['{}={}'.format(*call) for call in self._calls])

    def _get_fixture(self, fixture_name):
        return self._request.getfixturevalue(fixture_name)

    @property
    def _network_type(self):
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_network_type()

    @property
    @_store_call
    def computes_count(self):
        """Returns computes count."""
        hypervisor_steps = self._get_fixture('hypervisor_steps')
        return len(hypervisor_steps.get_hypervisors(check=False))

    @property
    @_store_call
    def controllers_count(self):
        """Returns controllers count."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return len(os_faults_steps.get_nodes(service_names=[config.NOVA_API]))

    @property
    @_store_call
    def dhcp_agent_nodes_count(self):
        """Get DHCP agents nodes count."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return len(
            os_faults_steps.get_nodes(
                service_names=[config.NEUTRON_DHCP_SERVICE], check=False))

    @property
    @_store_call
    def l3_agent_nodes_count(self):
        """Get L3 agents nodes count."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return len(
            os_faults_steps.get_nodes(
                service_names=[config.NEUTRON_L3_SERVICE], check=False))

    @property
    @_store_call
    def l3_agent_nodes_with_snat_count(self):
        """Get count of L3 agent nodes with SNAT."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return len(
            os_faults_steps.get_nodes_with_services(
                service_names=[config.NEUTRON_L3_SERVICE, config.NOVA_API],
                check=False))

    @property
    @_store_call
    def nova_ceph(self):
        """Define whether nova ceph enabled."""
        return self._get_fixture('nova_ceph_enabled')

    @property
    @_store_call
    def vlan(self):
        """Define whether neutron configures with vlan."""
        return self._network_type == config.NETWORK_TYPE_VLAN

    @property
    @_store_call
    def vxlan(self):
        """Define whether neutron configures with vxlan."""
        return self._network_type == config.NETWORK_TYPE_VXLAN

    @property
    @_store_call
    def l3_ha(self):
        """Define whether neutron configures with l3 ha."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_neutron_l3_ha()

    @property
    @_store_call
    def dvr(self):
        """Define whether neutron configures with DVR."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_neutron_dvr()

    @property
    @_store_call
    def l2pop(self):
        """Define whether neutron configures with L2pop."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_neutron_l2pop()

    @property
    @_store_call
    def glance_backend(self):
        """Get glance default backend."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_glance_backend()

    @property
    @_store_call
    def cinder_nodes_count(self):
        """Get count of cinder nodes."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return len(os_faults_steps.get_nodes(
                   service_names=[config.CINDER_VOLUME]))

    @property
    @_store_call
    def neutron_debug(self):
        """Define whether neutron configures with debug mode."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_neutron_debug()

    @property
    @_store_call
    def horizon_cinder_backup(self):
        """Define whether horizon cinder backup enabled."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        return os_faults_steps.get_horizon_cinder_backups()

    @property
    @_store_call
    def computes_suitable_for_all_flavors_count(self):
        """Get count of computes suitable for any of precreated flavor."""
        flavor_steps = self._get_fixture('flavor_steps')
        hypervisor_steps = self._get_fixture('hypervisor_steps')
        flavors = flavor_steps.get_flavors(check=False)
        count = 0
        for hypervisor in hypervisor_steps.get_hypervisors(check=False):
            for flavor in flavors:
                capacity = hypervisor_steps.get_hypervisor_capacity(
                    hypervisor, flavor, check=False)
                if capacity == 0:
                    break
            else:
                count += 1
        return count
