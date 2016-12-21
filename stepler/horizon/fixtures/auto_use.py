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

from stepler import config
from stepler.third_party import process_mutex
from stepler.third_party import utils
from stepler.third_party import video_recorder

__all__ = [
    'logger',
    'report_dir',
    'video_capture',
    'virtual_display',
    'test_env',
]

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def report_dir(request):
    """Create report directory to put test logs."""
    _report_dir = os.path.join(config.TEST_REPORTS_DIR,
                               utils.slugify(request._pyfuncitem.name))
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

    with process_mutex.Lock(config.XVFB_LOCK):
        LOGGER.info('Start xvfb')
        _virtual_display.start()

    def fin():
        LOGGER.info('Stop xvfb')
        _virtual_display.stop()

    request.addfinalizer(fin)


@pytest.fixture
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


@pytest.fixture(autouse=True)
def video_capture(report_dir, logger):
    """Capture video of test."""
    recorder = video_recorder.VideoRecorder(os.path.join(report_dir,
                                                         'video.mp4'))
    recorder.start()
    yield recorder
    recorder.stop()


@pytest.fixture(scope='session')
def test_env(virtual_display,
             resource_manager,
             get_network_steps,
             get_router_steps,
             get_subnet_steps,
             admin_project_resources,
             user_project_resources):
    """Fixture to prepare test environment.

    This fixture creates network with subnet and router for projects
    with admin and member users. Projects with users are created by
    admin_project_resources and user_project_resources fixtures.

    Args:
        virtual_display (None): virtual display fixture
        resource_manager (obj): ProjectResources object
        get_network_steps (function): function to get network steps
        get_router_steps (function): function to get router steps
        get_subnet_steps (function): function to get subnet steps
        admin_project_resources (AttrDict): project with admin user
        user_project_resources (AttrDict): project with member user
    """
    projects_resources = [admin_project_resources, user_project_resources]
    _build_neutron_resources_for_projects(
        resource_manager=resource_manager,
        get_network_steps=get_network_steps,
        get_subnet_steps=get_subnet_steps,
        get_router_steps=get_router_steps,
        projects_resources=projects_resources)

    yield

    _delete_neutron_resources_for_projects(
        resource_manager=resource_manager,
        get_network_steps=get_network_steps,
        get_router_steps=get_router_steps,
        projects_resources=projects_resources
    )


def _build_neutron_resources_for_projects(resource_manager,
                                          get_network_steps,
                                          get_subnet_steps,
                                          get_router_steps,
                                          projects_resources):
    for project_resources in projects_resources:
        with resource_manager.set_current_resources_context(project_resources):
            network_steps = get_network_steps()
            subnet_steps = get_subnet_steps()
            router_steps = get_router_steps()

            int_network = network_steps.create(config.INTERNAL_NETWORK_NAME)
            subnet = subnet_steps.create(config.INTERNAL_SUBNET_NAME,
                                         network=int_network,
                                         cidr="10.0.0.0/24")
            router = router_steps.create(config.ROUTER_NAME)
            external_net = network_steps.get_network_by_name(
                config.FLOATING_NETWORK_NAME)
            router_steps.set_gateway(router, external_net)
            router_steps.add_subnet_interface(router, subnet)


def _delete_neutron_resources_for_projects(resource_manager,
                                           get_network_steps,
                                           get_router_steps,
                                           projects_resources):
    for project_resources in projects_resources:
        with resource_manager.set_current_resources_context(project_resources):
            network_steps = get_network_steps()
            router_steps = get_router_steps()

            router = router_steps.get_router(
                name=config.ROUTER_NAME,
                tenant_id=project_resources.project.id)
            router_steps.delete(router)

            network = network_steps.get_network_by_name(
                config.INTERNAL_NETWORK_NAME,
                tenant_id=project_resources.project.id)
            network_steps.delete(network)
