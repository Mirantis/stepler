"""
----------------------
Neutron qouta fixtures
----------------------
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

from stepler.neutron import steps

__all__ = [
    'get_neutron_quota_steps',
    'neutron_quota_steps',
    'change_neutron_quota',
]


@pytest.fixture(scope="session")
def get_neutron_quota_steps(get_neutron_client):
    """Callable session fixture to get neutron quota steps.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client

    Returns:
        function: function to get instantiated neutron quota steps
    """

    def _get_steps(**credentials):
        return steps.QuotaSteps(get_neutron_client(**credentials).quotas)

    return _get_steps


@pytest.fixture
def neutron_quota_steps(get_neutron_quota_steps):
    """Function fixture to get neutron quota steps.

    Args:
        get_neutron_quota_steps (function): function to get instantiated
            neutron quota steps

    Returns:
        stepler.neutron.steps.QuotaSteps: instantiated neutron quota steps
    """
    return get_neutron_quota_steps()


@pytest.fixture
def change_neutron_quota(request, current_project, neutron_quota_steps):
    """Function fixture to change neutron quota values for test.

    After test all neutron quota values will be restored with original values.

    Note:
        This fixture should be parametrized.

    Example:
        @pytest.mark.parametrize('change_neutron_quota', [{
                    'network': 30,
                    'router': 30,
                    'subnet': 30,
                    'port': 90}
        ], indirect=True)
        def test_foo(change_neutron_quota):
            # test logic

    Args:
        request (obj): py.test's SubRequest
        current_project (obj): current project
        neutron_quota_steps (obj): instantiated neutron quota steps
    """
    new_values = request.param
    old_values = neutron_quota_steps.get(current_project)

    neutron_quota_steps.update(current_project, new_values)

    yield

    neutron_quota_steps.update(current_project, old_values)
