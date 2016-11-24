"""
----------------------
Ironic node API client
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

from stepler.base import Resource

from .base import IronicApiClient


class IronicApiClientV1(IronicApiClient):
    """Ironic node API client."""

    def node_list(self):
        """Get nodes list via API call.

        Returns:
            list of objects: list of nodes.
        """
        response = self._get('/v1/nodes/')
        response.raise_for_status()

        nodes = [Resource(self, node_dict)
                 for node_dict in response.json()['nodes']]
        return nodes

    def node_get(self, node_ident):
        """Get node via API call.

        Args:
            node_ident (str): the UUID or Name of the node.

        Returns:
            object: ironic node
        """
        response = self._get('/v1/nodes/{}'.format(node_ident))
        response.raise_for_status()

        return [Resource(self, response.json())]

    def node_create(self, driver, name=None, driver_info=None):
        """Create node via API call.

        Args:
            name(str): node name
            driver(str): node driver
            driver_info(json): node driver info

        Returns:
            object: ironic node
        """
        data = {"name": name,
                "driver": driver,
                "driver_info": driver_info}

        response = self._post('/v1/nodes/', json=data)
        response.raise_for_status()

        return Resource(self, response.json())

    def node_delete(self, node_ident):
        """Delete node via API call.

        Args:
            node_ident (str): the UUID or Name of the node.
        """
        response = self._delete('/v1/nodes/{}'.format(node_ident))
        response.raise_for_status()
