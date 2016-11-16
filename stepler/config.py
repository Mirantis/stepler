"""
------
Config
------
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
import socket
import uuid

import stepler.hacking  # noqa F401

socket.setdefaulttimeout(60)

DEBUG = bool(os.environ.get('DEBUG', False))

PROJECT_DOMAIN_NAME = os.environ.get('OS_PROJECT_DOMAIN_NAME', 'default')
USER_DOMAIN_NAME = os.environ.get('OS_USER_DOMAIN_NAME', 'default')
PROJECT_NAME = os.environ.get('OS_PROJECT_NAME', 'admin')
USERNAME = os.environ.get('OS_USERNAME', 'admin')
PASSWORD = os.environ.get('OS_PASSWORD', 'password')
OS_FAULTS_CONFIG = os.environ.get('OS_FAULTS_CONFIG')  # should be defined!

# If AUTH_URL is undefined, corresponding fixture raises exception.
# AUTH_URL absence doesn't raise exception here, because for docs generation
# and unittests launching this variable doesn't need.
AUTH_URL = os.environ.get('OS_AUTH_URL')

if AUTH_URL:  # figure out keystone API version
    AUTH_URL = AUTH_URL.rstrip('/')  # remove last slash if it is present
    version = AUTH_URL.rsplit('/')[-1]

    versions = ('v2.0', 'v3')
    assert version in versions, \
        "OS_AUTH_URL must have tail among values {!r}.".format(versions)

    KEYSTONE_API_VERSION = 3 if version == 'v3' else 2

UBUNTU_QCOW2_URL = 'https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img'  # noqa E501
UBUNTU_XENIAL_QCOW2_URL = 'https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img'  # noqa E501
FEDORA_QCOW2_URL = 'https://download.fedoraproject.org/pub/fedora/linux/releases/23/Cloud/x86_64/Images/Fedora-Cloud-Base-23-20151030.x86_64.qcow2'  # noqa E501
CIRROS_QCOW2_URL = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'  # noqa E501
UBUNTU_ISO_URL = 'http://archive.ubuntu.com/ubuntu/dists/trusty/main/installer-amd64/current/images/netboot/mini.iso'  # noqa E501
BAREMETAL_UBUNTU = 'http://mos-ironic.vm.mirantis.net/ipukha/dib-user-image-dkms-grub.raw'  # noqa E501

# TODO(schipiga): copied from mos-integration-tests, need refactor.
TEST_IMAGE_PATH = os.environ.get("TEST_IMAGE_PATH", os.path.expanduser('~/images'))  # noqa E501

TEST_REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../test_reports'))

STEPLER_PREFIX = 'stepler-' + str(uuid.uuid4())[:8]  # resources unique prefix

# IMAGE / SERVER CREDENTIALS
CIRROS_USERNAME = 'cirros'
UBUNTU_USERNAME = 'ubuntu'

# CURRENT API VERSIONS
CURRENT_GLANCE_VERSION = '2'
CURRENT_CINDER_VERSION = '2'
CURRENT_IRONIC_VERSION = '1'

# SERVICES
CINDER_VOLUME = 'cinder-volume'
KEYSTONE = 'keystone'
NOVA_API = 'nova-api'
NOVA_COMPUTE = 'nova-compute'

# STATUSES
STATUS_ACTIVE = 'active'
STATUS_AVAILABLE = 'available'
STATUS_AWAITING_TRANSFER = 'awaiting-transfer'
STATUS_BUILD = 'build'
STATUS_CREATING = 'creating'
STATUS_DOWNLOADING = 'downloading'
STATUS_INUSE = 'in-use'
STATUS_MIGRATING = 'migrating'
STATUS_OK = 'OK'
STATUS_FAILED = 'FAILED'
STATUS_RESIZE = 'resize'
STATUS_SOFT_DELETED = 'soft_deleted'
STATUS_SUCCESS = 'success'
STATUS_VERIFY_RESIZE = 'verify_resize'
STATUS_UPLOADING = 'uploading'
STATUS_REBUILDING = 'rebuilding'
STATUS_REBUILD_SPAWNING = 'rebuild_spawning'
STATUS_PAUSED = 'paused'
STATUS_PAUSING = 'pausing'
STATUS_RESCUE = 'rescue'
STATUS_RESCUING = 'rescuing'
STATUS_QUEUED = 'queued'

# TIMEOUTS (in seconds)
# TODO(kromanenko): Investigate less intensive good polling interval value.
POLLING_TIME = 1

# Cinder
VOLUME_AVAILABLE_TIMEOUT = 5 * 60
VOLUME_DELETE_TIMEOUT = 3 * 60
VOLUME_IN_USE_TIMEOUT = 60
VOLUME_ATTACH_TIMEOUT = 60
SNAPSHOT_AVAILABLE_TIMEOUT = 5 * 60
SNAPSHOT_SHOW_TIMEOUT = 60
SNAPSHOT_DELETE_TIMEOUT = 3 * 60
VOLUME_RETYPE_TIMEOUT = 60
CINDER_VOLUME_MAX_SIZE_QUOTA_VALUE = 20
CINDER_SNAPSHOTS_QUOTA_BIG_VALUE = 200
POLICY_NEVER = 'never'
VOLUME_HOST_ATTR = 'os-vol-host-attr:host'
VOLUME_HOST_POSTFIX = '@LVM-backend#LVM-backend'
BACKUP_AVAILABLE_TIMEOUT = 5 * 60
BACKUP_SHOW_TIMEOUT = 60
BACKUP_DELETE_TIMEOUT = 3 * 60
TRANSFER_CREATE_TIMEOUT = 3 * 60
TRANSFER_SHOW_TIMEOUT = 60

# Glance
IMAGE_AVAILABLE_TIMEOUT = 5 * 60
IMAGE_QUEUED_TIMEOUT = 30
BAREMETAL_DISK_INFO = [{"name": "sda",
                        "extra": [],
                        "free_space": 11000,
                        "type": "disk",
                        "id": "sda",
                        "size": 11000,
                        "volumes": [{"mount": "/",
                                     "type": "partition",
                                     "file_system": "ext4",
                                     "size": 10000}]}]


# Nova
CREDENTIALS_PREFIX = 'stepler_credentials_'
ROOT_DISK_TIMESTAMP_FILE = '/timestamp.txt'
EPHEMERAL_DISK_TIMESTAMP_FILE = '/mnt/timestamp.txt'
NOVA_API_LOG_FILE = '/var/log/nova/nova-api.log'
NOVA_CONFIG_PATH = '/etc/nova/nova.conf'

FLAVOR_TINY = 'm1.tiny'
FLAVOR_SMALL = 'm1.small'
BAREMETAL_RAM = "16384"
BAREMETAL_VCPUS = "4"
BAREMETAL_DISK = "150"

ROLE_MEMBER = '_member_'

PING_CALL_TIMEOUT = 5 * 60
PING_BETWEEN_SERVERS_TIMEOUT = 5 * 60
USERDATA_EXECUTING_TIMEOUT = 5 * 60
SSH_CLIENT_TIMEOUT = 60
SSH_CONNECT_TIMEOUT = 8 * 60
LIVE_MIGRATE_TIMEOUT = 5 * 60
LIVE_MIGRATION_PING_MAX_LOSS = 20
VERIFY_RESIZE_TIMEOUT = 3 * 60
SOFT_DELETED_TIMEOUT = 30
SERVER_DELETE_TIMEOUT = 3 * 60
SERVER_ACTIVE_TIMEOUT = 10 * 60
SERVER_UPDATE_TIMEOUT = 2 * 60

NOVA_AVAILABILITY_TIMEOUT = 2 * 60

USERDATA_DONE_MARKER = 'userdata-done %s' % uuid.uuid4()

INSTALL_LM_WORKLOAD_USERDATA = """#!/bin/bash -v
apt-get install -yq stress cpulimit sysstat iperf
echo {}""".format(USERDATA_DONE_MARKER)
SMALL_RECLAIM_INTERVAL = str(30)
BIG_RECLAIM_INTERVAL = str(24 * 60 * 60)
SMALL_RECLAIM_TIMEOUT = 3 * int(SMALL_RECLAIM_INTERVAL)
NOVA_INSTANCES_PATH = "/var/lib/nova/instances/"

# Heat
HEAT_VERSION = 1
HEAT_IN_PROGRESS_STATUS = 'in_progress'
HEAT_COMPLETE_STATUS = 'complete'
STACK_STATUS_CREATE_COMPLETE = 'create_complete'
STACK_STATUS_UPDATE_COMPLETE = 'update_complete'
STACK_STATUS_SUSPEND_COMPLETE = 'suspend_complete'
STACK_STATUS_RESUME_COMPLETE = 'resume_complete'
STACK_STATUS_CHECK_COMPLETE = 'check_complete'
STACK_CREATION_TIMEOUT = 5 * 60
STACK_DELETING_TIMEOUT = 3 * 60
STACK_UPDATING_TIMEOUT = 5 * 60
STACK_PREVIEW_TIMEOUT = 60
STACK_SHOW_TIMEOUT = 60
STACK_SUSPEND_TIMEOUT = 60
STACK_RESUME_TIMEOUT = 60
STACK_CHECK_TIMEOUT = 3 * 60
STACK_CLI_TIMEOUT = 60
RESOURCE_NAME = 'stepler_cirros_image'
HEAT_SIMPLE_TEMPLATE_URL = 'https://raw.githubusercontent.com/openstack/heat-templates/master/hot/resource_group/resource_group.yaml'  # noqa

# Ironic
BAREMETAL_NETWORK = 'baremetal'

# CLI clients
SERVER_LIST_TIMEOUT = 60
MIGRATION_START_TIMEOUT = 15
LIVE_EVACUATE_CLI_TIMEOUT = 60
LIVE_EVACUATE_TIMEOUT = 5 * 60
IMAGE_CREATION_TIMEOUT = 60

# For DevStack cmd should looks like `source devstack/openrc admin admin`
OPENRC_ACTIVATE_CMD = os.environ.get('OPENRC_ACTIVATE_CMD', 'source /root/openrc')  # noqa E501


CLEANUP_UNEXPECTED_BEFORE_TEST = bool(
    os.environ.get('CLEANUP_UNEXPECTED_BEFORE_TEST', False))

CLEANUP_UNEXPECTED_AFTER_TEST = bool(
    os.environ.get('CLEANUP_UNEXPECTED_AFTER_TEST', False))

CLEANUP_UNEXPECTED_AFTER_ALL = bool(
    os.environ.get('CLEANUP_UNEXPECTED_AFTER_ALL', False))

UNEXPECTED_VOLUMES_LIMIT = int(
    os.environ.get('UNEXPECTED_VOLUMES_LIMIT', 0))
