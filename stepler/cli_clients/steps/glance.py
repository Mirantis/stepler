"""
-----------------------
Glance CLI client steps
-----------------------
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

from hamcrest import assert_that, contains_string  # noqa

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import steps_checker


class CliGlanceSteps(base.BaseCliSteps):
    """CLI glance client steps."""

    @steps_checker.step
    def check_negative_image_create_without_properties(self, file,
                                                       api_version=1):
        """Step to get glance image list."""

        cmd = 'glance image-create --file {0}'.format(file)
        error_message = ("Must provide --container-format, "
                         "--disk-format when using --file.")
        exit_code, stdout, stderr = self.execute_command(
            cmd, environ={'OS_IMAGE_API_VERSION': api_version},
            should_pass=False)

        assert_that(stderr, contains_string(error_message))
