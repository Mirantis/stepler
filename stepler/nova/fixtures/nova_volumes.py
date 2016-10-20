"""
-----------------------
Server volumes fixtures
-----------------------
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
from stepler.nova.steps import NovaVolumeSteps

__all__ = [
    'nova_volume_steps',
    'attach_volume_to_server',
    'detach_volume_from_server'
]


@pytest.fixture
def nova_volume_steps(nova_client):
    """Function fixture to get server volumes steps.

    Args:
        nova_client (stepler.nova): instantiated nova object.

    Returns:
        object: instantiated steps objects for server volumes
    """
    return NovaVolumeSteps(nova_client.volumes)


@pytest.fixture
def attach_volume_to_server(nova_volume_steps, cinder_steps):
    """Function fixture to attach volume to server.

    Can be called several times during test.
    """
    def _attach_volume_to_server(server, volume, *args, **kwgs):
        attached_ids = cinder_steps.get_volume_attachment_ids(volume)
        nova_volume_steps.attach_volume_to_server(server, volume,
                                                  *args, **kwgs)
        cinder_steps.check_volume_status(volume, 'in-use',
                                         timeout=config.VOLUME_IN_USE_TIMEOUT)
        attached_ids.append(server.id)
        cinder_steps.check_volume_attachments(volume, attached_ids)

    return _attach_volume_to_server


@pytest.fixture
def detach_volume_from_server(nova_volume_steps, cinder_steps):
    """Function fixture to detach volume from server.

    Can be called several times during test.
    """
    def _detach_volume_from_server(server, volume, *args, **kwgs):
        attached_ids = cinder_steps.get_volume_attachment_ids(volume)
        nova_volume_steps.detach_volume_from_server(server, volume,
                                                    *args, **kwgs)
        cinder_steps.check_volume_status(
            volume, 'available', timeout=config.VOLUME_AVAILABLE_TIMEOUT)
        attached_ids.remove(server.id)
        cinder_steps.check_volume_attachments(volume, attached_ids)

    return _detach_volume_from_server
