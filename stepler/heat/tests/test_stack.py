"""
----------------
Heat stack tests
----------------
"""

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from stepler.third_party import utils


def test_create_stack_with_aws(read_heat_template, network, subnet, router,
                               add_router_interfaces, public_network,
                               create_stack, port_steps):
    """**Scenario:** Create stack with AWS resources.

    **Setup:**

        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network

    **Steps:**

        #. Add router interface to created network
        #. Read AWS template from file
        #. Create stack with template with parameters:
            internal_network, internal_subnet, external_network
        #. Check stack reach "COMPLETE" status

    **Teardown:**

        #. Delete stack
        #. Delete router
        #. Delete subnet
        #. Delete network
    """
    add_router_interfaces(router, [subnet])
    template = read_heat_template('aws')
    stack_name = next(utils.generate_ids('stack'))
    create_stack(
        stack_name,
        template=template,
        parameters={
            'internal_network': network['id'],
            'internal_subnet': subnet['id'],
            'external_network': public_network['id']
        })


def test_create_stack_with_docker(keypair, flavor, network, subnet, router,
                                  ubuntu_xenial_image, read_heat_template,
                                  add_router_interfaces, public_network,
                                  create_stack, stack_steps):
    """**Scenario:** Create stack with Docker.

    **Setup:**

        #. Create network
        #. Create subnet
        #. Create router
        #. Set router default gateway to public network

    **Steps:**

        #. Add router interface to created network
        #. Read docker host template from file
        #. Create stack with template with parameters:
            key, flavor, image, public_net, int_network_id
        #. Check stack reach "COMPLETE" status
        #. Get created server floating_ip
        #. Read docker_containers template
        #. Create stack with template with `docker_endpoint` parameter
        #. Check stack reach "COMPLETE" status

    **Teardown:**

        #. Delete stacks
        #. Delete router
        #. Delete subnet
        #. Delete network
    """
    add_router_interfaces(router, [subnet])
    docker_port = 2376
    template = read_heat_template('docker_host')
    docker_host_stack = create_stack(
        next(utils.generate_ids('docker_host_stack')),
        template=template,
        parameters={
            'key': keypair.name,
            'flavor': flavor.name,
            'image': ubuntu_xenial_image.id,
            'public_net': public_network['id'],
            'int_network_id': network['id'],
            'docker_port': docker_port,
        })
    floating_ip = stack_steps.get_output(docker_host_stack,
                                         'instance_ip')['output_value']
    docker_endpoint = 'tcp://%s:%s' % (floating_ip, docker_port)
    template = read_heat_template('docker_containers')
    create_stack(
        next(utils.generate_ids('docker_containers_stack')),
        template,
        parameters={'docker_endpoint': docker_endpoint})
