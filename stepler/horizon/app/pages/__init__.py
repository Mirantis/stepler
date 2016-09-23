"""
Module with horizon pages.

@author: schipiga@mirantis.com
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

from .access import PageAccess
from .base import PageBase
from .containers import PageContainers
from .defaults import PageDefaults
from .flavors import PageFlavors
from .host_aggregates import PageHostAggregates
from .images import PageImage, PageImages
from .instances import PageInstance, PageInstances
from .login import PageLogin
from .metadata_definitions import PageMetadataDefinitions
from .networks import (PageAdminNetworks,
                       PageNetwork,
                       PageNetworks)
from .projects import PageProjects
from .routers import PageRouters
from .settings import PagePassword, PageSettings
from .users import PageUsers
from .volumes import (PageAdminVolumes,
                      PageVolume,
                      PageVolumes,
                      PageVolumeTransfer)

pages = [
    PageAccess,
    PageAdminNetworks,
    PageAdminVolumes,
    PageBase,
    PageContainers,
    PageDefaults,
    PageFlavors,
    PageHostAggregates,
    PageImage,
    PageImages,
    PageInstance,
    PageInstances,
    PageLogin,
    PageMetadataDefinitions,
    PageNetwork,
    PageNetworks,
    PagePassword,
    PageProjects,
    PageRouters,
    PageSettings,
    PageUsers,
    PageVolume,
    PageVolumes,
    PageVolumeTransfer
]
