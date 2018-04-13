"""
-------------
Horizon steps
-------------

Contains steps specific for horizon (UI testing).
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

from .api_access import ApiAccessSteps  # noqa
from .auth import AuthSteps  # noqa
from .containers import ContainersSteps  # noqa
from .defaults import DefaultsSteps  # noqa
from .flavors import FlavorsSteps  # noqa
from .floating_ips import FloatingIPsSteps  # noqa
from .host_aggregates import HostAggregatesSteps  # noqa
from .images import ImagesSteps  # noqa
from .instances import InstancesSteps  # noqa
from .keypairs import KeypairsSteps  # noqa
from .metadata_definitions import NamespacesSteps  # noqa
from .networks import NetworksSteps  # noqa
from .overview import OverviewSteps
from .projects import ProjectsSteps  # noqa
from .routers import RoutersSteps  # noqa
from .security_groups import SecurityGroupsSteps  # noqa
from .settings import SettingsSteps  # noqa
from .stacks import StacksSteps  # noqa
from .users import UsersSteps  # noqa
from .volume_types import VolumeTypesSteps  # noqa
from .volumes import VolumesSteps  # noqa

__all__ = [
    'ApiAccessSteps',
    'AuthSteps',
    'ContainersSteps',
    'DefaultsSteps',
    'FlavorsSteps',
    'FloatingIPsSteps',
    'HostAggregatesSteps',
    'ImagesSteps',
    'InstancesSteps',
    'KeypairsSteps',
    'NamespacesSteps',
    'NetworksSteps',
    'OverviewSteps',
    'ProjectsSteps',
    'RoutersSteps',
    'SecurityGroupsSteps',
    'SettingsSteps',
    'StacksSteps',
    'UsersSteps',
    'VolumeTypesSteps',
    'VolumesSteps'
]
