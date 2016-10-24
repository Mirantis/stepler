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


def test_create_stack_with_wait_condition(read_heat_template, cirros_image,
                                          flavor, public_network, create_stack,
                                          port_steps):
    """**Scenario:** Create stack with WaitCondition resources.

    **Setup:**

        #. Create cirros image
        #. Create flavor

    **Steps:**

        #. Read AWS template from file
        #. Create stack with template with parameters:
            image, flavor, public_net
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
            'public_net': public_network['id'],
        })
