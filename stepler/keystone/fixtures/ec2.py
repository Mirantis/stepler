"""
------------
Ec2 fixtures
------------
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

from stepler.keystone import steps

__all__ = [
    'ec2_steps',
    'ec2_credentials',
]


@pytest.fixture
def ec2_steps(keystone_client):
    """Fixture to get ec2 steps.

    Args:
        keystone_client (object): keystone client for authorizing

    Returns:
        object: object with ec2 credentials steps
    """
    return steps.Ec2Steps(keystone_client.ec2)


@pytest.fixture
def ec2_credentials(ec2_steps, current_project, current_user):
    """Fixture to create EC2 credentials for current user.

    After the test it destroys created credentials.

    Args:
        ec2_steps (obj): instantiated EC2 steps
        current_project (obj): current project
        current_user (obj): current user
    """
    return ec2_steps.create(current_user, current_project)
