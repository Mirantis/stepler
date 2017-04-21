"""
-------------
Routers steps
-------------
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

from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils


class RoutersSteps(base.BaseSteps):
    """Routers steps."""

    def _page_routers(self):
        """Open routers page if it isn't opened."""
        return self._open(self.app.page_routers)

    @steps_checker.step
    def create_router(self, router_name=None, admin_state=None,
                      external_network=None, check=True):
        """Step to create router."""
        router_name = router_name or next(utils.generate_ids('router'))

        page_routers = self._page_routers()
        page_routers.button_create_router.click()

        with page_routers.form_create_router as form:
            form.field_name.value = router_name

            if admin_state:
                form.combobox_admin_state.value = admin_state

            if external_network:
                form.combobox_external_network.value = external_network

            form.submit()

        if check:
            self.close_notification('success')
            page_routers.table_routers.row(
                name=router_name).wait_for_presence(30)

        return router_name

    @steps_checker.step
    def delete_router(self, router_name, check=True):
        """Step to delete router."""
        page_routers = self._page_routers()

        with page_routers.table_routers.row(
                name=router_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_routers.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_routers.table_routers.row(
                name=router_name).wait_for_absence()
