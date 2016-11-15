"""
---------------------
Nova CLI client steps
---------------------
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

from hamcrest import assert_that, empty, equal_to, is_not  # noqa H301

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliNovaSteps(base.BaseCliSteps):
    """CLI nova client steps."""

    @steps_checker.step
    def nova_list(self, api_version=None, check=True):
        """Step to get nova list.

        Args:
            api_version (str|None): micro version for nova list command
            check (bool): flag whether to check result or not

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        cmd = 'nova'
        if api_version:
            cmd += ' --os-compute-api-version ' + api_version
        cmd += ' list'

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.SERVER_LIST_TIMEOUT, check=check)

        if check:
            list_result = output_parser.listing(stdout)
            assert_that(list_result, is_not(empty()))

    @steps_checker.step
    def live_evacuate(self, source_host, target_host, servers, check=True):
        """Step to execute host-evacuate-live.

        This step is executed using CLI because there is no API for it.

        Args:
            source_host (str): source host
            target_host (str): target host
            servers (list): list of server objects
            check (bool): flag whether to check result or not

        Raises:
            AssertionError: if check failed
        """
        cmd = ('nova host-evacuate-live --target-host {0} --block-migrate {1}'.
               format(target_host, source_host))
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.LIVE_EVACUATE_CLI_TIMEOUT, check=check)

        if check:
            evacuation_table = output_parser.table(stdout)
            ids = []
            for id, accepted, err_message in evacuation_table['values']:
                ids.append(id)
                assert_that(accepted, equal_to('True'))
                assert_that(err_message, equal_to(''))
            server_ids = [server.id for server in servers]
            assert_that(sorted(ids), equal_to(sorted(server_ids)))
