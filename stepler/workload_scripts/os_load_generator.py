#!/usr/bin/env python

"""
--------------------------------------------------------------------
Openstack load generator (creation/deletion of networks and servers)
--------------------------------------------------------------------
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
import signal
import sys
import time
import uuid

from glanceclient.v2.client import Client as GlanceClient
from keystoneauth1 import identity
from keystoneauth1 import session as _session
from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.client import Client as NovaClient


SUFFIX = str(uuid.uuid4())
NETWORK_NAME = 'network-' + SUFFIX
SUBNET_NAME = 'subnet-' + SUFFIX
SERVER_NAME = 'server-' + SUFFIX
TIMEOUT_SERVER_CREATION = 300
TIMEOUT_SERVER_DELETION = 120

signals_received = []


def handle_signal(signum, frame):
    """Signal handler"""
    signals_received.append(signum)


def init_session():
    """Initialization of keystone session, glance, nova and neutron clients.

    Returns:
        tuple: glance_client, nova_client, neutron_client
    """
    AUTH_URL = os.environ.get('OS_AUTH_URL')
    if not AUTH_URL:
        print("AUTH_URL must be set")
        sys.exit(1)

    PROJECT_DOMAIN_NAME = os.environ.get('OS_PROJECT_DOMAIN_NAME', 'default')
    USER_DOMAIN_NAME = os.environ.get('OS_USER_DOMAIN_NAME', 'default')
    PROJECT_NAME = os.environ.get('OS_PROJECT_NAME', 'admin')
    USERNAME = os.environ.get('OS_USERNAME', 'admin')
    PASSWORD = os.environ.get('OS_PASSWORD', 'password')

    auth = identity.v3.Password(
        auth_url=AUTH_URL,
        username=USERNAME,
        user_domain_name=USER_DOMAIN_NAME,
        password=PASSWORD,
        project_name=PROJECT_NAME,
        project_domain_name=PROJECT_DOMAIN_NAME)

    session = _session.Session(auth=auth)

    glance_client = GlanceClient(session=session)
    images = list(glance_client.images.list())
    if not images:
        print("At least one image must exist")
        sys.exit(1)

    nova_client = NovaClient(version=2, session=session)
    neutron_client = NeutronClient(session=session,
                                   project_name=session.get_project_id())

    return glance_client, nova_client, neutron_client


def create_net_subnet_server(glance_client,
                             neutron_client,
                             nova_client):
    """Creation of network, subnet and server with predefined names.

    Args:
        glance_client (obj): instantiated glance client
        neutron_client (obj): instantiated neutron client
        nova_client (obj): instantiated nova client

    Raises:
        Exception: if any problem
    """

    data = {
        'name': NETWORK_NAME,
        'admin_state_up': True
    }
    network = neutron_client.create_network({'network': data})['network']

    data = {
        "network_id": network['id'],
        "ip_version": 4,
        "cidr": '10.2.0.0/24',
        "name": SUBNET_NAME
    }
    neutron_client.create_subnet({'subnet': data})

    image = next(glance_client.images.list())

    server = nova_client.servers.create(name=SERVER_NAME,
                                        image=image['id'],
                                        flavor=2,
                                        nics=[{'net-id': network['id']}])

    finish_time = time.time() + TIMEOUT_SERVER_CREATION
    while server.status == 'BUILD' and time.time() < finish_time:
        server.get()
        time.sleep(1)


def delete_server_subnet_net(neutron_client,
                             nova_client):
    """Deletion of server, subnet and network with predefined names.

    Args:
        neutron_client (obj): instantiated neutron client
        nova_client (obj): instantiated nova client

    Raises:
        Exception: if any problem
    """

    servers = [server for server in nova_client.servers.list()
               if server.name == SERVER_NAME]
    # More than one server with the same name can exist if previous
    # deletion was failed. Similar for networks and subnets.
    for server in servers:
        nova_client.servers.delete(server.id)
        server_exists = True
        finish_time = time.time() + TIMEOUT_SERVER_DELETION
        while server_exists and time.time() < finish_time:
            try:
                server.get()
                time.sleep(1)
            except Exception:
                server_exists = False

    subnets = [subnet for subnet in neutron_client.list_subnets()['subnets']
               if subnet['name'] == SUBNET_NAME]
    for subnet in subnets:
        neutron_client.delete_subnet(subnet['id'])

    networks = [net for net in neutron_client.list_networks()['networks']
                if net['name'] == NETWORK_NAME]
    for network in networks:
        neutron_client.delete_network(network['id'])


def is_parent_process_alive():
    """Check if parent process is alive"""
    return os.getppid() != 1


def generate_os_load():
    """Generator of openstack workload.

    This generator creates and deletes networks, subnets and servers until
    getting a signal TERM or INT. Besides, it stops after terminating its
    parent process.
    It's supposed that there is at least one image.
    All created/deleted objects have names like <prefix>-network where
    <prefix> is the unique identifier for one session.
    During running this generator, some critical operation can be done, ex:
    controller reboot. The generator does not stop if any problems.
    If an error occurs during deletion of objects, they can be deleted
    on the next cycle.
    After getting a signal, the generator provides deletion of objects
    created before.
    """

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    glance_client, nova_client, neutron_client = init_session()

    errors = False
    while not signals_received and is_parent_process_alive():

        try:
            create_net_subnet_server(glance_client, neutron_client,
                                     nova_client)
        except Exception as e:
            errors = True
            print("Exception when object creating: {}".format(e))
            time.sleep(1)

        try:
            delete_server_subnet_net(neutron_client, nova_client)
        except Exception as e:
            errors = True
            print("Exception when object deleting: {}".format(e))
            time.sleep(1)

        time.sleep(5)

    if errors:
        delete_server_subnet_net(neutron_client, nova_client)


if __name__ == "__main__":
    generate_os_load()
