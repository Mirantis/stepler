"""
------------------------------
Object Storage container steps
------------------------------
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

import boto3
from hamcrest import (assert_that, empty, is_in, is_not, has_items,
                      has_entries, equal_to)  # noqa H301

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['ContainerSwiftSteps', 'ContainerCephSteps']


class ContainerSwiftSteps(base.BaseSteps):
    """Swift container steps."""

    @steps_checker.step
    def create(self, name, check=True):
        """Step to create container and check it exists in containers list.

        Args:
            name (str): container name
            check (bool, optional): flag whether to check this step or not

        Returns:
            dict: created container

        Raises:
            AssertionError: if check failed
        """
        self._client.put_container(name)
        container = self.get(name, check=check)
        if check:
            self.check_presence(name)
        return container

    @steps_checker.step
    def get(self, name, check=True):
        """Step to get container by name.

        Args:
            name (str): container name
            check (bool, optional): flag whether to check this step or not

        Returns:
            dict: container

        Raises:
            AssertionError: if container dict is empty
        """
        container, _ = self._client.get_container(name)
        if check:
            assert_that(container, is_not(empty()))
        return container

    @steps_checker.step
    def delete(self, name, check=True):
        """Step to delete container by name.

        Args:
            name (str): container name
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if container is not deleted
        """
        self._client.delete_container(name)
        if check:
            self.check_presence(name, must_present=False)

    @steps_checker.step
    def check_presence(self, name, must_present=True):
        """Step to check container presence.

        Args:
            name (str): container name
            must_present (bool, optional): flag whether container should exist
                or not

        Raises:
            AssertionError: if check failed
        """
        _, containers = self._client.get_container('', full_listing=True)
        matcher = has_items(has_entries(name=name))
        if not must_present:
            matcher = is_not(matcher)
        assert_that(containers, matcher)

    @steps_checker.step
    def put_object(self, container_name, object_name, content, check=True):
        """Step to put object to container.

        Args:
            container_name (str): container name
            object_name (str): object name
            content (str): content to put
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if object is not present in container
        """
        self._client.put_object(container_name, object_name, content)
        if check:
            self.check_object_presence(container_name, object_name)

    @steps_checker.step
    def get_object(self, container_name, object_name, check=True):
        """Step to get (download) object from container.

        Args:
            container_name (str): container name
            object_name (str): object name
            check (bool, optional): flag whether to check this step or not

        Returns:
            str: object content
        """
        _, content = self._client.get_object(container_name, object_name)
        if check:
            assert_that(content, is_not(empty()))
        return content

    @steps_checker.step
    def delete_object(self, container_name, object_name, check=True):
        """Step to delete object from container.

        Args:
            container_name (str): container name
            object_name (str): object name
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if object is present in container after deleting
        """
        self._client.delete_object(container_name, object_name)
        if check:
            self.check_object_presence(container_name, object_name,
                                       must_present=False)

    @steps_checker.step
    def check_object_presence(self, container_name, object_name,
                              must_present=True):
        """Step to check object presence.

        Args:
            container_name (str): container name
            object_name (str): object name
            must_present (bool, optional): flag whether object should exist or
                not

        Raises:
            AssertionError: if check failed
        """
        _, objects = self._client.get_container(container_name,
                                                full_listing=True)
        matcher = has_items(has_entries(name=object_name))
        if not must_present:
            matcher = is_not(matcher)
        assert_that(objects, matcher)

    @steps_checker.step
    def check_object_content(self, container_name, object_name,
                             expected_content):
        """Step to check object content.

        Args:
            container_name (str): container name
            object_name (str): object name
            expected_content (str): expected content

        Raises:
            AssertionError: if object content is not equal to expected content
        """
        content = self.get_object(container_name, object_name)
        assert_that(content, equal_to(expected_content))


class ContainerCephSteps(base.BaseSteps):
    """Ceph container steps."""

    @steps_checker.step
    def connect_s3(self, ec2_creds, check=True):
        """Step to connect to s3.

        Args:
            ec2_creds (dict): ec2 credentials dict
            check (bool, optional): flag whether to check this step or not
        """
        auth_url = config.AUTH_URL.rsplit(':')
        endpoint_url = '{}:{}'.format(auth_url[0], auth_url[1])
        s3 = boto3.client('s3',
                          aws_access_key_id=ec2_creds.access,
                          aws_secret_access_key=ec2_creds.secret,
                          endpoint_url='{}:8080'.format(endpoint_url))
        return s3

    @steps_checker.step
    def create(self, session, container_name, check=True):
        """Step to create container.

        Args:
            session: module to connect to s3
            container_name (str): container name
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        bucket = session.create_bucket(Bucket=container_name)
        if check:
            self.check_radow_container_presence(session, bucket)
        return bucket

    @steps_checker.step
    def list(self, session, check=True):
        """Step to list all containers.

        Args:
            session: module to connect to s3
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        containers_name_list = session.list_buckets()
        if check:
            assert_that(containers_name_list, is_not(empty()))
        return containers_name_list

    @steps_checker.step
    def check_radow_container_presence(self, session, bucket,
                                       must_present=True):
        """Step to check container presents in containers list.

        Args:
            session: module to connect to s3
            bucket (obj): container object
            must_present (bool, optional): flag whether container should exist
                or not

        Raises:
            AssertionError: if check failed
        """
        containers_name_list = self.list(session)
        if must_present:
            assert_that(bucket, is_in(containers_name_list['Buckets']))
        else:
            assert_that(bucket, is_not(is_in(containers_name_list['Buckets'])))

    @steps_checker.step('c1ec8c55-3698-4c5a-97bc-3e4205066948')
    def put_object_radow(self, session, container_name, key, check=True):

        """Step to put object to container.

         Args:
            session: module to connect to s3
            container_name (str): container name
            key(str): key of object
            check (bool, optional): flag whether to check this step or not

         Raises:
            AssertionError: if check failed
        """
        session.put_object(Bucket=container_name, Key=key)
        if check:
            session.list_objects(Bucket=container_name)

    @steps_checker.step('69be0793-47f8-43a0-bb9b-27e467b1aa2a')
    def delete_object_from_container_radow(self, session, container_name,
                                           check=True):
        """Step to put object to container.

         Args:
            session: module to connect to s3
            container_name (str): container name
            key(str): key of object
            check (bool, optional): flag whether to check this step or not

         Raises:
            AssertionError: if check failed
        """
        page = session.get_paginator('list_objects')
        for page in page.paginate(Bucket=container_name):
            keys = [{'Key': obj['Key']} for obj in page.get('Contents', [])]
            if keys:
                session.delete_objects(Bucket=container_name,
                                       Delete={'Objects': keys})
        if check:
            assert_that('Contents', is_not(is_in(session.list_objects(
                Bucket=container_name))))
