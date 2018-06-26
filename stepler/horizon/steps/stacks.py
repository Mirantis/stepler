"""
------------
Stacks steps
------------
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

from hamcrest import assert_that, equal_to, less_than  # noqa

from stepler import config
from stepler.horizon.steps import base
from stepler.third_party import steps_checker
from stepler.third_party import utils


class StacksSteps(base.BaseSteps):
    """Stacks steps."""

    def _page_stacks(self):
        """Open stacks page if it isn't opened."""
        return self._open(self.app.page_stacks)

    @steps_checker.step
    def create_stack(self, stack_name, admin_password,
                     keypair, template_source='Direct Input',
                     env_source='Direct Input',
                     flavor=config.FLAVOR_EXTRA_TINY,
                     image=config.HORIZON_TEST_IMAGE_CIRROS, check=True):
        """Step to create stack."""
        page_stacks = self._page_stacks()

        stack_name = stack_name or next(utils.generate_ids())
        page_stacks.button_create_stack.click()

        with page_stacks.form_create_stack as form:
            form.combobox_template_source.value = template_source
            if template_source == 'Direct Input':
                form.field_template_data.value = (
                    config.HORIZON_STACK_SOURCE)
            form.combobox_env_source.value = env_source
            if env_source == 'Direct Input':
                form.field_env_data.value = config.HORIZON_STACK_ENV_SOURCE

            form.submit()

        with page_stacks.form_launch_stack as form:
            form.field_name.value = stack_name
            form.field_admin_password.value = admin_password
            form.checkbox_rollback.select()
            form.field_flavor.value = flavor
            form.field_image.value = image
            form.field_key.value = keypair.name

            form.submit()

        if check:
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_presence()
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_status('Create In Progress')

    @steps_checker.step
    def delete_stack(self, stack, check=True):
        """Step to delete stack."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_stacks.form_confirm_delete.submit()

        if check:
            self.close_notification('success')
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def delete_stacks(self, stacks, check=True):
        """Step to delete stacks."""
        page_stacks = self._page_stacks()
        stack_names = [stack.stack_name for stack in stacks]

        for stack_name in stack_names:
            page_stacks.table_stacks.row(
                name=stack_name).checkbox.select()

        page_stacks.button_delete_stacks.click()

        page_stacks.form_confirm_delete.wait_for_presence()
        page_stacks.form_confirm_delete.submit()

        if check:
            self.close_notification('success')
            for stack_name in stack_names:
                page_stacks.table_stacks.row(
                    name=stack_name).wait_for_absence(config.EVENT_TIMEOUT)

    @steps_checker.step
    def view_stack(self, stack, check=True):
        """Step to view stack."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        page_stacks.table_stacks.row(
            name=stack_name).webdriver.find_element_by_partial_link_text(
                stack_name).click()

        self.app.page_stack.stack_info_main.wait_for_presence()

        if check:
            self.app.page_stack.table_resource_topology.is_present

    @steps_checker.step
    def preview_stack(self, stack_name, template_source='Direct Input',
                      env_source='Direct Input', check=True):
        """Step to preview stack."""
        stack_name = stack_name or next(utils.generate_ids('stack'))
        page_stacks = self._page_stacks()
        page_stacks.button_preview_stack.click()

        with page_stacks.form_preview_template as form:
            form.combobox_template_source.value = template_source
            if template_source == 'Direct Input':
                form.field_template_data.value = (
                    config.HORIZON_STACK_SOURCE)
            form.combobox_env_source.value = env_source
            if env_source == 'Direct Input':
                form.field_env_data.value = config.HORIZON_STACK_ENV_SOURCE

            form.submit()

        with page_stacks.form_preview_stack as form:
            form.field_name.value = stack_name
            form.checkbox_rollback.select()

            form.submit()

        if check:
            page_stacks.form_example_stack.is_present
            page_stacks.form_example_stack.button_cancel.click()

    @steps_checker.step
    def check_stack(self, stack, check=True):
        """Step to check stack status."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.item_default.click()

        if check:
            self.close_notification('success')
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_status('Check Complete')

    @steps_checker.step
    def suspend_stack(self, stack, check=True):
        """Step to suspend stack."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_suspend_stack.click()

        if check:
            self.close_notification('success')
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_status('Suspend Complete')

    @steps_checker.step
    def resume_stack(self, stack, check=True):
        """Step to resume stack."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_resume_stack.click()

        if check:
            self.close_notification('success')
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_status('Resume Complete')

    @steps_checker.step
    def change_stack_template(self, stack, admin_password,
                              env_data=config.HORIZON_STACK_ENV_SOURCE,
                              template_data=config.HORIZON_STACK_SOURCE,
                              template_source='Direct Input',
                              env_source='Direct Input',
                              new_flavor='m1.tiny_test',
                              new_image='TestCirros-0.3.5',
                              new_keypair='test', check=True):
        """Step to change stack template."""
        page_stacks = self._page_stacks()
        stack_name = stack.stack_name

        with page_stacks.table_stacks.row(
                name=stack_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_change_template.click()

        with page_stacks.form_change_template as form:
            form.combobox_template_source.value = template_source
            if template_source == 'Direct Input':
                form.field_template_data.value = template_data
            form.combobox_env_source.value = env_source
            if env_source == 'Direct Input':
                form.field_env_data.value = env_data

            form.submit()

        with page_stacks.form_update_stack as form:
            form.field_admin_password.value = admin_password
            form.field_flavor.value = new_flavor
            form.field_image.value = new_image
            form.field_key.value = new_keypair

            form.button_submit.click()

        if check:
            page_stacks.table_stacks.row(
                name=stack_name).wait_for_presence()
