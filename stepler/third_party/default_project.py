"""
----------------------------------------------------------------
Pytest plugin to use default project instead of creation new one
----------------------------------------------------------------
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

__all__ = [
    'pytest_addoption',
    'pytest_configure',
]


def pytest_addoption(parser):
    """Add ``--use-default-project`` option to pytest."""
    parser.addoption("--use-default-project", action="store_true",
                     help="Use current project for tests running or "
                          "create new admin project.")


def pytest_configure(config):
    if not config.option.use_default_project:
        config.addinivalue_line('usefixtures', 'admin_project_resources')
