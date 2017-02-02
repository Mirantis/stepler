"""
--------------------------
Openstack CLI client steps
--------------------------
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

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliOpenstackSteps(base.BaseCliSteps):
    """CLI openstack client steps."""

    @steps_checker.step
    def server_list(self, check=True):
        """Step to get server list.

        Args:
            check (bool): flag whether to check result or not

        Returns:
            str: result of command shell execution

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'openstack server list'
        result = self.execute_command(
            cmd, timeout=config.SERVER_LIST_TIMEOUT, check=check)
        return result

    @steps_checker.step
    def baremetal_node_list(self, check=True):
        """Step to get baremetal node list.

        Args:
            check (bool): flag whether to check result or not

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'openstack baremetal list'
        self.execute_command(cmd,
                             timeout=config.SERVER_LIST_TIMEOUT,
                             check=check)

    @steps_checker.step
    def ec2_creds_create(self, check=True):
        """Step to create ec2 creds.

        Args:
            check (bool): flag whether to check result or not

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'openstack ec2 credentials create'
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.SERVER_LIST_TIMEOUT, check=check)
        if check:
            creds_table = output_parser.table(stdout)['values']
            creds = {line[0]: line[1] for line in creds_table}
            return creds
