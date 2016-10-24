"""
------------
Volume tests
------------
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

from cinderclient.exceptions import BadRequest
from hamcrest import assert_that, calling, raises  # noqa


@pytest.mark.idempotent_id('adcb5b96-35a3-401b-8ca2-3bc13ee225b9')
@pytest.mark.parametrize('size', [-1, 1])
def test_negative_extend_volume(size, create_volume, cinder_steps):
    vol = create_volume(size=2)
    error_message = 'New size for extend must be greater than current size'
    assert_that(
        calling(cinder_steps.volume_extend).with_args(vol, size, check=False),
        raises(BadRequest, error_message))
