"""
-----------------
Auto use fixtures
-----------------
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
import os

import pytest
import xvfbwrapper

from stepler.horizon.third_party import VideoRecorder, Lock  # noqa

from stepler.horizon import config
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
    _report_dir = os.path.join(config.TEST_REPORTS_DIR,
                               slugify(request._pyfuncitem.name))
    if not os.path.isdir(_report_dir):
        os.mkdir(_report_dir)
    return _report_dir


@pytest.fixture(scope="session")
def virtual_display(request):
    """Run test in virtual X server if env var is defined."""
    if not config.VIRTUAL_DISPLAY:
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

    with Lock(config.XVFB_LOCK):
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
def test_env(virtual_display, get_project_steps, get_user_steps,
             get_role_steps):
    """Fixture to prepare test environment.

    This fixture creates 2 projects, 2 users and grant admin and member roles
    on projects to users.

    Args:
        virtual_display (None): virtual display fixture
        get_project_steps (function): function to get project steps
        get_user_steps (function): function to get user steps
        get_role_steps (function): function to get role steps
    """
    _build_test_env(get_project_steps, get_user_steps,
                    get_role_steps)
    yield
    _destroy_test_env(get_project_steps, get_user_steps)


def _build_test_env(get_project_steps, get_user_steps, get_role_steps):
    project_steps = get_project_steps()
    admin_project = project_steps.create_project(config.ADMIN_PROJECT)
    user_project = project_steps.create_project(config.USER_PROJECT)

    role_steps = get_role_steps()
    admin_role = role_steps.get_role(name="admin")
    member_role = role_steps.get_role(name="_member_")

    user_steps = get_user_steps()
    admin = user_steps.create_user(
        user_name=config.ADMIN_NAME,
        password=config.ADMIN_PASSWD)
    user = user_steps.create_user(
        user_name=config.USER_NAME,
        password=config.USER_PASSWD)
    role_steps.grant_role(admin_role, admin, project=admin_project)
    role_steps.grant_role(member_role, user, project=user_project)


def _destroy_test_env(get_project_steps, get_user_steps):
    user_steps = get_user_steps()
    users = user_steps.get_users()
    for user in users:
        if user.name in [config.ADMIN_NAME, config.USER_NAME]:
            user_steps.delete_user(user)

    project_steps = get_project_steps()
    projects = project_steps.get_projects()
    for project in projects:
        if project.name in [config.ADMIN_PROJECT, config.USER_PROJECT]:
            project_steps.delete_project(project)
