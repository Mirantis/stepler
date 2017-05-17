"""
---------------------------------
Neutron LBaaS pool member manager
---------------------------------
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

import functools

from stepler.neutron.client import base


class Member(base.Resource):
    pass


class MemberManager(base.BaseNeutronManager):
    """LBaaS pool member manager."""

    NAME = "member"
    API_NAME = 'lbaas_member'
    _resource_class = Member

    def __init__(self, client, pool_id):
        super(MemberManager, self).__init__(client)
        self.pool_id = pool_id

    @property
    def _create_method(self):
        """Returns resource create callable."""
        return functools.partial(
            super(MemberManager, self)._create_method, self.pool_id)

    @property
    def _delete_method(self):
        """Returns resource delete callable."""
        return functools.partial(
            super(MemberManager, self)._delete_method, self.pool_id)

    @property
    def _list_method(self):
        """Returns resource list callable."""
        return functools.partial(
            super(MemberManager, self)._list_method, self.pool_id)

    @property
    def _show_method(self):
        """Returns resource show callable."""
        return functools.partial(
            super(MemberManager, self)._show_method, self.pool_id)

    @property
    def _update_method(self):
        """Returns resource update callable."""
        return functools.partial(
            super(MemberManager, self)._update_method, self.pool_id)

    @base.filter_by_project
    def find_all(self, **kwargs):
        return super(MemberManager, self).find_all(**kwargs)
