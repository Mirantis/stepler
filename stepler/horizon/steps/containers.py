"""
----------------
Containers steps
----------------
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

from hamcrest import assert_that, contains_string, equal_to  # noqa
import requests

from stepler.horizon.steps import base
from stepler.third_party import steps_checker


class ContainersSteps(base.BaseSteps):
    """Containers steps."""

    def _page_containers(self):
        """Open containers page if it isn't opened."""
        return self._open(self.app.page_containers)

    @steps_checker.step
    def create_container(self, container_name, public=False, check=True):
        """Step to create container."""
        page_containers = self._page_containers()
        page_containers.button_create_container.click()

        with page_containers.form_create_container as form:
            form.field_name.value = container_name

            if public:
                form.checkbox_public.select()
            else:
                form.checkbox_public.unselect()

            form.submit()

        if check:
            self.close_notification('success')
            page_containers.list_containers.row(
                container_name).wait_for_presence()

    @steps_checker.step
    def delete_container(self, container_name, check=True):
        """Step to delete container."""
        page_containers = self._page_containers()

        with page_containers.list_containers.row(container_name) as row:
            row.click()
            row.button_delete_container.click()

        page_containers.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_containers.list_containers.row(
                container_name).wait_for_absence()

    def __enter__(self):
        """Enter to context manager."""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Exit from context manager."""
        self._callback()

    @steps_checker.step
    def get_container(self, container_name):
        """Step to enter to container."""
        self.app.page_containers.list_containers.row(container_name).click()

        def exit(self=self):
            self.app.page_containers.list_containers.row(
                container_name).click()

        self._callback = exit
        return self

    @steps_checker.step
    def get_folder(self, folder_name):
        """Step to enter to folder."""
        self.app.page_containers.table_objects.row(
            name=folder_name).link_folder.click()

        def exit(self=self):
            self.app.page_containers.back()

        self._callback = exit
        return self

    @steps_checker.step
    def create_folder(self, folder_name, check=True):
        """Step to create folder."""
        with self.app.page_containers as page:
            page.button_create_folder.click()

            with page.form_create_folder as form:
                form.field_name.value = folder_name
                form.submit()

        if check:
            self.close_notification('success')
            self.app.page_containers.table_objects.row(
                name=folder_name).wait_for_presence()

    @steps_checker.step
    def delete_folder(self, folder_name, check=True):
        """Step to delete folder."""
        with self.app.page_containers as page:
            page.table_objects.row(
                name=folder_name).button_delete.click()
            # Confirm deleting
            page.form_confirm.submit(modal_absent=False)
            # Close modal
            page.form_confirm.submit()

        if check:
            self.app.page_containers.table_objects.row(
                name=folder_name).wait_for_absence()

    @steps_checker.step
    def get_container_info(self, container_name):
        """Step to get container info."""
        with self.app.page_containers.list_containers.row(
                container_name) as row:
            container_info = {
                'objects_count': row.label_objects_count.value,
                'size': row.label_size.value,
                'created_date': row.label_created_date.value,
                'public_url': row.link_public_url.href}
            return container_info

    @steps_checker.step
    def upload_file(self, file_path, file_name=None, check=True):
        """Step to upload file."""
        self.app.page_containers.button_upload_file.click()

        with self.app.page_containers.form_upload_file as form:
            form.field_file.value = file_path

            if file_name:
                form.field_name.value = file_name

            file_name = form.field_name.value
            form.submit()

        if check:
            self.close_notification('success')
            self.app.page_containers.table_objects.row(
                name=file_name).wait_for_presence()

        return file_name

    @steps_checker.step
    def delete_file(self, file_name, check=True):
        """Step to delete file."""
        with self.app.page_containers.table_objects.row(
                name=file_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        # Confirm deleting
        self.app.page_containers.form_confirm.submit(modal_absent=False)
        # Close modal
        self.app.page_containers.form_confirm.submit()

        if check:
            self.app.page_containers.table_objects.row(
                name=file_name).wait_for_absence()

    @steps_checker.step
    def check_folder_avaiable_by_public_url(self, folder_name, public_url):
        """Step to check that folder is available by public URL."""
        assert_that(requests.get(public_url).text,
                    contains_string(folder_name))

    @steps_checker.step
    def check_container_name_volume_backups(self):
        """Step to check that container has name 'volumebackups'."""
        page_containers = self._page_containers()
        page_containers.list_containers.wait_for_presence()
        container_name = page_containers.item_container_name()
        assert_that('volumebackups', equal_to(container_name))
