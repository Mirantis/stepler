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


class SecurityGroupRule(base.Resource):
    pass


class SecurityGroupRuleManager(base.BaseNeutronManager):
    """Security group rule manager."""

    NAME = 'security_group_rule'
    _resource_class = SecurityGroupRule
