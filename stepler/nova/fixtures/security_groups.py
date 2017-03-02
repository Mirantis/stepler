"""
--------------
Security group
--------------
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

import warnings

import attrdict
import pytest

from stepler.nova import steps

__all__ = [
    'security_group',
    'security_group_steps',
    'get_security_group_steps',
]


@pytest.fixture(scope='session')
def get_security_group_steps(get_nova_client):
    """Callable session fixture to get security groups steps.

    Args:
        get_nova_client (function): function to get nova client.

    Returns:
        function: function to get security groups steps.
    """
    warnings.warn("Nova API from 2.36 microversion is not supported security "
                  "groups creation. Use `get_neutron_security_group_steps` "
                  "instead", DeprecationWarning)

    def _get_security_group_steps(**credentials):
        return steps.SecurityGroupSteps(get_nova_client(**credentials))

    return _get_security_group_steps


@pytest.fixture
def security_group_steps(get_security_group_steps):
    """Fixture to get security group steps.

    Args:
        get_security_group_steps (function): function to get security groups
            steps
    """
    warnings.warn("Nova API from 2.36 microversion is not supported security "
                  "groups creation. Use `neutron_security_group_steps` "
                  "instead", DeprecationWarning)
    return get_security_group_steps()


@pytest.fixture
def security_group(neutron_security_group):
    """Fixture to create security group before test.

    This fixture designed for backward compatibility.

    Args:
        neutron_security_group (dict): created security group

    Returns:
        attrdict.AttrDict: security group
    """
    warnings.warn("Nova API from 2.36 microversion is not supported security "
                  "groups creation. Use `neutron_security_group` instead",
                  DeprecationWarning)
    return attrdict.AttrDict(neutron_security_group)
