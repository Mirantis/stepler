"""
---------------------------
Neutron floating ip manager
---------------------------
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

from stepler.neutron.client import base


class FloatingIP(base.Resource):
    pass


class FloatingIPManager(base.BaseNeutronManager):
    """Floating IP (neutron) manager."""

    NAME = 'floatingip'
    _resource_class = FloatingIP

    @base.transform_one
    def create(self, network_id, port_id=None, project_id=None, **kwargs):
        """Create new neutron floating IP.

        Args:
            network_id (str): id of the external network
            port_id (str|None): id of port to create floating ip on it. By
                default created floating ip is not binded to any port.
            project_id (str|None): project id to create floating ip in it. By
                default floating ip will be created on current project.
            **kwargs: other arguments to pass to API

        Returns:
            dict: created floating ip
        """
        kwargs['floating_network_id'] = network_id
        if port_id:
            kwargs['port_id'] = port_id
        if project_id:
            kwargs['tenant_id'] = project_id
        return super(FloatingIPManager, self).create(**kwargs)

    @base.filter_by_project
    def find_all(self, **kwargs):
        return super(FloatingIPManager, self).find_all(**kwargs)
