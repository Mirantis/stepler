"""
Fixtures aggregator.

@author: schipiga@mirantis.com
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
import shutil

import pytest

from .config import TEST_REPORTS_DIR, XVFB_LOCK
from .fixtures import *  # noqa
from .utils import slugify


def pytest_configure(config):
    """Pytest configure hook."""
    if not hasattr(config, 'slaveinput'):
        # on xdist-master node do all the important stuff
        if os.path.exists(TEST_REPORTS_DIR):
            shutil.rmtree(TEST_REPORTS_DIR)
        os.mkdir(TEST_REPORTS_DIR)
        if os.path.exists(XVFB_LOCK):
            os.remove(XVFB_LOCK)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """Pytest hook to delete test report if it is passed."""
    if not hasattr(item, 'is_passed'):
        item.is_passed = True

    outcome = yield
    rep = outcome.get_result()

    if not rep.passed:
        item.is_passed = False

    if rep.when == 'teardown' and item.is_passed:
        shutil.rmtree(os.path.join(TEST_REPORTS_DIR, slugify(item.name)))
