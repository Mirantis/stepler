"""
-------------
Horizon pages
-------------
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

from .api_access import PageApiAccess  # noqa
from .base import PageBase
from .containers import PageContainers
from .defaults import PageDefaults
from .flavors import PageFlavors
from .host_aggregates import PageHostAggregates
from .images import PageImage, PageImages, PageUserImages  # noqa
from .instances import (PageInstance,
                        PageInstances,
                        PageAdminInstances)  # noqa
from .keypairs import PageKeypairs
from .login import PageLogin
from .metadata_definitions import PageMetadataDefinitions
from .networks import (PageAdminNetworks,
                       PageFloatingIPs,
                       PageManageRules,
                       PageNetwork,
                       PageNetworkTopology,
                       PageNetworks,
                       PageSecurityGroups)  # noqa
from .projects import PageProjects
from .routers import PageRouters
from .settings import PagePassword, PageSettings  # noqa
from .stacks import PageStack, PageStacks  # noqa
from .users import PageUsers
from .volumes import (PageAdminVolumes,
                      PageVolume,
                      PageVolumes,
                      PageVolumeTransfer)  # noqa
from .overview import PageOverview  # noqa

pages = [
    PageAdminInstances,
    PageAdminNetworks,
    PageAdminVolumes,
    PageApiAccess,
    PageBase,
    PageContainers,
    PageDefaults,
    PageFlavors,
    PageFloatingIPs,
    PageHostAggregates,
    PageImage,
    PageImages,
    PageInstance,
    PageInstances,
    PageKeypairs,
    PageLogin,
    PageManageRules,
    PageMetadataDefinitions,
    PageNetwork,
    PageNetworkTopology,
    PageNetworks,
    PagePassword,
    PageProjects,
    PageRouters,
    PageSecurityGroups,
    PageSettings,
    PageStack,
    PageStacks,
    PageUsers,
    PageUserImages,
    PageVolume,
    PageVolumes,
    PageVolumeTransfer,
    PageOverview
]
