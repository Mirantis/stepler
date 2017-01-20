"""
------------------
Nova Rebuild tests
------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from stepler import config


@pytest.mark.idempotent_id('a277b275-507f-4340-a74a-f9936a7fc25a',
                           cirros_server_to_rebuild={
                               'boot_from_volume': False})
@pytest.mark.idempotent_id('c1b4d772-aef4-4e37-85dd-a193b74e34b7',
                           cirros_server_to_rebuild={
                               'boot_from_volume': True})
@pytest.mark.parametrize('cirros_server_to_rebuild',
                         [
                             {'boot_from_volume': False},
                             {'boot_from_volume': True}
                         ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['cirros_server_to_rebuild'])
def test_rebuild_locked_server(cirros_server_to_rebuild,
                               cirros_image,
                               nova_floating_ip,
                               server_steps):
    """**Scenario:** Rebuild locked server.

        **Setup:**

        #. Upload cirros image
        #. Create network with subnet and router
        #. Create security group with allowed ping and ssh rules
        #. Create flavor
        #. Boot a server from image or volume

        **Steps:**

        #. Create a floating IP and attach it to previously created server
        #. Lock the server and check its status
        #. Rebuild previously locked server
        #. Check that rebuilt server has an ACTIVE status and locked=True
        #. Send pings to server's floating IP to check network connectivity

        **Teardown:**

        #. Delete a server
        #. Delete flavor
        #. Delete security group
        #. Delete network, subnet, router
        #. Delete floating IP
        #. Delete cirros image
        """
    server_steps.attach_floating_ip(cirros_server_to_rebuild, nova_floating_ip)
    server_steps.lock_server(cirros_server_to_rebuild)
    server_steps.rebuild_server(cirros_server_to_rebuild, cirros_image)
    server_steps.check_server_attribute(cirros_server_to_rebuild,
                                        attr=config.SERVER_ATTR_LOCKED,
                                        value=True)
    server_steps.check_ping_to_server_floating(
        cirros_server_to_rebuild,
        timeout=config.PING_CALL_TIMEOUT
    )


@pytest.mark.idempotent_id('a924b1c5-87c8-448b-8f9f-29177daab6e9',
                           cirros_server_to_rebuild={
                               'boot_from_volume': False})
@pytest.mark.idempotent_id('30603075-45a7-4382-8168-8ef912261d8d',
                           cirros_server_to_rebuild={
                               'boot_from_volume': True})
@pytest.mark.parametrize('cirros_server_to_rebuild',
                         [
                             {'boot_from_volume': False},
                             {'boot_from_volume': True}
                         ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['cirros_server_to_rebuild'])
def test_rebuild_server_with_description(cirros_server_to_rebuild,
                                         cirros_image,
                                         nova_floating_ip,
                                         server_steps):
    """**Scenario:** Rebuild server with description.

        **Setup:**

        #. Upload cirros image
        #. Create network with subnet and router
        #. Create security group with allowed ping and ssh rules
        #. Create flavor
        #. Boot a server from image or volume

        **Steps:**

        #. Create a floating IP and attach it to previously created server
        #. Rebuild the server with --description parameter
        #. Check that rebuilt server has an ACTIVE status
        #. Check that the description was added
        #. Send pings to server's floating IP to check network connectivity

        **Teardown:**

        #. Delete a server
        #. Delete flavor
        #. Delete security group
        #. Delete network, subnet, router
        #. Delete floating IP
        #. Delete cirros image
        """
    server_steps.attach_floating_ip(cirros_server_to_rebuild, nova_floating_ip)
    server_steps.rebuild_server(
        cirros_server_to_rebuild, cirros_image,
        description=config.DESCRIPTION_FOR_TEST_REBUILD
    )
    server_steps.check_server_attribute(
        cirros_server_to_rebuild,
        attr=config.SERVER_ATTR_DESCRIPTION,
        value=config.DESCRIPTION_FOR_TEST_REBUILD
    )
    server_steps.check_ping_to_server_floating(
        cirros_server_to_rebuild,
        timeout=config.PING_CALL_TIMEOUT
    )


@pytest.mark.idempotent_id('ac561e28-a72e-4dde-850b-83165d2ec404',
                           ubuntu_server_to_rebuild={
                               'boot_from_volume': False})
@pytest.mark.idempotent_id('25092173-96b0-422b-bb7e-191fc4d82696',
                           ubuntu_server_to_rebuild={
                               'boot_from_volume': True})
@pytest.mark.parametrize('ubuntu_server_to_rebuild',
                         [
                             {'boot_from_volume': False},
                             {'boot_from_volume': True}
                         ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['ubuntu_server_to_rebuild'])
def test_rebuild_with_user_files(ubuntu_server_to_rebuild,
                                 ubuntu_image,
                                 nova_floating_ip,
                                 server_steps):
    """**Scenario:** Rebuild server with user files.

        **Setup:**

        #. Upload ubuntu image
        #. Create network with subnet and router
        #. Create security group with allowed ping and ssh rules
        #. Create flavor
        #. Boot a server from image or volume

        **Steps:**

        #. Create a floating IP and attach it to previously created server
        #. Rebuild the server with --files parameter
        #. Check that rebuilt server has an ACTIVE status
        #. Check that ubuntu booted successfully on a rebuilt server
        #. Check that all files added during server's rebuild
           are present in target directory of this server

        **Teardown:**

        #. Delete a server
        #. Delete flavor
        #. Delete security group
        #. Delete network, subnet, router
        #. Delete floating IP
        #. Delete ubuntu image
        """
    server_steps.attach_floating_ip(ubuntu_server_to_rebuild, nova_floating_ip)
    server_steps.rebuild_server(ubuntu_server_to_rebuild, ubuntu_image,
                                files=config.USER_FILES_FOR_TEST_REBUILD)
    server_steps.check_server_log_contains_record(
        ubuntu_server_to_rebuild,
        ubuntu_server_to_rebuild.name + ' login: ',
        timeout=config.UBUNTU_BOOT_COMPLETE_TIMEOUT
    )

    with server_steps.get_server_ssh(ubuntu_server_to_rebuild,
                                     nova_floating_ip.ip) as server_ssh:
        for filepath in sorted(config.USER_FILES_FOR_TEST_REBUILD.keys()):
            server_steps.check_files_presence_for_fs(server_ssh, filepath)


@pytest.mark.idempotent_id('280559ac-d000-4132-ab7e-6b75b1dfb1fd')
def test_rebuild_in_paused_state(cirros_image, server, server_steps):
    """**Scenario:** Try to rebuild an instance in Paused state.

    **Setup:**

    #. Create server

    **Steps:**

    #. Pause server
    #. Try to rebuild server
    #. Check that rebuild fails and exception is called

    **Teardown:**

    #. Delete server
    """
    server_steps.pause_server(server)
    server_steps.check_server_not_rebuilt_in_paused_state(
        server, cirros_image)


@pytest.mark.idempotent_id('f289dfcd-b63a-473d-90fb-1e099fe51c4b')
def test_rebuild_in_rescue_state(cirros_image, server, server_steps):
    """**Scenario:** Try to rebuild an instance in Rescued state.

    **Setup:**

    #. Create server

    **Steps:**

    #. Rescue server
    #. Try to rebuild server
    #. Check that rebuild fails and exception is called

    **Teardown:**

    #. Delete server
    """
    server_steps.rescue_server(server)
    server_steps.check_server_not_rebuilt_in_rescue_state(
        server, cirros_image)
