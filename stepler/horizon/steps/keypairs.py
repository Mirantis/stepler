"""
--------------
Keypairs steps
--------------
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

from hamcrest import (assert_that, equal_to, is_in, less_than)  # noqa

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party.utils import Timer


class KeypairsSteps(base.BaseSteps):
    """Keypairs steps."""

    def _page_keypairs(self):
        """Open keypairs page."""
        return self._open(self.app.page_keypairs)

    @steps_checker.step
    def create_keypair(self, keypair_name=None, check=True):
        """Step to create keypair."""
        keypair_name = keypair_name or next(utils.generate_ids('keypair'))

        page_keypairs = self._page_keypairs()
        page_keypairs.button_create_keypair.click()

        with page_keypairs.form_create_keypair as form:
            form.field_name.value = keypair_name
            form.button_create_keypair.click()
            form.button_submit().click()

        if check:
            self._page_keypairs()
            page_keypairs.table_keypairs.row(
                name=keypair_name).wait_for_presence()

        return keypair_name

    @steps_checker.step
    def delete_keypair(self, keypair_name, check=True):
        """Step to delete keypair."""
        page_keypairs = self._page_keypairs()

        page_keypairs.table_keypairs.row(
            name=keypair_name).button_delete_keypair.click()
        page_keypairs.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_keypairs.table_keypairs.row(
                name=keypair_name).wait_for_absence()

    @steps_checker.step
    def import_keypair(self, keypair_name, public_key, check=True):
        """Step to import keypair."""
        page_keypairs = self._page_keypairs()
        page_keypairs.button_import_keypair.click()

        with page_keypairs.form_import_keypair as form:
            form.field_name.value = keypair_name
            form.field_public_key.value = public_key
            form.submit()

        if check:
            self.close_notification('success')
            page_keypairs.table_keypairs.row(
                name=keypair_name).wait_for_presence()

    @steps_checker.step
    def delete_keypairs(self, keypair_names, check=True):
        """Step to delete keypairs."""
        page_keypairs = self._page_keypairs()

        for keypair_name in keypair_names:
            page_keypairs.table_keypairs.row(
                name=keypair_name).checkbox.select()

        page_keypairs.button_delete_keypairs.click()
        page_keypairs.form_confirm.submit()

        if check:
            self.close_notification('success')
            for keypair_name in keypair_names:
                page_keypairs.table_keypairs.row(
                    name=keypair_name).wait_for_absence()

    @steps_checker.step
    def check_button_import_key_pair_disabled(self):
        """Step to check `import Key Pair` disabled if quota exceeded."""
        page_keypairs = self._page_keypairs()
        assert_that('disabled', is_in(
            page_keypairs.button_import_keypair.get_attribute("class")))

    @steps_checker.step
    def check_keypairs_time(self):
        """Step to check time opening Keypairs page."""
        with Timer() as timer:
            self._page_keypairs()
        assert_that(timer.interval, less_than(config.UI_TIMEOUT_OPENING_PAGE))
