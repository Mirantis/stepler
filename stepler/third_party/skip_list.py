"""
-------------------------------------
Pytest plugin to skip tests with file
-------------------------------------

Note:

    Skip file should be valid yaml file with format:

    .. code:: yaml

        <idempotent-id>:
            reason: optional reason
            url: optional bug url
        <idempotent-id>:
        <idempotent-id>:

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

import yaml

import pytest

from stepler.third_party import idempotent_id

__all__ = [
    'pytest_addoption',
    'pytest_collection_modifyitems',
]


def pytest_addoption(parser):
    """Add ``--bugs-file`` option to pytest."""
    parser.addoption(
        "--skip-file",
        action="store",
        help="Path to yaml file with skip list.")


def pytest_collection_modifyitems(config, items):
    """Hook to skip tests with opened bugs."""
    if not config.option.skip_file:
        return

    with open(config.option.skip_file) as f:
        to_skip = yaml.load(f)

    for item in items:
        test_id = idempotent_id.get_item_id(item)

        if test_id not in to_skip:
            continue

        skip_info = to_skip[test_id]
        if skip_info is None:
            skip_message = 'Skipped with skip file'
        else:
            skip_message = ('Skipped with skip file. '
                            'Reason: {}. Url: {}').format(
                                skip_info.get('reason'), skip_info.get('url'))
        item.add_marker(pytest.mark.skip(reason=skip_message))
