"""
Role steps.

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

from waiting import wait

from stepler.steps import BaseSteps, step

__all__ = [
    'RoleSteps'
]


class RoleSteps(BaseSteps):
    """Role steps."""

    @step
    def create_role(self, role_name, check=True):
        """Step to create role."""
        role = self._client.create(role_name)

        if check:
            self.check_role_presence(role)
        return role

    @step
    def delete_role(self, role, check=True):
        """Step to delete role."""
        self._client.delete(role.id)
        if check:
            self.check_role_presence(role, present=False)

    @step
    def find_role(self, *args, **kwgs):
        """Step to find role."""
        return self._client.find(*args, **kwgs)

    @step
    def grant_role(self, role, user=None, group=None, domain=None,
                   project=None, check=True):
        """Step to grant role to user or group on domain or project."""
        self._client.grant(role, user=user, group=group, domain=domain,
                           project=project)
        if check:
            self.check_role_grant_status(role, user=user, group=group,
                                         domain=domain, project=project)

    @step
    def revoke_role(self, role, user=None, group=None, domain=None,
                    project=None, check=True):
        """Step to revoke role from user or group on domain or project."""
        self._client.revoke(role, user=user, group=group, domain=domain,
                            project=project)
        if check:
            self.check_role_grant_status(role, user=user, project=project,
                                         group=group, domain=domain,
                                         granted=False)

    @step
    def check_role_presence(self, role, present=True, timeout=0):
        """Check step that role is present."""
        def predicate():
            try:
                self._client.get(role.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def check_role_grant_status(self, role, user=None, group=None, domain=None,
                                project=None, granted=True, timeout=0):
        """Check step if a user or group has a role on a domain or project."""
        def predicate():
            try:
                self._client.check(role, user=user, group=group, domain=domain,
                                   project=project)
                return granted
            except Exception:
                return not granted

        wait(predicate, timeout_seconds=timeout)
