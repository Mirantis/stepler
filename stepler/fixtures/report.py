"""
---------------
Report fixtures
---------------
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

import logging
import logging.config
import os

import pytest
import yaml

from stepler import config
from stepler.third_party import utils

__all__ = [
    'report_log',
    'report_dir',
]


@pytest.fixture
def report_dir(request):
    """Create report directory.

    Args:
        request (object): pytest request

    Returns:
        str: path to report directory
    """
    _report_dir = os.path.join(config.TEST_REPORTS_DIR,
                               utils.slugify(request._pyfuncitem.name))

    if not os.path.isdir(_report_dir):
        os.mkdir(_report_dir)

    return _report_dir


@pytest.fixture(autouse=True)
def report_log(report_dir):
    """Configure log handlers to write test logs.

    Args:
        report_dir (str): path to report directory
    """
    with open('./logging.yaml') as file:
        log_content = file.read().format(REPORT_DIR=report_dir)
    logging.config.dictConfig(yaml.safe_load(log_content))
