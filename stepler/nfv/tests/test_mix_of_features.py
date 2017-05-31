"""
----------------------
NFV features mix tests
----------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler import config
from stepler.third_party import utils


@pytest.mark.requires("vlan")
@pytest.mark.parametrize('computes_with_cpu_pinning_and_hp',
                         [{'host_count': 2, 'hp_count_2mb': 512,
                           'hp_count_1gb': 4}],
                         indirect=['computes_with_cpu_pinning_and_hp'])
@pytest.mark.idempotent_id('2a163a5c-171c-467d-a843-10b4a5caa3e9')
def test_cpu_pinning_and_hp_connectivity(computes_with_cpu_pinning_and_hp,
                                         create_aggregate,
                                         aggregate_steps,
                                         cirros_image,
                                         keypair,
                                         create_flavor,
                                         flavor_steps,
                                         security_group,
                                         neutron_2_networks,
                                         create_floating_ip,
                                         server_steps,
                                         host_steps):
    """**Scenario:** Check connectivity between servers with CPU pinning and HP

    **Setup:**

    #. Find two computes with CPU pinning and HP 2Mb/1Gb
    #. Create cirros image
    #. Create keypair
    #. Create security group
    #. Create two networks, subnets and one router

    **Steps:**

    #. Create aggregate with pinned=True, hpgs=true and host1 and host2
    #. Create flavor1 with mem_page_size=1048576, hpgs=true, pinned=false
    #. Create flavor2 with mem_page_size=2048, hpgs=true, cpu_policy=dedicated,
    #.     pinned=true, numa_nodes=2
    #. Create flavor3 with hpgs=false, cpu_policy=dedicated, pinned=true,
    #.     numa_nodes=2
    #. Create flavor4 with mem_page_size=2048, hpgs=true, cpu_policy=dedicated,
    #.     pinned=true
    #. Create flavor5 with pinned=false
    #. Create server1 with flavor1 on host1, network1
    #. Create server2 with flavor2 on host1, network1
    #. Create server3 with flavor3 on host2, network2
    #. Create server4 with flavor2 on host2, network2
    #. Create server5 with flavor5 on host1, network2
    #. Create and attach floating IPs to servers
    #. Check connectivity between servers

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavors
    #. Delete keypair
    #. Delete cirros image
    #. Delete aggregate
    """
    aggregate = create_aggregate()
    metadata = {'pinned': 'true', 'hpgs': 'true'}
    aggregate_steps.set_metadata(aggregate, metadata)

    fqdns = computes_with_cpu_pinning_and_hp
    host_names_cpu_pinning_hp = [host_steps.get_host(fqdn=fqdn).host_name
                                 for fqdn in fqdns]

    flavors = []
    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'hw:mem_page_size': str(config.page_1gb),
                'aggregate_instance_extra_specs:hpgs': 'true',
                'aggregate_instance_extra_specs:pinned': 'false'}
    flavor_steps.set_metadata(flavor, metadata)
    flavors.append(flavor)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=512, vcpus=2, disk=20)
    metadata = {'hw:mem_page_size': str(config.page_2mb),
                'aggregate_instance_extra_specs:hpgs': 'true',
                'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '2'}
    flavor_steps.set_metadata(flavor, metadata)
    flavors.append(flavor)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'aggregate_instance_extra_specs:hpgs': 'false',
                'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true',
                'hw:numa_nodes': '2'}
    flavor_steps.set_metadata(flavor, metadata)
    flavors.append(flavor)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=512, vcpus=2, disk=20)
    metadata = {'hw:mem_page_size': str(config.page_2mb),
                'aggregate_instance_extra_specs:hpgs': 'true',
                'hw:cpu_policy': 'dedicated',
                'aggregate_instance_extra_specs:pinned': 'true'}
    flavor_steps.set_metadata(flavor, metadata)
    flavors.append(flavor)

    flavor_name = next(utils.generate_ids('flavor'))
    flavor = create_flavor(flavor_name, ram=2048, vcpus=2, disk=20)
    metadata = {'aggregate_instance_extra_specs:pinned': 'false'}
    flavor_steps.set_metadata(flavor, metadata)
    flavors.append(flavor)

    networks = [neutron_2_networks.networks[0],
                neutron_2_networks.networks[0],
                neutron_2_networks.networks[1],
                neutron_2_networks.networks[1],
                neutron_2_networks.networks[1]]

    host_names = [host_names_cpu_pinning_hp[0],
                  host_names_cpu_pinning_hp[0],
                  host_names_cpu_pinning_hp[1],
                  host_names_cpu_pinning_hp[1],
                  host_names_cpu_pinning_hp[0]]

    servers = []
    for i in range(5):
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavors[i],
            networks=[networks[i]],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            password=config.CIRROS_PASSWORD,
            keypair=keypair,
            availability_zone='nova:{}'.format(host_names[i]))[0]
        floating_ip = create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)
        servers.append(server)

    server_steps.check_ping_between_servers_via_floating(
        servers, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
