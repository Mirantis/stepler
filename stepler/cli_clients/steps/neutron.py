"""
------------------------
Neutron CLI client steps
------------------------
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

from hamcrest import assert_that, contains_string, empty, is_not  # noqa H301
from six import moves

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker
from stepler.third_party import utils


class CliNeutronSteps(base.BaseCliSteps):
    """CLI neutron client steps."""

    @steps_checker.step
    def create_router(self,
                      name=None,
                      project=None,
                      username=None,
                      password=None,
                      distributed=None,
                      expected_error=False,
                      check=True):
        """Step to create router using CLI.

        Args:
            name (str): name of created router
            project (str): name of the project
            username (str): user name
            password (str): user password
            distributed (bool): flag whether to create DVR or not
            expected_error (bool): flag whether to expect error during
                router creation or not
            check (bool): flag whether to check step or not

        Returns:
            tuple: (router or None, exit_code, stdout, stderr)
        """
        name = name or next(utils.generate_ids())
        router = None
        cmd = 'neutron router-create ' + moves.shlex_quote(name)

        if project:
            cmd += ' --os-project-name ' + project
        if username and password:
            cmd += ' --os-username {0} --os-password {1}'.format(username,
                                                                 password)
        if distributed is not None:
            cmd += ' --distributed ' + str(distributed)

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.ROUTER_AVAILABLE_TIMEOUT, check=check)

        if not expected_error:
            router_table = output_parser.table(stdout)
            router = {key: value for key, value in router_table['values']}
            if check:
                assert_that(router, is_not(empty()))

        return router, exit_code, stdout, stderr

    @steps_checker.step
    def check_negative_router_create_with_distributed_option(
            self, project, username, password, distributed, name=None):
        """Step to check that router is not created with distributed option.

        In case of creation of the router with explicit distributed option
        by user with member role this creation should be prohibited by policy.

        Args:
            project (str): name of the project
            username (str): user name
            password (str): user password
            distributed (bool): flag whether to create DVR or not
            name (str): name of created router

        Raises:
            AssertionError: if command exit code is 0 or stderr doesn't
                contain expected message
        """
        name = name or next(utils.generate_ids())
        message = "disallowed by policy"
        router, exit_code, stdout, stderr = self.create_router(
            name,
            project=project,
            username=username,
            password=password,
            distributed=distributed,
            expected_error=True,
            check=False)
        assert_that(exit_code, is_not(0))
        assert_that(stderr, contains_string(message))
