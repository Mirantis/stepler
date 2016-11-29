"""
------------------------
tcpdump helper unittests
------------------------
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

from stepler.third_party import ssh
from stepler.third_party import tcpdump

docker = pytest.importorskip("docker")

LOG = logging.getLogger(__name__)
IMAGE_TAG = 'test/tcpdump'


@pytest.fixture(scope="session")
def docker_cli():
    return docker.Client('unix:///var/run/docker.sock')


@pytest.fixture(scope="session")
def image(docker_cli):
    with open(
            os.path.join(
                os.path.dirname(__file__), 'tcpdump_files/Dockerfile')) as f:
        for line in docker_cli.build(fileobj=f, tag=IMAGE_TAG):
            LOG.info(line)

    yield IMAGE_TAG
    docker_cli.remove_image(IMAGE_TAG)


@pytest.fixture(scope="session")
def container(docker_cli, image):
    container = docker_cli.create_container(image=image)
    docker_cli.start(container=container.get('Id'))
    yield container
    docker_cli.remove_container(container=container.get('Id'), force=True)


@pytest.fixture(scope="session")
def container_data(container, docker_cli):
    return docker_cli.inspect_container(container=container['Id'])


@pytest.fixture(scope="session")
def remote(container_data):
    with ssh.SshClient(
            container_data['NetworkSettings']['IPAddress'],
            username='user',
            password='screencast') as remote:
        yield remote


@pytest.fixture
def gateway_ip(container_data):
    return container_data['NetworkSettings']['Gateway']


def test_icmp_success(remote, gateway_ip):
    """Test success ping - it should returns 2 packets - request and reply."""
    with tcpdump.tcpdump(remote, args='', proto='icmp') as result:
        remote.check_call('ping -c1 {}'.format(gateway_ip))
    assert len(result) == 2


def test_icmp_wrong_ip(remote):
    """Test wrong ping - it should returns request packet only."""
    with tcpdump.tcpdump(remote, args='', proto='icmp') as result:
        remote.check_call('! ping -c1 192.168.254.254')
    assert len(result) == 1


def test_without_proto(remote, gateway_ip):
    """Test capturing without protocol filtering."""
    with tcpdump.tcpdump(remote, args='') as result:
        remote.check_call('ping -c1 {}'.format(gateway_ip))
    assert len(result) >= 2


def test_get_last_ping_reply_ts(remote, gateway_ip):
    """Test extracting last retrieved ICMP reply timestamp."""
    with tcpdump.tcpdump(remote, args='', proto='icmp') as result:
        remote.check_call('ping -c2 {}'.format(gateway_ip))
    ts = tcpdump.get_last_ping_reply_ts(result)
    last_ts = max(ts for ts, _ in result)
    assert ts == last_ts


def test_get_last_ping_reply_ts_wrong_ip(remote):
    """Negative test extracting last retrieved ICMP reply timestamp."""
    with tcpdump.tcpdump(remote, args='', proto='icmp') as result:
        remote.check_call('! ping -c2 192.168.254.254')
    ts = tcpdump.get_last_ping_reply_ts(result)
    assert ts is None
