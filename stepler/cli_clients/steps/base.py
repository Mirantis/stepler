"""
---------------------
Base CLI client steps
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

from hamcrest import assert_that, is_  # noqa

from stepler import base
from stepler import config


class BaseCliSteps(base.BaseSteps):
    """Base CLI client steps."""
    def __init__(self, client, openrc_path):
        super(BaseCliSteps, self).__init__(client)
        self.openrc_path = openrc_path

    def execute_command(self,
                        cmd,
                        use_openrc=True,
                        environ=None,
                        timeout=0,
                        check=True):
        """Execute client command in shell.

        Args:
            cmd (str): client command to execute
            use_openrc (bool): add 'source openrc' before `cmd` executing
            environ (dict): shell environment variables to set before `cmd`
                executing. By default it not set any variable
            timeout (int): seconds to wait command executed
            check (bool): flag whether to check result or not

        Returns:
            tuple: (exit_code, stdout, stderr) - result of command execution

        Raises:
            AssertionError: if result check was failed
        """
        if use_openrc:
            source_cmd = config.OPENRC_ACTIVATE_CMD + ";"
            if self.openrc_path:
                source_cmd += " source {};".format(self.openrc_path)
        else:
            source_cmd = ""

        environ = environ or {}
        environ_string = ' '.join("{0}='{1}'".format(*item)
                                  for item in environ.items())
        cmd = u"{source_cmd} {env} {command}".format(source_cmd=source_cmd,
                                                     env=environ_string,
                                                     command=cmd)
        result = self._client(cmd=cmd,
                              timeout=timeout,
                              check=check)
        payload = result[0].payload
        if check:
            assert_that(payload['rc'], is_(0))
        return payload['rc'], payload['stdout'], payload['stderr']
