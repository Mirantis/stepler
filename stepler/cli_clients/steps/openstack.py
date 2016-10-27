from stepler.third_party import steps_checker

from .base import BaseCliSteps


class CliOpenstackSteps(BaseCliSteps):
    """CLI openstack client steps."""

    @steps_checker.step
    def server_list(self, check=True):
        """Step to get server list."""
        cmd = 'openstack server list'
        result = self.execute_command(cmd, timeout=60, check=check)
        return result
