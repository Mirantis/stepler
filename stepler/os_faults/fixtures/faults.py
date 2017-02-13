"""
------------------
os_faults fixtures
------------------
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

import os_faults
import pytest

from stepler import config
from stepler.os_faults.steps import OsFaultsSteps
from stepler import os_faults_config
from stepler.third_party import context
from stepler.third_party import network_checks

__all__ = [
    'os_faults_client',
    'os_faults_steps',
    'patch_ini_file_and_restart_services',
    'execute_command_with_rollback',
    'nova_api_node',
    'ironic_api_node',
    'shutdown_nodes',
]


@pytest.fixture(scope='session')
def os_faults_client():
    """Function fixture to get os_faults client.

    Returns:
        object: instantiated os_faults client
    """
    if os_faults_config.OS_FAULTS_CONFIG:
        destructor = os_faults.connect(
            config_filename=os_faults_config.OS_FAULTS_CONFIG)
    else:
        destructor = os_faults.connect(os_faults_config.OS_FAULTS_DICT_CONFIG)

    destructor.verify()
    return destructor


@pytest.fixture(scope='session')
def os_faults_steps(os_faults_client):
    """Function fixture to get os_faults steps.

    Args:
        os_faults_client (object): instantiated os_faults client

    Returns:
        stepler.os_faults.steps.OsFaultsSteps: instantiated os_faults steps
    """
    return OsFaultsSteps(os_faults_client)


@pytest.fixture(scope='session')
def patch_ini_file_and_restart_services(os_faults_steps):
    """Session callable fixture to modify config files and restart services.

    It can be called several times during test. It is used as context manager
    to guarantee the result.

    Args:
        os_faults_steps: instantiated os_faults steps.

    Returns:
        context.context: context manager to restore backup and restart services
    """

    @context.context
    def _patch_ini_file_and_restart_services(
            service_names, file_path, option, value, section=None):
        nodes = os_faults_steps.get_nodes_with_any_service(
            service_names=service_names)

        backup_path = os_faults_steps.patch_ini_file(
            nodes, file_path, option, value, section)
        os_faults_steps.restart_services(service_names)

        yield

        os_faults_steps.restore_backup(nodes, file_path, backup_path)
        os_faults_steps.restart_services(service_names)

    return _patch_ini_file_and_restart_services


@pytest.fixture(scope='session')
def execute_command_with_rollback(os_faults_steps):
    """Callable fixture to execute provided bash command on nodes.
    Then performs execution of a provided rollback command.

    It can be called several times during test. It is used as context manager
    to guarantee the result.

    Args:
        os_faults_steps: instantiated os_faults steps.

    Returns:
        context.context: context manager to run cmd and run rollback cmd
    """

    @context.context
    def _exec_cmd_with_rollback(nodes, cmd, rollback_cmd, check=True):
        os_faults_steps.execute_cmd(nodes, cmd, check=check)
        yield
        os_faults_steps.execute_cmd(nodes, rollback_cmd, check=check)

    return _exec_cmd_with_rollback


@pytest.fixture
def nova_api_node(os_faults_steps):
    """Function fixture to get node with nova-api service.

    This node will be helpful for executing openstack CLI commands on it.

    Args:
        os_faults_steps (object): instantiated os_faults steps

    Returns:
        obj: node with nova-api service
    """
    return os_faults_steps.get_node(service_names=[config.NOVA_API])


@pytest.fixture
def ironic_api_node(os_faults_steps):
    """Function fixture to get node with ironic-api service.

    Args:
        os_faults_steps (object): instantiated os_faults steps

    Returns:
        obj: node with ironic-api service
    """
    return os_faults_steps.get_node(service_names=[config.IRONIC_API])


@pytest.fixture
def shutdown_nodes(os_faults_steps, get_nova_client, nova_service_steps):
    """Callable fixture to shutdown nodes gracefully.

    Can be called several times during a test.
    After the test all stopped nodes are powered on.

    Args:
        os_faults_steps (object): instantiated os_faults steps

    Yields:
        function: function to shutdown nodes
    """
    stopped_fqdns = []

    def _shutdown_nodes(nodes):
        os_faults_steps.shutdown_nodes(nodes)
        fqdns = [node.fqdn for node in nodes]
        stopped_fqdns.extend(fqdns)

    yield _shutdown_nodes

    fqdns_to_start = []
    for fqdn in stopped_fqdns:
        node = os_faults_steps.get_node(fqdns=[fqdn])
        ip = node.get_ips()[0]
        if not network_checks.check_tcp_connect(ip):
            fqdns_to_start.append(fqdn)

    if fqdns_to_start:
        nodes_to_start = os_faults_steps.get_nodes(fqdns=fqdns_to_start)
        os_faults_steps.poweron_nodes(nodes_to_start)
        # reinit nova client and wait for its availability
        get_nova_client()
        nova_service_steps.check_services_up(
            timeout=config.NOVA_SERVICES_UP_TIMEOUT)
        time.sleep(config.NOVA_TIME_AFTER_SERVICES_UP)
