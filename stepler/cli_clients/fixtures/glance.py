"""
--------------------------
Glance CLI client fixtures
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

import os
import pytest


from stepler.cli_clients import steps

__all__ = [
    'cli_glance_steps',
]


@pytest.fixture
def cli_glance_steps(remote_executor):
    """Function fixture to glance CLI steps.

    Returns:
        CliGlanceSteps: instantiated glance CLI steps
    """
    return steps.CliGlanceSteps(remote_executor)


@pytest.fixture
def delete_file(name_file):
    """Step to delete file.

    """
    if os.path.exists(name_file) is True:
        os.remove(name_file)
    else:
        return False
