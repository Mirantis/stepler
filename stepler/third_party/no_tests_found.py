"""
----------------------------------------------------------------
Pytest plugin to show output error message if no tests are found
----------------------------------------------------------------

It shows error message in stdout if no tests are found according to input
parameters. For example::

    No tests are found matching input parameters: keyword expression
    'test1 and not test2', mark expression 'destructive'.
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

__all__ = [
    'pytest_collection_modifyitems',
]


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Hook to show error message if no tests are found."""
    if not items:
        keyword = config.option.keyword
        markexpr = config.option.markexpr

        msg = 'No tests are found matching input parameters:'
        if keyword:
            msg += ' keyword expression {!r},'.format(keyword)
        if markexpr:
            msg += ' mark expression {!r}'.format(markexpr)
        msg = msg.rstrip(':,') + '.'

        config.get_terminal_writer().write(msg, red=True, bold=True)
