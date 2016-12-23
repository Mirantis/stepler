"""
--------------------------------------------------------
Pytest plugin to mark and choose platform-specific tests
--------------------------------------------------------

Usage example:

.. code:: python

    from stepler.third_party import platform

    @platform.mos10
    def test_something():
        pass

Launching example::

    py.test stepler --platform mos10

Supported platforms are ``mos10``, ``mk2x``, ``mcp``, ``tcp``.
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

import pytest

PLATFORMS = [
    'mos10',
    'mk2x',
    'mcp',
    'tcp',
]


def pytest_addoption(parser):
    """Add option ``--platform`` to choose platform-specific tests."""
    parser.addoption('--platform', action='store', choices=PLATFORMS,
                     help='Use this option to choose platform-specific tests.')


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, items):
    """Reject tests for unspecified platforms.

    Notes:
        - If platform isn't specified, only common tests will be executed.
        - If platform is specified, common tests + platform-specific tests will
          be executed.
    """
    specified_platform = session.config.option.platform
    for item in items[:]:

        markers = item.get_marker('platform')
        if not markers:
            continue  # non-platform-specific test is launched in any case

        for requested_platform in [m.args[0] for m in markers]:
            if requested_platform == specified_platform:
                break
        else:
            items.remove(item)


for _name in PLATFORMS:
    globals()[_name] = pytest.mark.platform(_name)
del _name
