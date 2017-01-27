"""
-----------------
RabbitMQ fixtures
-----------------
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

from stepler import config
from stepler.nova import steps

__all__ = [
    'rabbitmq_steps',
    'get_rabbitmq_cluster_data',
]


@pytest.fixture
def rabbitmq_steps():
    """Function fixture to get RabbitMQ steps.

    Returns:
        stepler.nova.steps.RabbitMQSteps: instantiated RabbitMQ steps
    """
    return steps.RabbitMQSteps()


@pytest.fixture
def get_rabbitmq_cluster_data(os_faults_steps):
    """Callable fixture to get RabbitMQ cluster config data and its status.

   Args:
        os_faults_steps: instantiated os_faults steps.

    Returns:
        function: function to get cluster data.
    """
    cluster_node_names, fqdns, ip_addresses = (
        os_faults_steps.get_rabbitmq_cluster_config_data())

    def _get_cluster_data():
        ctl_fqdn = fqdns[-1]
        ctl_node = os_faults_steps.get_node(fqdns=[ctl_fqdn])
        cluster_status = os_faults_steps.execute_cmd(
            ctl_node, config.RABBITMQ_CHECK_CLUSTER_CMD)[0].payload['stdout']
        return cluster_node_names, fqdns, ip_addresses, cluster_status

    return _get_cluster_data
