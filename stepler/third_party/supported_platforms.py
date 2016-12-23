"""
--------------------------------------------------------
Pytest plugin to mark and choose platform-specific tests
--------------------------------------------------------

Usage example:

.. code:: python

    from stepler.third_party.supported_platforms import platform

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

import attrdict
import pytest

__all__ = [
    'platform',
    'pytest_addoption',
    'pytest_collection_modifyitems',
]

PLATFORMS = [
    'mos10',
    'mk2x',
    'mcp',
]

platform = attrdict.AttrDict(
    {name: pytest.mark.platform(name) for name in PLATFORMS})


def pytest_addoption(parser):
    """Add option ``--platform`` to choose platform-specific tests."""
    parser.addoption('--platform', action='store', choices=PLATFORMS,
                     help='Use this option to choose platform-specific tests.')


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, items):
    """Skip tests for unspecified platforms.

    Notes:
        - If platform isn't specified, only common tests will be executed.
        - If platform is specified, common tests with platform-specific tests
          will be executed.
    """
    specified_platform = session.config.option.platform
    for item in items:

        marker = item.get_marker('platform')
        if not marker:
            continue  # non-platform-specific test is launched in any case

        test_platforms = marker.args
        if specified_platform not in test_platforms:
            skip_msg = ('Test is only for platform(s): ' +
                        ', '.join(test_platforms))
            item.add_marker(pytest.mark.skip(reason=skip_msg))
