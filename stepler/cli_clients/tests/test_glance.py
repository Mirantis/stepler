# -*- coding: utf-8 -*-

"""
---------------------------
Tests for glance CLI client
---------------------------
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


@pytest.mark.idempotent_id('85461edd-7c82-4c27-ad19-d3af178818fe')
def test_glance_validate_unicode_support(cli_glance_steps):
    """**Scenario:** Check support of unicode symbols in image name.

    **Steps:**

        #. Create image with name 試験画像
        #. Check that created image is in list and has status `queued`
        #. Delete image
        #  Check that image deleted
    """
    cli_glance_steps.validate_unicode_support()
