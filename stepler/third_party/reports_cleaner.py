"""
----------------------
Pytest plugin to clean test reports
----------------------

It ensures two things:

* Remove test reports folder before tests launching
* Remove test report folder if test is passed

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
# limitations under the License.from functools import wraps

import os
import shutil

import pytest

from stepler import config as stepler_config
from stepler import logging_config
from stepler.third_party import utils

__all__ = [
    'pytest_configure',
    'pytest_runtest_makereport',
]


def pytest_configure(config):
    """Pytest hook to remove test reports before tests launching."""
    if not hasattr(config, 'slaveinput'):  # if it is not xdist slave node
        if os.path.isdir(stepler_config.TEST_REPORTS_DIR):
            for name in os.listdir(stepler_config.TEST_REPORTS_DIR):
                path = os.path.join(stepler_config.TEST_REPORTS_DIR, name)
                if (os.path.isfile(path) and
                        path != logging_config.LOG_FILE_PATH):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        else:
            os.mkdir(stepler_config.TEST_REPORTS_DIR)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """Pytest hook to remove test report if test is passed."""
    if not hasattr(item, 'is_passed'):
        item.is_passed = True  # mark test as passed by default

    outcome = yield
    rep = outcome.get_result()

    if not rep.passed:
        item.is_passed = False  # test was failed in some stage

    if rep.when == 'teardown' and item.is_passed:
        report_dir = os.path.join(stepler_config.TEST_REPORTS_DIR,
                                  utils.slugify(item.name))

        if os.path.isdir(report_dir):
            shutil.rmtree(report_dir)
