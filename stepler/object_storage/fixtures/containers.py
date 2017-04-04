"""
---------------------------------
Object Storage container fixtures
---------------------------------
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
import boto3
import pytest
from six.moves.urllib.parse import urlparse

from stepler import config
from stepler.object_storage import steps as object_storage_steps
from stepler.third_party import utils

__all__ = [
    's3_client',
    'container_steps',
    'container',
]


@pytest.fixture
def s3_client(current_user, ec2_credentials):
    """Fixture to get s3 client.

    Args:
        current_user (obj): current user
        ec2_credentials (obj): EC2 credentials for current user

    Returns:
        obj: s3 client
    """
    auth_url = urlparse(config.AUTH_URL)
    net_ip = auth_url.netloc.rsplit(':')[0]
    endpoint_url = '{}://{}'.format(auth_url.scheme, net_ip)
    s3 = boto3.client('s3',
                      aws_access_key_id=ec2_credentials.access,
                      aws_secret_access_key=ec2_credentials.secret,
                      endpoint_url='{}:{}'.format(endpoint_url,
                                                  config.S3_PORT))
    return s3


@pytest.fixture
def container_steps(swift_client, os_faults_steps, s3_client):
    """Fixture to get swift container steps.

    Args:
        swift_client (obj): instantiated swift client
        os_faults_steps (obj): instantiated os_faults steps
        s3_client (obj): s3 client

    Returns:
        object: instantiated swift or rbd container steps
    """
    if os_faults_steps.get_default_glance_backend() == "swift":
        return object_storage_steps.ContainerSwiftSteps(swift_client)
    else:
        return object_storage_steps.ContainerCephSteps(s3_client)


@pytest.fixture
def container(container_steps):
    """Fixture to create container.

    Args:
        container_steps (obj): instantiated container steps

    Yields:
        attrdict.AttrDict: created container name and info
    """
    name, = utils.generate_ids()
    container = container_steps.create(name)
    yield attrdict.AttrDict(name=name, info=container)

    container_steps.delete(name)
