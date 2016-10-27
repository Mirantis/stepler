from stepler.third_party import steps_checker

from .base import BaseCliSteps


class CliOpenstackSteps(BaseCliSteps):
    """CLI openstack client steps."""

    @steps_checker.step
    def server_list(self, check=True):
        """Step to get server list.

        Args:
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution

        Raises:
            AssertionError: if check was failed
        """
        cmd = 'openstack server list'
        result = self.execute_command(cmd, timeout=60, check=check)
        return result
