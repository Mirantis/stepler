"""
----------------
Heat stack tests
----------------
"""

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

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.idempotent_id('26888f92-a5f9-4cf8-a6a6-22c766d41197')
def test_stack_output_show(create_stack,
                           read_heat_template,
                           stack_steps):
    """**Scenario:** Check stack output show has correct output.

    **Steps:**

    #. Read template from file
    #. Create stack with template
    #. Get output show
    #. Check that attribute output_show exist

    **Teardown:**

    #. Delete stack
    """
    template = read_heat_template('random_str')
    stack = create_stack(next(utils.generate_ids()), template)
    stack_steps.check_output_show(stack, 'random_str1')


@pytest.mark.idempotent_id('675eab7b-cad1-4557-9706-7c8338208322')
def test_check_output_show_during_stack_creation(create_stack,
                                                 read_heat_template,
                                                 stack_steps):
    """**Scenario:** Check stack output show during stack creation.

    **Steps:**

    #. Read template from file
    #. Launch creation stack with template
    #. Get output show
    #. Check that output contains expected attribute values

    **Teardown:**

    #. Delete stack
    """
    attr_values = {'output_value': 'a', 'description': 'ID of resource a',
                   'output_key': 'resource_id_a'}

    template = read_heat_template('check_output')
    stack = create_stack(next(utils.generate_ids()),
                         template=template,
                         parameters={'wait_secs': 15},
                         check=False)
    stack_steps.check_status(stack, config.HEAT_IN_PROGRESS_STATUS)
    stack_steps.check_output_show(stack, attr_values['output_key'],
                                  attr_values,
                                  timeout=config.STACK_CHECK_TIMEOUT)


@pytest.mark.idempotent_id('2c0122e4-c39f-4384-a144-56f656b9792c')
def test_stack_output_list(create_stack,
                           read_heat_template,
                           stack_steps):
    """**Scenario:** Check stack output list has correct output.

    **Steps:**

    #. Read template from file
    #. Create stack with template
    #. Get output list
    #. Check that output list has correct output

    **Teardown:**

    #. Delete stack
    """
    template = read_heat_template('random_str')
    stack_name = next(utils.generate_ids('stack'))
    stack = create_stack(stack_name, template)
    output_list = stack_steps.get_stack_output_list(stack)
    stack_steps.check_output_list(output_list)


@pytest.mark.idempotent_id('d23ef04a-6db0-4729-97ac-3a8302951f69')
def test_create_stack_with_aws(
        net_subnet_router,
        read_heat_template,
        public_network,
        create_stack,
        port_steps):
    """**Scenario:** Create stack with AWS resources.

    **Setup:**

    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network
    #. Add router interface to created network

    **Steps:**

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
    network, subnet, _ = net_subnet_router
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


@pytest.mark.idempotent_id('d9df00f4-97fe-469e-ad3c-5a3cb74a4587')
def test_create_stack_with_heat_resources(read_heat_template, create_stack):
    """**Scenario:** Create stack with heat resources.

    **Steps:**

    #. Read Heat resources template from file
    #. Create stack with template
    #. Check stack reach "COMPLETE" status

    **Teardown:**

    #. Delete stack
    """
    template = read_heat_template('heat_resources')
    stack_name = next(utils.generate_ids('stack'))
    create_stack(stack_name, template=template)


@pytest.mark.idempotent_id('2a001c1b-becc-4db3-a711-9f49642b7ae9')
def test_create_stack_with_wait_condition(
        cirros_image,
        flavor,
        net_subnet_router,
        read_heat_template,
        create_stack,
        port_steps):
    """**Scenario:** Create stack with WaitCondition resources.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network

    **Steps:**

    #. Read template with WaitCondition resources
    #. Create stack with template with parameters:
            image, flavor, private_net
    #. Check stack reach "COMPLETE" status

    **Teardown:**

    #. Delete stack
    #. Delete flavor
    #. Delete image
    """
    template = read_heat_template('wait_condition')
    stack_name = next(utils.generate_ids('stack'))
    create_stack(
        stack_name,
        template=template,
        parameters={
            'image': cirros_image.id,
            'flavor': flavor.id,
            'private_net': net_subnet_router[0]['id'],
        })


@pytest.mark.idempotent_id('c8afb285-1f48-4a0f-9a52-a5b090a48240')
def test_create_stack_with_neutron_resources(
        cirros_image,
        flavor,
        public_network,
        net_subnet_router,
        read_heat_template,
        create_stack):
    """**Scenario:** Create stack with Neutron resources.

    **Setup:**

    #. Create cirros image
    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network
    #. Add router interface to created network

    **Steps:**

    #. Read Heat resources template from file
    #. Create stack with template with parameters:
            image, flavor, public_net_id, private_net_id, private_subnet_id
    #. Check stack reach "COMPLETE" status

    **Teardown:**

    #. Delete stack
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    network, subnet, _ = net_subnet_router
    template = read_heat_template('neutron_resources')
    stack_name = next(utils.generate_ids('stack'))
    create_stack(
        stack_name,
        template=template,
        parameters={
            'image': cirros_image.id,
            'flavor': flavor.id,
            'public_net_id': public_network['id'],
            'private_net_id': network['id'],
            'private_subnet_id': subnet['id'],
        })


@pytest.mark.idempotent_id('933d8d45-59c7-4e0e-a9dd-36cd38bc1e98')
def test_create_stack_with_nova_resources(
        cirros_image,
        flavor,
        public_network,
        net_subnet_router,
        read_heat_template,
        create_stack):
    """**Scenario:** Create stack with Nova resources.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network
    #. Add router interface to created network

    **Steps:**

    #. Read Heat resources template from file
    #. Create stack with template with parameters:
            image, flavor, public_net_id, private_net_id, private_subnet_id
    #. Check stack reach "COMPLETE" status

    **Teardown:**

    #. Delete stack
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete flavor
    #. Delete cirros image
    """
    template = read_heat_template('nova_resources')
    additional_template = read_heat_template('volume_with_attachment')
    stack_name = next(utils.generate_ids('stack'))
    create_stack(
        stack_name,
        template=template,
        parameters={
            'image': cirros_image.id,
            'flavor': flavor.id,
            'int_network': net_subnet_router[0]['id'],
        },
        files={'volume_with_attachment.yaml': additional_template})


@pytest.mark.idempotent_id('83c10ab7-3902-4d20-9ed8-81f3a47ba415')
def test_create_stack_with_docker(
        keypair,
        flavor,
        net_subnet_router,
        ubuntu_xenial_image,
        read_heat_template,
        public_network,
        create_stack,
        stack_steps):
    """**Scenario:** Create stack with Docker.

    **Setup:**

    #. Create network
    #. Create subnet
    #. Create router
    #. Set router default gateway to public network
    #. Add router interface to created network

    **Steps:**

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
            'int_network_id': net_subnet_router[0]['id'],
            'docker_port': docker_port,
        })
    floating_ip = stack_steps.get_output(docker_host_stack,
                                         'instance_ip')['output_value']
    docker_endpoint = 'tcp://{}:{}'.format(floating_ip, docker_port)
    template = read_heat_template('docker_containers')
    create_stack(
        next(utils.generate_ids('docker_containers_stack')),
        template,
        parameters={'docker_endpoint': docker_endpoint})


@pytest.mark.idempotent_id('cff710ec-1df2-4fe3-990f-4c4684b89550')
def test_stack_update_parameter_replace(create_stack,
                                        read_heat_template,
                                        stack_steps,
                                        heat_resource_steps,
                                        glance_steps):
    """**Scenario:** Update stack with changed template.

    **Steps:**

    #. Read template from file
    #. Create stack with template
    #. Get physical_resource_id
    #. Get image
    #. Check that image container_format is bare
    #. Check that image disk_format is qcow2
    #. Update stack
    #. Check that image container_format is ami
    #. Check that image disk_format is ami
    #. Check that image_id was changed
    #. Check that physical_resource_id was changed

    **Teardown:**

    #. Delete stack
    """
    template = read_heat_template('cirros_image_tmpl')
    template_updated = read_heat_template('cirros_image_updated_tmpl')
    stack_name = next(utils.generate_ids('stack'))

    stack = create_stack(stack_name, template)
    resource_id = heat_resource_steps.get_resource(
        stack, config.RESOURCE_NAME).physical_resource_id
    image = glance_steps.get_image(name=config.RESOURCE_NAME)
    glance_steps.check_image_container_and_disk_format(
        config.RESOURCE_NAME, 'bare', 'qcow2')

    stack_steps.update_stack(stack, template_updated)
    glance_steps.check_image_container_and_disk_format(
        config.RESOURCE_NAME, 'ami', 'ami')
    glance_steps.check_that_image_id_is_changed(
        config.RESOURCE_NAME, image['id'])
    heat_resource_steps.check_that_resource_id_changed(
        resource_id, stack, config.RESOURCE_NAME)


@pytest.mark.idempotent_id('f9ef547a-9934-46f7-b913-5959c03e0eac')
def test_get_stack_template(empty_stack, stack_steps):
    """**Scenario:** Show template of created stack.

    **Setup:**

    #. Create stack

    **Steps:**

    #. Get template for stack
    #. Check that template is not empty

    **Teardown:**

    #. Delete stack
    """
    stack_steps.get_stack_template(empty_stack)
