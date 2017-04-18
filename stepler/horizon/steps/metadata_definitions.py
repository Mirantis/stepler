"""
--------------------------
Metadata definitions steps
--------------------------
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


NAMESPACE_TEMPLATE = '''{
    "namespace": "%(name)s",
    "display_name": "%(name)s",
    "description": "Namespace description",
    "resource_type_associations": [
        {
            "name": "OS::Nova::Flavor"
        },
        {
            "name": "OS::Glance::Image"
        }
    ],
    "properties": {
        "prop1": {
            "default": "20",
            "type": "integer",
            "description": "More info here",
            "title": "My property1"
        }
    }
}'''


class NamespacesSteps(base.BaseSteps):
    """Namespaces steps."""

    def _page_metadata_definitions(self):
        """Open namespaces page if it isn't opened."""
        return self._open(self.app.page_metadata_definitions)

    @steps_checker.step
    def create_namespace(self, namespace_name=None,
                         namespace_source='Direct Input',
                         check=True):
        """Step to create namespace."""
        namespace_name = (namespace_name or
                          next(utils.generate_ids('namespace')))

        page_metadata_definitions = self._page_metadata_definitions()
        page_metadata_definitions.button_import_namespace.click()

        with page_metadata_definitions.form_import_namespace as form:
            form.combobox_namespace_source.value = namespace_source
            form.field_namespace_json.value = \
                NAMESPACE_TEMPLATE % {'name': namespace_name}
            form.submit()

        if check:
            self.close_notification('success')
            page_metadata_definitions.table_namespaces.row(
                name=namespace_name).wait_for_presence()

        return namespace_name

    @steps_checker.step
    def delete_namespace(self, namespace_name, check=True):
        """Step to delete namespace."""
        page_metadata_definitions = self._page_metadata_definitions()

        with page_metadata_definitions.table_namespaces.row(
                name=namespace_name).dropdown_menu as menu:
            menu.button_toggle.click()
            menu.item_delete.click()

        page_metadata_definitions.form_confirm.submit()

        if check:
            self.close_notification('success')
            page_metadata_definitions.table_namespaces.row(
                name=namespace_name).wait_for_absence()
