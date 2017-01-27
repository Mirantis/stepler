"""
--------------
RabbitMQ steps
--------------
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

import re

from hamcrest import assert_that, is_, has_items, calling, raises  # noqa
import pika

from stepler.third_party import steps_checker

__all__ = [
    'RabbitMQSteps'
]


class RabbitMQSteps(object):
    """RabbitMQ steps."""

    @steps_checker.step
    def check_cluster_status(self, cluster_status, cluster_node_names,
                             disabled_nodes_number=0):
        """Step to check status of RabbitMQ cluster.

        Cluster status is checked by 'rabbitmqctl cluster_status'.
        Example of its output:
        Cluster status of node rabbit@ctl03 ...
        [{nodes,[{disc,[rabbit@ctl01,rabbit@ctl02,rabbit@ctl03]}]},
        {running_nodes,[rabbit@ctl02,rabbit@ctl03]},
        {cluster_name,<<"openstack">>},
        {partitions,[]},
        {alarms,[{rabbit@ctl02,[]},{rabbit@ctl03,[]}]}]

        This step checks that:
        - list of nodes is equal to expected one (from config file)
        - list of running nodes is subset of list of all nodes
        - number of running nodes <= number of all nodes
        (depending on disabled_nodes_number)

        Args:
            cluster_status (str): output of rabbitmqctl
            cluster_node_names (list): names of cluster nodes
            disabled_nodes_number (int): number of nodes where RabbitMQ is
                stopped
            check (bool, optional): flag whether to check step or not

        Raises:
            AssertionError: if hosts list is empty
        """
        lines = cluster_status.split('\n')
        all_nodes = re.findall(r'(\w+@\w+)', lines[1])
        running_nodes = re.findall(r'(\w+@\w+)', lines[2])
        assert_that(sorted(all_nodes), is_(sorted(cluster_node_names)))
        assert_that(all_nodes, has_items(*running_nodes))
        assert_that(len(all_nodes) - disabled_nodes_number,
                    is_(len(running_nodes)))

    def _connect(self, ip_address):
        # connection to RabbitMQ server
        parameters = pika.ConnectionParameters(host=ip_address)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        return channel

    @steps_checker.step
    def check_traffic_disabled_ip(self, ip_address):
        """Step to check traffic on disabled RabbitMQ server.

         This step checks that connection to stopped RabbitMQ server is
         impossible.

         Args:
             ip_address (str): IP address of RabbitMQ server

         Raises:
             AssertionError: if no exceptions during connection
         """
        assert_that(
            calling(self._connect).with_args(ip_address=ip_address),
            raises(pika.exceptions.ConnectionClosed))

    @steps_checker.step
    def check_traffic_enabled_ip(self, main_ip_address, ip_addresses):
        """Step to check traffic on RabbitMQ server.

        This step connects to RabbitMQ server, creates a queue, sends several
        messages to it and disconnects. Then it connects to every available
        RabbitMQ server, gets messages from the queue and checks them.

        Args:
            ip_address (str): IP address of RabbitMQ server
            ip_addresses (list): IP addresses of available RabbitMQ servers

        Raises:
            ConnectionClosed: if any problems of pika operations
            AssertionError: if wrong message content
        """
        channel = self._connect(main_ip_address)

        # create a queue
        queue_name = main_ip_address
        channel.queue_declare(queue=queue_name)

        # send messages
        messages = []
        for i in range(len(ip_addresses)):
            message = 'message-{}-{}'.format(main_ip_address, i)
            channel.basic_publish(exchange='',
                                  routing_key=queue_name,
                                  body=message)
            messages.append(message)
        channel.connection.close()

        # check messages
        for ip_address in ip_addresses:
            channel = self._connect(ip_address)
            message = channel.basic_get(queue=queue_name, no_ack=True)
            assert_that(message[2], is_(messages.pop(0)))
            channel.connection.close()

        # delete queue
        channel = self._connect(main_ip_address)
        channel.queue_delete(queue=queue_name)
        channel.connection.close()

    @steps_checker.step
    def check_traffic(self, ip_addresses, disabled_ip_address=None):
        """Step to check traffic on all RabbitMQ servers.

        This step checks sending/receiving messages between running RabbitMQ
        servers. For stopped server, it checks connection to it.

        Args:
            ip_addresses (list): IP addresses of available RabbitMQ servers
            disabled_ip_address (str): IP address of stopped RabbitMQ server
        """
        ip_addresses_enabled = list(ip_addresses)
        if disabled_ip_address:
            self.check_traffic_disabled_ip(disabled_ip_address)
            ip_addresses_enabled.remove(disabled_ip_address)

        for ip_address in ip_addresses_enabled:
            self.check_traffic_enabled_ip(ip_address, ip_addresses_enabled)
