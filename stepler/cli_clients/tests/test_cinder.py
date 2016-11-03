# -*- coding: utf-8 -*-
"""
---------------------------
Tests for cinder CLI client
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

from stepler import config


@pytest.mark.idempotent_id('225d218b-6562-431d-bdf9-0ec0221c0f86')
def test_volume_backup_non_unicode_name(volume, backups_cleanup,
                                        cli_cinder_steps, backup_steps):
    """**Scenario:** Create volume backup with non unicode symbols name.

    **Setup:**

    #. Create volume

    **Steps:**

    #. Create volume backup with non unicode symbols name using CLI

    **Teardown:**

    #. Delete volume backup
    #. Delete volume
    """
    backup_dict = cli_cinder_steps.create_volume_backup(volume, name=u"シンダー")
    backup = backup_steps.get_backup_by_id(backup_dict['id'])
    backup_steps.check_backup_status(backup, config.STATUS_AVAILABLE,
                                     timeout=config.BACKUP_AVAILABLE_TIMEOUT)
