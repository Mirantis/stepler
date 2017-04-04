"""
---------------------
Cinder quota fixtures
---------------------
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

from stepler.cinder import steps
from stepler import config

__all__ = [
    'get_cinder_quota_steps',
    'cinder_quota_steps',
    'big_snapshot_quota',
    'volume_size_quota',
]


@pytest.fixture(scope='session')
def get_cinder_quota_steps(get_cinder_client):
    """Callable session fixture to get cinder quota steps.

    Args:
        get_cinder_client (function): function to get cinder client

    Returns:
        function: function to get cinder quota steps
    """
    def _get_cinder_quota_steps(version=config.CURRENT_CINDER_VERSION,
                                is_api=False,
                                **credentials):
        return steps.CinderQuotaSteps(
            get_cinder_client(version, is_api, **credentials).quotas)

    return _get_cinder_quota_steps


@pytest.fixture
def cinder_quota_steps(get_cinder_quota_steps):
    """Function fixture to get cinder quota steps.

    Args:
        get_cinder_quota_steps (function): function to get cinder quota steps

    Returns:
        stepler.cinder.steps.CinderQuotaSteps: instantiated quota steps
    """
    return get_cinder_quota_steps()


@pytest.fixture(scope='session')
def big_snapshot_quota(get_current_project, get_cinder_quota_steps):
    """Session fixture to increase cinder snapshots count quota.

    This fixture restore original quota value after test.

    Args:
        get_current_project (function): function to get current project
        get_cinder_quota_steps (function): function to get cinder quota steps
    """
    _current_project = get_current_project()
    _cinder_quota_steps = get_cinder_quota_steps()

    original_quota = _cinder_quota_steps.get_snapshots_quota(_current_project)
    _cinder_quota_steps.set_snapshots_quota(
        _current_project, config.CINDER_SNAPSHOTS_QUOTA_BIG_VALUE)

    yield

    get_cinder_quota_steps().set_snapshots_quota(_current_project,
                                                 original_quota)


@pytest.fixture
def volume_size_quota(current_project, cinder_quota_steps):
    """Function fixture to get cinder volume size quota.

    Default value for volume size quota can be too large for some tests.
    This fixture sets volume size quota for the current project to
    the value from config and then yields this value.
    The fixture restores original quota value after test.

    Args:
        current_project (obj): current project
        cinder_quota_steps (obj): initialized cinder quota steps

    Yields:
        int: volume size quota value
    """
    original_quota = cinder_quota_steps.get_volume_size_quota(current_project)

    cinder_quota_steps.set_volume_size_quota(
        current_project, config.CINDER_VOLUME_MAX_SIZE_QUOTA_VALUE)

    yield config.CINDER_VOLUME_MAX_SIZE_QUOTA_VALUE

    cinder_quota_steps.set_volume_size_quota(current_project, original_quota)
