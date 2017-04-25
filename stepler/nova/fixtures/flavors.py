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

from hamcrest import assert_that, empty, is_not  # noqa
from novaclient import exceptions
import pytest

from stepler import config
from stepler.nova import steps
from stepler.third_party import utils

__all__ = [
    'create_flavor',
    'flavor',
    'flavors',
    'flavor_steps',
    'tiny_flavor',
    'small_flavor',
    'baremetal_flavor',
    'public_flavor',
    'available_flavors_for_hypervisors',
]


@pytest.fixture
def flavor_steps(nova_client):
    """Function fixture to get nova flavor steps.

    Args:
        nova_client (function): function to get nova client

    Yields:
        stepler.nova.steps.FlavorSteps: instantiated flavor steps
    """
    _flavor_steps = steps.FlavorSteps(nova_client.flavors)

    flavors = _flavor_steps.get_flavors(check=False)
    flavor_ids_before = {flavor.id for flavor in flavors}

    yield _flavor_steps

    uncleanable_ids = flavor_ids_before
    _cleanup_flavors(_flavor_steps, uncleanable_ids=uncleanable_ids)


def _cleanup_flavors(_flavor_steps, uncleanable_ids=None):
    """Function to cleanup flavors.

    Args:
        _flavor_steps (object): instantiated flavor steps
        uncleanable_ids (AttrDict): resources ids to skip cleanup
    """
    uncleanable_ids = uncleanable_ids or []

    for flavor in _flavor_steps.get_flavors(check=False):
        if flavor.id not in uncleanable_ids:
            _flavor_steps.delete_flavor(flavor)


@pytest.fixture
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


def flavor_builder(**kwargs):
    """Function to generate flavor fixture function.

    Args:
        **kwargs: any arguments to be passed to create flavor method

    Returns:
        function: flavor fixture
    """

    @pytest.fixture
    def _flavor(request, flavor_steps):
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
            request (object): py.test SubRequest
            flavor_steps (object): instantiated flavor steps

        Returns:
            function: function to create single flavor with options
        """
        flavor_params = config.DEFAULT_FLAVOR_PARAMS.copy()
        flavor_params.update(**kwargs)
        flavor_params.update(getattr(request, 'param', {}))

        flavor_name, = utils.generate_ids('flavor')
        metadata = flavor_params.pop('metadata', None)

        flavor = flavor_steps.create_flavor(flavor_name, **flavor_params)

        if metadata:
            flavor_steps.set_metadata(flavor, metadata)

        return flavor

    return _flavor

flavor = flavor_builder()
public_flavor = flavor_builder(is_public=True)


@pytest.fixture
def flavors(request, flavor_steps):
    """Function fixture to create flavor with default options before test.

    Args:
        request (object): py.test's SubRequest instance
        create_flavor (function): function to create flavor with options

    Returns:
        list: nova flavors
    """
    count = int(getattr(request, 'param', 3))

    flavors = []
    flavor_names = utils.generate_ids(prefix='flavor', count=count)
    flavor_params = config.DEFAULT_FLAVOR_PARAMS.copy()
    flavor_params.pop('metadata')

    for flavor_name in flavor_names:
        flavor = flavor_steps.create_flavor(flavor_name, **flavor_params)
        flavors.append(flavor)

    return flavors


@pytest.fixture
def tiny_flavor(flavor_steps):
    """Function fixture to find or create tiny flavor before test.

    Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        object: tiny flavor
    """
    try:
        flavor = flavor_steps.get_flavor(name=config.FLAVOR_TINY)
    except exceptions.NotFound:
        name, = utils.generate_ids(config.FLAVOR_TINY)
        flavor = flavor_steps.create_flavor(name, ram=512, vcpus=1, disk=1)
    return flavor


@pytest.fixture
def small_flavor(flavor_steps):
    """Function fixture to find or create small flavor before test.

    Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        object: small flavor
    """
    try:
        flavor = flavor_steps.get_flavor(name=config.FLAVOR_SMALL)
    except exceptions.NotFound:
        name, = utils.generate_ids(config.FLAVOR_SMALL)
        flavor = flavor_steps.create_flavor(name, ram=2048, vcpus=1, disk=20)
    return flavor


@pytest.fixture
def baremetal_flavor(flavor_steps):
    """Function fixture to create baremetal flavor before test.

     Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        object: baremetal flavor
    """
    params = {'is_public': True}
    if config.BAREMETAL_NODE:
        params.update({
            'ram': config.BAREMETAL_RAM,
            'vcpus': config.BAREMETAL_VCPUS,
            'disk': config.BAREMETAL_DISK,
        })
    else:
        params.update({
            'ram': config.BAREMETAL_VIRTUAL_RAM,
            'vcpus': config.BAREMETAL_VIRTUAL_VCPUS,
            'disk': config.BAREMETAL_VIRTUAL_DISK,
        })

    return flavor_steps.create_flavor(next(utils.generate_ids('bm_flavor')),
                                      **params)


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
