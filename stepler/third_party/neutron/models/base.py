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


class BaseNeutronManager(object):
    """Base Neutron components manager."""

    def __init__(self, neutron_client):
        """Init base neutron manager

        Args:
            client (obj): initialized client wrapper (for access to another
                managers)
            neutron_client (obj): initialized neutronclient object
        """
        self._neutron_client = neutron_client

    @property
    def _name(self):
        return self.__class__.__name__.split('Manager')[0].lower()

    @property
    def _create_method(self):
        """Returns resource create callable."""
        methodname = 'create_{}'.format(self._name)
        return getattr(self._neutron_client, methodname)

    @property
    def _delete_method(self):
        """Returns resource delete callable."""
        methodname = 'delete_{}'.format(self._name)
        return getattr(self._neutron_client, methodname)

    @property
    def _list_method(self):
        """Returns resource list callable."""
        methodname = 'list_{}s'.format(self._name)
        return getattr(self._neutron_client, methodname)

    @property
    def _show_method(self):
        """Returns resource show callable."""
        methodname = 'show_{}'.format(self._name)
        return getattr(self._neutron_client, methodname)

    def create(self, **kwargs):
        """Base create."""
        query = {self._name: kwargs}
        obj = self._create_method(query)[self._name]
        return obj

    def delete(self, obj_id):
        """Base delete."""
        self._delete_method(obj_id)

    def list(self):
        """Base list (retrive all)."""
        return self.find_all()

    def find_all(self, **kwargs):
        """Return a list of objects by conditions.

        Results may be empty.
        """
        objs = self._list_method(**kwargs)[self._name + 's']
        return objs

    def find(self, **kwargs):
        """Return one found object.

        Raises LookupError if object is absent, or if there is more than one
        object is found.
        """
        objs = self._list_method(**kwargs)[self._name + 's']
        if len(objs) == 0:
            raise LookupError("{} with {!r} is absent".format(self._name,
                                                              kwargs))
        if len(objs) > 1:
            raise LookupError("Founded more than one {} with {!r}".format(
                self._name, kwargs))
        return objs[0]

    def get(self, obj_id):
        """Return object by id."""
        return self._show_method(obj_id)[self._name]
