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

import functools


class Resource(dict):
    """Base class for neutron resource.

    It will be helpful on comparsion operations.

    Example:
        >>> a = dict(id=1, state='active')
        >>> b = dict(id=1, state='available')
        >>> ar = Resource(a)
        >>> br = Resource(b)

        >>> a == b
        False
        >>> ar == br
        True
        >>> a in [b]
        False
        >>> ar in [br]
        True
    """

    def __repr__(self):
        return u'<{}: {}>'.format(self.__class__.__name__,
                                  super(Resource, self).__repr__())

    def __hash__(self):
        if 'id' in self:
            return hash(self['id'])
        else:
            return super(Resource, self).__hash__()

    def __eq__(self, other):
        if 'id' in other and 'id' in self:
            return self['id'] == other['id']
        else:
            return self == other


def transform_one(f):
    """Decorator to transform single dict to Resource."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        return self._make_resource(result)
    return wrapper


def transform_many(f):
    """Decorator to transform list of dicts to list of Resource instances."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        return [self._make_resource(item) for item in result]
    return wrapper


def filter_by_project(f):
    """Decorator to filter list of objects by current project."""
    @functools.wraps(f)
    def wrapper(self, current_project_only=True, *args, **kwargs):
        result = f(self, *args, **kwargs)
        if current_project_only:
            current_project_id = self._rest_client.get_auth_info()[
                'auth_tenant_id']
            filtered_objs = []
            for item in result:
                if current_project_id in (item.get('project_id'),
                                          item.get('tenant_id')):
                    filtered_objs.append(item)
            result = filtered_objs
        return result
    return wrapper


class BaseNeutronManager(object):
    """Base Neutron components manager."""

    NAME = ''
    API_NAME = None
    _resource_class = Resource

    def __init__(self, client):
        """Init base neutron manager

        Args:
            client (obj): initialized client wrapper (for access to another
                managers)
        """
        self.client = client
        self._rest_client = self.client._rest_client

    def _make_resource(self, result):
        resource = self._resource_class(result)
        resource.client = self.client
        return resource

    @property
    def _create_method(self):
        """Returns resource create callable."""
        methodname = 'create_{}'.format(self.API_NAME or self.NAME)
        return getattr(self._rest_client, methodname)

    @property
    def _delete_method(self):
        """Returns resource delete callable."""
        methodname = 'delete_{}'.format(self.API_NAME or self.NAME)
        return getattr(self._rest_client, methodname)

    @property
    def _list_method(self):
        """Returns resource list callable."""
        methodname = 'list_{}s'.format(self.API_NAME or self.NAME)
        return getattr(self._rest_client, methodname)

    @property
    def _show_method(self):
        """Returns resource show callable."""
        methodname = 'show_{}'.format(self.API_NAME or self.NAME)
        return getattr(self._rest_client, methodname)

    @property
    def _update_method(self):
        """Returns resource update callable."""
        methodname = 'update_{}'.format(self.API_NAME or self.NAME)
        return getattr(self._rest_client, methodname)

    @transform_one
    def create(self, **kwargs):
        """Base create."""
        query = {self.NAME: kwargs}
        obj = self._create_method(query)[self.NAME]
        return obj

    def update(self, obj_id, **kwargs):
        """Base update."""
        query = {self.NAME: kwargs}
        return self._update_method(obj_id, query)[self.NAME]

    def delete(self, obj_id):
        """Base delete."""
        self._delete_method(obj_id)

    @transform_many
    def list(self):
        """Base list (retrive all)."""
        return self.find_all()

    @transform_many
    def find_all(self, **kwargs):
        """Returns a list of objects by conditions.

        Results may be empty.
        """
        objs = self._list_method(**kwargs)[self.NAME + 's']
        return objs

    @transform_one
    def find(self, **kwargs):
        """Returns one found object.

        Raises LookupError if object is absent, or if there is more than one
        object found.
        """
        objs = self._list_method(**kwargs)[self.NAME + 's']
        if len(objs) == 0:
            raise LookupError("{} with {!r} is absent".format(self.NAME,
                                                              kwargs))
        if len(objs) > 1:
            raise LookupError("Founded more than one {} with {!r}".format(
                self.NAME, kwargs))
        return objs[0]

    @transform_one
    def get(self, obj_id):
        """Return object by id."""
        return self._show_method(obj_id)[self.NAME]
