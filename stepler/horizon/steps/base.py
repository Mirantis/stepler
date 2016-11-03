"""
------------------
Horizon base steps
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

from hamcrest import assert_that, equal_to  # noqa

from stepler.third_party import steps_checker


class BaseSteps(object):
    """Base steps."""

    def __init__(self, app):
        """Constructor.

        Arguments:
            - app: horizon application instance.
        """
        self.app = app

    def _open(self, page):
        current_page = self.app.current_page
        if page.__class__ != current_page.__class__:

            if getattr(page, 'navigate_items', None):
                current_page.navigate(page.navigate_items)

            else:
                page.open()

        return page

    @steps_checker.step
    def switch_project(self, project_name, check=True):
        """Switch project in user account.

        Arguments:
            - project_name: string, name of project.
        """
        with self.app.page_base.dropdown_menu_project as menu:

            if menu.label_project.value == project_name:
                self.app.current_project = project_name
                return

            menu.click()
            menu.item_project(project_name).click()
            self.app.current_project = project_name

        if check:
            self.close_notification('success')
            assert_that(menu.label_project.value, equal_to(project_name))

    @steps_checker.step
    def close_notification(self, level, check=True):
        """Close notification popup window.

        Arguments:
            - level: string, level of popup: "success", "info", "error".
        """
        self.app.page_base.modal.wait_for_absence()
        with self.app.page_base.notification(level) as popup:
            popup.button_close.click()
            if check:
                popup.wait_for_absence()

    @steps_checker.step
    def refresh_page(self, check=True):
        """Step to refresh page."""
        url = self.app.page_base.url
        self.app.page_base.refresh()

        if check:
            assert_that(self.app.page_base.url, equal_to(url))
