"""
Auto use fixtures.

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

import contextlib
import logging
import os

import pytest
import xvfbwrapper

from stepler.horizon.app import Horizon
from stepler.horizon.steps import (AuthSteps,
                                   ProjectsSteps,
                                   NetworksSteps,
                                   UsersSteps)
from stepler.horizon.third_party import VideoRecorder, Lock

from stepler.horizon.config import (ADMIN_NAME,
                                    ADMIN_PASSWD,
                                    ADMIN_PROJECT,
                                    DASHBOARD_URL,
                                    DEFAULT_ADMIN_NAME,
                                    DEFAULT_ADMIN_PASSWD,
                                    DEFAULT_ADMIN_PROJECT,
                                    FLOATING_NETWORK_NAME,
                                    INTERNAL_NETWORK_NAME,
                                    TEST_REPORTS_DIR,
                                    USER_NAME,
                                    USER_PASSWD,
                                    USER_PROJECT,
                                    VIRTUAL_DISPLAY,
                                    XVFB_LOCK)
from stepler.horizon.utils import slugify

__all__ = [
    'logger',
    'report_dir',
    'video_capture',
    'virtual_display',
    'test_env'
]

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def report_dir(request):
    """Create report directory to put test logs."""
    _report_dir = os.path.join(TEST_REPORTS_DIR,
                               slugify(request._pyfuncitem.name))
    if not os.path.isdir(_report_dir):
        os.mkdir(_report_dir)
    return _report_dir


@pytest.fixture(scope="session")
def virtual_display(request):
    """Run test in virtual X server if env var is defined."""
    if not VIRTUAL_DISPLAY:
        return

    _virtual_display = xvfbwrapper.Xvfb(width=1920, height=1080)
    # workaround for memory leak in Xvfb taken from:
    # http://blog.jeffterrace.com/2012/07/xvfb-memory-leak-workaround.html
    # and disables X access control
    args = ["-noreset", "-ac"]

    if hasattr(_virtual_display, 'extra_xvfb_args'):
        _virtual_display.extra_xvfb_args.extend(args)  # xvfbwrapper>=0.2.8
    else:
        _virtual_display.xvfb_cmd.extend(args)

    with Lock(XVFB_LOCK):
        LOGGER.info('Start xvfb')
        _virtual_display.start()

    def fin():
        LOGGER.info('Stop xvfb')
        _virtual_display.stop()

    request.addfinalizer(fin)


@pytest.yield_fixture
def logger(report_dir, test_env):
    """Fixture to put test log in report."""
    class RootFilter(logging.Filter):

        def filter(self, record):
            return record.name not in \
                ('timeit', 'selenium.webdriver.remote.remote_connection')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_handler = logging.FileHandler(
        os.path.join(report_dir, 'test.log'))
    root_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(pathname)s#%(lineno)d - %(message)s')
    root_handler.setFormatter(root_formatter)
    root_handler.addFilter(RootFilter())
    root_logger.addHandler(root_handler)

    timeit_logger = logging.getLogger('timeit')
    timeit_logger.setLevel(logging.DEBUG)
    timeit_handler = logging.FileHandler(
        os.path.join(report_dir, 'timeit.log'))
    timeit_handler.setLevel(logging.DEBUG)

    remote_logger = logging.getLogger(
        'selenium.webdriver.remote.remote_connection')
    remote_logger.setLevel(logging.DEBUG)
    remote_handler = logging.FileHandler(
        os.path.join(report_dir, 'remote_connection.log'))
    remote_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(message)s')

    timeit_handler.setFormatter(formatter)
    timeit_logger.addHandler(timeit_handler)

    remote_handler.setFormatter(formatter)
    remote_logger.addHandler(remote_handler)

    yield

    timeit_logger.handlers.remove(timeit_handler)
    remote_logger.handlers.remove(remote_handler)
    root_logger.handlers.remove(root_handler)


@pytest.yield_fixture(autouse=True)
def video_capture(report_dir, logger):
    """Capture video of test."""
    recorder = VideoRecorder(os.path.join(report_dir, 'video.mp4'))
    recorder.start()
    yield recorder
    recorder.stop()


@pytest.yield_fixture(scope='session')
def test_env(request, virtual_display):
    """Fixture to prepare test environment."""
    test_name = slugify(request._pyfuncitem.name)
    _build_test_env(test_name)
    yield
    _destroy_test_env(test_name)


def _build_test_env(test_name):
    file_path = os.path.join(TEST_REPORTS_DIR,
                             'build_env_{}.mp4'.format(test_name))
    recorder = VideoRecorder(file_path)
    recorder.start()

    app = Horizon(DASHBOARD_URL)
    try:
        auth_steps = AuthSteps(app)
        auth_steps.login(DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASSWD)
        auth_steps.switch_project(DEFAULT_ADMIN_PROJECT)

        projects_steps = ProjectsSteps(app)
        projects_steps.create_project(ADMIN_PROJECT)
        projects_steps.create_project(USER_PROJECT)

        users_steps = UsersSteps(app)
        users_steps.create_user(ADMIN_NAME, ADMIN_PASSWD, ADMIN_PROJECT,
                                role='admin')
        users_steps.create_user(USER_NAME, USER_PASSWD, USER_PROJECT)

        # networks_steps = NetworksSteps(app)
        # networks_steps.admin_update_network(INTERNAL_NETWORK_NAME,
        #                                     shared=True, check=False)
        # networks_steps.admin_update_network(FLOATING_NETWORK_NAME,
        #                                     shared=True, check=False)

        auth_steps.logout()
    finally:
        app.quit()
        recorder.stop()


@contextlib.contextmanager
def _try_delete(resource_name):
    try:
        yield
    except Exception:
        LOGGER.error("Can't delete resource {!r}".format(resource_name))


def _destroy_test_env(test_name):
    file_path = os.path.join(TEST_REPORTS_DIR,
                             'destroy_env_{}.mp4'.format(test_name))
    recorder = VideoRecorder(file_path)
    recorder.start()

    app = Horizon(DASHBOARD_URL)
    try:
        auth_steps = AuthSteps(app)
        auth_steps.login(DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASSWD)
        auth_steps.switch_project(DEFAULT_ADMIN_PROJECT)

        users_steps = UsersSteps(app)
        with _try_delete(USER_NAME):
            users_steps.filter_users(USER_NAME)
            users_steps.delete_user(USER_NAME)
        with _try_delete(ADMIN_NAME):
            users_steps.filter_users(ADMIN_NAME)
            users_steps.delete_user(ADMIN_NAME)

        projects_steps = ProjectsSteps(app)
        with _try_delete(USER_PROJECT):
            projects_steps.filter_projects(USER_PROJECT)
            projects_steps.delete_project(USER_PROJECT)
        with _try_delete(ADMIN_PROJECT):
            projects_steps.filter_projects(ADMIN_PROJECT)
            projects_steps.delete_project(ADMIN_PROJECT)

        auth_steps.logout()
    finally:
        app.quit()
        recorder.stop()
