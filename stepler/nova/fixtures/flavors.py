"""
---------------
Flavor fixtures
---------------
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

import pytest

from hamcrest import assert_that, empty, is_not  # noqa
from novaclient import exceptions

from stepler import config
from stepler.nova.steps import FlavorSteps
from stepler.third_party import utils

__all__ = [
    'create_flavor',
    'flavor',
    'flavor_steps',
    'tiny_flavor',
    'small_flavor',
    'baremetal_flavor',
    'public_flavor',
    'available_flavors_for_hypervisors',
]


@pytest.fixture
def flavor_steps(nova_client):
    """Callable function fixture to get nova flavor steps.

    Args:
        nova_client (function): function to get nova client

    Returns:
        function: function to instantiated flavor steps
    """
    return FlavorSteps(nova_client.flavors)


@pytest.yield_fixture
def create_flavor(flavor_steps):
    """Callable function fixture to create nova flavor with options.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        function: function to create flavors as batch with options
    """
    flavors = []

    def _create_flavor(flavor_name, *args, **kwargs):
        flavor = flavor_steps.create_flavor(flavor_name, *args, **kwargs)
        flavors.append(flavor)
        return flavor

    yield _create_flavor

    for flavor in flavors:
        flavor_steps.delete_flavor(flavor)


@pytest.fixture
def flavor(request, create_flavor, flavor_steps):
    """Function fixture to create single nova flavor with options.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Can be parametrized with dict of create_flavor arguments.


    Example:
        .. code:: python

            @pytest.mark.parametrize('flavor', [
                dict(ram=2048, vcpus=2),
                dict(ram=512, disk=1, metadata={'hw:mem_page_size':
                                                'large m1.tiny'}),
            ], indirect=['flavor'])
            def test_foo(instance):
                # Instance will created with different flavors

    Args:
        request (obj): py.test SubRequest
        create_flavor (function): function to create flavor with options
        flavor_steps (object): instantiated flavor steps

    Returns:
        function: function to create single flavor with options
    """
    flavor_params = config.DEFAULT_FLAVOR_PARAMS.copy()
    flavor_params.update(getattr(request, 'param', {}))

    flavor_name, = utils.generate_ids('flavor')
    flavor = create_flavor(flavor_name, **flavor_params)

    metadata = flavor_params.get('metadata')
    if metadata:
        flavor_steps.set_metadata(flavor, metadata)

    return flavor


@pytest.fixture
def tiny_flavor(flavor_steps, create_flavor):
    """Function fixture to find or create tiny flavor before test.

    Args:
        flavor_steps (object): instantiated flavor steps
        create_flavor (function): function to create flavor with options

    Returns:
        object: tiny flavor
    """
    try:
        flavor = flavor_steps.get_flavor(name=config.FLAVOR_TINY)
    except exceptions.NotFound:
        name, = utils.generate_ids(config.FLAVOR_TINY)
        flavor = create_flavor(name, ram=512, vcpus=1, disk=1)
    return flavor


@pytest.fixture
def small_flavor(flavor_steps, create_flavor):
    """Function fixture to find or create small flavor before test.

    Args:
        flavor_steps (object): instantiated flavor steps
        create_flavor (function): function to create flavor with options

    Returns:
        object: small flavor
    """
    try:
        flavor = flavor_steps.get_flavor(name=config.FLAVOR_SMALL)
    except exceptions.NotFound:
        name, = utils.generate_ids(config.FLAVOR_SMALL)
        flavor = create_flavor(name, ram=2048, vcpus=1, disk=20)
    return flavor


@pytest.fixture
def baremetal_flavor(create_flavor):
    """Function fixture to create baremetal flavor before test.

     Args:
        create_flavor (function): function to create flavor with options

    Returns:
        object: baremetal flavor
    """
    if config.BAREMETAL_NODE:
        ram = config.BAREMETAL_RAM
        vcpus = config.BAREMETAL_VCPUS
    else:
        ram = config.BAREMETAL_VIRTUAL_RAM
        vcpus = config.BAREMETAL_VIRTUAL_VCPUS

    return create_flavor(next(utils.generate_ids('bm_flavor')),
                         ram=ram,
                         vcpus=vcpus,
                         disk=config.BAREMETAL_DISK)


@pytest.fixture
def public_flavor(create_flavor):
    """Function fixture to create public flavor before test.

     Args:
        create_flavor (function): function to create flavor with options

    Returns:
        object: public flavor
    """

    flavor_params = dict(ram=512, vcpus=1, disk=2, is_public=True)
    flavor_name, = utils.generate_ids('flavor')
    return create_flavor(flavor_name, **flavor_params)


@pytest.fixture
def available_flavors_for_hypervisors(flavor_steps, hypervisor_steps):
    """Function fixture to get available flavors for hypervisors.

    Args:
        flavor_steps (object): instantiated flavor steps
        hypervisor_steps (object): instantiated hypervisor steps

    Returns:
        list: list of available flavors
    """
    flavors = flavor_steps.get_flavors()
    hypervisors = hypervisor_steps.get_hypervisors(check=False)
    available_flavors = []
    for flavor in flavors:
        for hypervisor in hypervisors:
            capacity = hypervisor_steps.get_hypervisor_capacity(hypervisor,
                                                                flavor,
                                                                check=False)
            if capacity > 0:
                if flavor not in available_flavors:
                    available_flavors.append(flavor)

    err_msg = "No flavors were retrieved for presents hypervisors"
    assert_that(available_flavors, is_not(empty()), err_msg)

    return available_flavors
