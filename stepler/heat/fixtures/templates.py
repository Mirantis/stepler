"""
---------------------------
Fixtures for heat templates
---------------------------
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

__all__ = [
    'read_heat_template',
]


@pytest.fixture(scope='session')
def read_heat_template():
    """Function fixture to read template from stepler/heat/templates folder.

    Can be called several times during a test.

    Returns:
        function: function to read template
    """
    def _read_template(name):
        filename = "{}/{}.yaml".format(template_dir, name)
        with open(filename) as f:
            return f.read()

    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    return _read_template
