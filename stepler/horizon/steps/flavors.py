"""
Flavors steps.

@author: schipiga@mirantis.com
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

import pom

from .base import BaseSteps


class FlavorsSteps(BaseSteps):
    """Flavors steps."""

    def page_flavors(self):
        """Open flavors page if it isn't opened."""
        return self._open(self.app.page_flavors)

    @pom.timeit('Step')
    def create_flavor(self, flavor_name, cpu_count=1, ram=1024, root_disk=1,
                      check=True):
        """Step to create flavor."""
        page_flavors = self.page_flavors()
        page_flavors.button_create_flavor.click()

        with page_flavors.form_create_flavor as form:
            form.field_name.value = flavor_name
            form.field_vcpus.value = cpu_count
            form.field_ram.value = ram
            form.field_root_disk.value = root_disk
            form.submit()

        if check:
            self.close_notification('success')
            page_flavors.table_flavors.row(
                name=flavor_name).wait_for_presence()

    @pom.timeit('Step')
    def delete_flavor(self, flavor_name, check=True):
        """Step to delete flavor."""
        page_flavors = self.page_flavors()

        with page_flavors.table_flavors.row(
                name=flavor_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_flavors.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_flavors.table_flavors.row(
                name=flavor_name).wait_for_absence()

    @pom.timeit('Step')
    def delete_flavors(self, flavor_names, check=True):
        """Step to delete flavors as batch."""
        page_flavors = self.page_flavors()

        for flavor_name in flavor_names:
            page_flavors.table_flavors.row(
                name=flavor_name).checkbox.select()

        page_flavors.button_delete_flavors.click()
        page_flavors.form_confirm.submit()

        if check:
            self.close_notification('success')
            for flavor_name in flavor_names:
                page_flavors.table_flavors.row(
                    name=flavor_name).wait_for_absence()

    @pom.timeit('Step')
    def update_flavor(self, flavor_name, new_flavor_name=None, check=True):
        """Step to update flavor."""
        page_flavors = self.page_flavors()
        page_flavors.table_flavors.row(
            name=flavor_name).dropdown_menu.item_default.click()

        with page_flavors.form_update_flavor as form:
            form.label_info.click()
            if new_flavor_name:
                form.field_name.value = new_flavor_name
            form.submit()

        if check:
            self.close_notification('success')
            page_flavors.table_flavors.row(
                name=new_flavor_name or flavor_name).wait_for_presence()

    @pom.timeit('Step')
    def update_metadata(self, flavor_name, metadata, check=True):
        """Step to update flavor metadata."""
        page_flavors = self.page_flavors()

        with page_flavors.table_flavors.row(
                name=flavor_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        with page_flavors.form_update_metadata as form:
            for metadata_name, metadata_value in metadata.items():
                form.field_metadata_name.value = metadata_name
                form.button_add_metadata.click()
                form.list_metadata.row(
                    metadata_name).field_metadata_value.value = metadata_value

            form.submit()

        if check:
            page_flavors.table_flavors.row(
                name=flavor_name).wait_for_presence()

    @pom.timeit('Step')
    def get_metadata(self, flavor_name):
        """Step to get flavor metadata."""
        metadata = {}

        page_flavors = self.page_flavors()

        with page_flavors.table_flavors.row(
                name=flavor_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_update_metadata.click()

        for row in page_flavors.form_update_metadata.list_metadata.rows:
            metadata[row.field_metadata_name.value] = \
                row.field_metadata_value.value

        page_flavors.form_update_metadata.cancel()

        return metadata

    @pom.timeit('Step')
    def modify_access(self, flavor_name, project, check=True):
        """Step to modify flavor access."""
        page_flavors = self.page_flavors()

        with page_flavors.table_flavors.row(
                name=flavor_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_modify_access.click()

        with page_flavors.form_update_flavor as form:
            form.label_access.click()
            form.list_available_projects.row(project).button_add.click()
            form.submit()

        if check:
            self.close_notification('success')
            page_flavors.table_flavors.row(
                name=flavor_name).wait_for_presence()
