"""
------------------
Volume types steps
------------------
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


class VolumeTypesSteps(base.BaseSteps):
    """Volume types steps."""

    def _tab_volume_types(self):
        """Open volume types tab."""
        with self._open(self.app.page_admin_volumes) as page:
            page.label_volume_types.click()
            return page.tab_volume_types

    @steps_checker.step
    def create_volume_type(self, volume_type_name=None, description=None,
                           check=True):
        """Step to create volume type."""
        volume_type_name = (volume_type_name or
                            next(utils.generate_ids('volume-type')))

        tab = self._tab_volume_types()
        tab.button_create_volume_type.click()

        with tab.form_create_volume_type as form:
            form.field_name.value = volume_type_name
            if description:
                form.field_description.value = description
            form.submit()

        if check:
            self.close_notification('success')
            tab.table_volume_types.row(
                name=volume_type_name).wait_for_presence()

        return volume_type_name

    @steps_checker.step
    def delete_volume_type(self, volume_type_name, check=True):
        """Step to delete volume type."""
        tab = self._tab_volume_types()

        with tab.table_volume_types.row(
                name=volume_type_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        tab.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab.table_volume_types.row(
                name=volume_type_name).wait_for_absence()

    @steps_checker.step
    def delete_volume_types(self, volume_type_names, check=True):
        """Step to delete volume types."""
        tab = self._tab_volume_types()

        for volume_type_name in volume_type_names:
            tab.table_volume_types.row(name=volume_type_name).checkbox.click()

        tab.button_delete_volume_types.click()
        tab.confirm_form.submit()

        if check:
            self.close_notification('success')
            for volume_type_name in volume_type_names:
                tab.table_volume_types.row(
                    name=volume_type_name).wait_for_absence()

    @steps_checker.step
    def create_qos_spec(self, qos_spec_name=None, consumer=None, check=True):
        """Step to create qos spec."""
        qos_spec_name = qos_spec_name or next(utils.generate_ids('qos-spec'))

        tab = self._tab_volume_types()
        tab.button_create_qos_spec.click()

        with tab.form_create_qos_spec as form:
            form.field_name.value = qos_spec_name
            if consumer:
                form.field_consumer.value = consumer
            form.submit()

        if check:
            self.close_notification('success')
            tab.table_qos_specs.row(name=qos_spec_name).wait_for_presence()

        return qos_spec_name

    @steps_checker.step
    def delete_qos_spec(self, qos_spec_name, check=True):
        """Step to delete qos spec."""
        tab = self._tab_volume_types()

        with tab.table_qos_specs.row(
                name=qos_spec_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        tab.form_confirm.submit()

        if check:
            self.close_notification('success')
            tab.table_qos_specs.row(name=qos_spec_name).wait_for_absence()
