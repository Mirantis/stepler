"""
---------------
os_faults steps
---------------
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

import collections
import os
import re
import tempfile
import time
import warnings

from hamcrest import (assert_that, empty, equal_to, has_item, has_properties,
                      is_not, only_contains, has_items, has_entries,
                      has_length, is_, contains_inanyorder, is_in, any_of,
                      all_of, contains_string, greater_than,
                      less_than_or_equal_to)  # noqa H301
from os_faults.ansible.executor import AnsibleExecutionException
from os_faults.api.node_collection import NodeCollection
from six import moves

from stepler import base
from stepler import config
from stepler.third_party import network_checks
from stepler.third_party import steps_checker
from stepler.third_party import tcpdump
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ['OsFaultsSteps']


class OsFaultsSteps(base.BaseSteps):
    """os-faults steps."""

    @steps_checker.step
    def get_cloud_param_value(self, param_name):
        """Step to get value of a cloud management parameter.

        Args:
            param_name (str): parameter name

        Returns:
            str: parameter value

        Raises:
            AttributeError: if wrong parameter name
        """
        if param_name == 'driver':
            value = self._client.get_driver_name()
        else:
            value = getattr(self._client, param_name)
        return value

    @steps_checker.step
    def get_nodes(self, fqdns=None, service_names=None, check=True):
        """Step to get nodes.

        If ``fqdns`` and ``service_names`` are not ``None``
        simultaneously, then the intersection of nodes with fqdns and
        nodes with all required services will be returned.

        Args:
            fqdns (list): nodes hostnames to filter
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            NodeCollection: one or more nodes
        """
        nodes = self._client.get_nodes(fqdns=fqdns)
        for service_name in service_names or []:
            nodes &= self._client.get_service(service_name).get_nodes()

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @steps_checker.step
    def get_node(self, fqdns=None, service_names=None, check=True):
        """Step to get one node.

        Args:
            fqdns (list): nodes hostnames to filter
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            NodeCollection: one node
        """
        nodes = self.get_nodes(
            fqdns=fqdns, service_names=service_names, check=check)
        return nodes.pick()

    @steps_checker.step
    def get_nodes_with_any_service(self, service_names, check=True):
        """Step to get nodes with running services.

        Unlike get_nodes, it returns nodes with at least one required service.

        Args:
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            NodeCollection: one or more nodes
        """
        nodes = self._client.get_service(service_names[0]).get_nodes()
        for service_name in service_names[1:]:
            nodes |= self._client.get_service(service_name).get_nodes()

        if check:
            assert_that(nodes, is_not(empty()))
        return nodes

    @steps_checker.step
    def get_service(self, name, check=True):
        """Step to get services.

        Args:
            name (str): service name
            check (bool): flag whether check step or not

        Returns:
            object: service
        """
        service = self._client.get_service(name=name)

        if check:
            assert_that(service, is_not(None))

        return service

    @steps_checker.step
    def get_services_names(self, name_prefix, check=True):
        """Step to get services names by name_prefix.

        Args:
            name_prefix (str): services name prefix
            check (bool): flag whether to check step or not

        Returns:
            list: service names
        """
        names = self._client.list_supported_services()
        names = [name for name in names if name.startswith(name_prefix)]
        if check:
            assert_that(names, is_not(empty()))
        return names

    @steps_checker.step
    def check_service_state(self, service_name, nodes, must_run=True,
                            timeout=0):
        """Verify step to check that service is running or not on nodes.

        Args:
            service_name (str): name of service
            nodes (obj): NodeCollection instance to check service state on it
            must_run (bool): flag whether service should be run on nodes or not
            timeout (int, optional): seconds to wait a result of check

        Raises:
            TimeoutExpired: if service state is wrong after timeout
        """
        service = self._client.get_service(service_name)

        def _check_service_state():
            matcher = has_items(*nodes)
            if not must_run:
                matcher = is_not(matcher)
            return waiter.expect_that(service.get_nodes(), matcher)

        waiter.wait(_check_service_state, timeout_seconds=timeout)

    @steps_checker.step
    def restart_service(self, name, nodes=None, check=True):
        """Step to restart service.

        Args:
            names (str): service name
            nodes (obj): NodeCollection instance to restart service on it
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
            AssertionError: if nodes don't contain service
        """
        nodes = nodes or self._client.get_nodes()
        service = self._client.get_service(name=name)
        running_nodes = service.get_nodes()
        to_restart_nodes = running_nodes & nodes
        if check:
            assert_that(to_restart_nodes, is_not(empty()))
        if to_restart_nodes:
            service.restart(nodes=to_restart_nodes)

    @steps_checker.step
    def restart_services(self, names, nodes=None, check=True):
        """Step to restart services.

        Args:
            names (list): service names
            nodes (obj): NodeCollection instance to restart service on it
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
        """
        for name in names:
            self.restart_service(name, nodes, check=check)

    @steps_checker.step
    def terminate_service(self, service_name, nodes, check=True):
        """Step to terminate service.

        Args:
            service_name (str): service name
            nodes (obj): NodeCollection instance to terminate service on it
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
        """
        service = self._client.get_service(service_name)
        service.terminate(nodes)
        if check:
            self.check_service_state(
                service_name,
                nodes,
                must_run=False,
                timeout=config.SERVICE_TERMINATE_TIMEOUT)

    @steps_checker.step
    def start_service(self, service_name, nodes, check=True):
        """Step to start service.

        Args:
            service_name (str): service name
            nodes (obj): NodeCollection instance to start service on it
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
        """
        service = self._client.get_service(service_name)
        service.start(nodes)
        if check:
            self.check_service_state(
                service_name,
                nodes,
                must_run=True,
                timeout=config.SERVICE_START_TIMEOUT)

    @steps_checker.step
    def get_nodes_private_key_path(self, check=True):
        """Step to retrieve private key for nodes.

        Args:
            check (bool): flag whether check step or not

        Returns:
            str: path to private key which is used for ssh to nodes

        Raises:
            AssertionError: if path to private key doesn't exist
        """
        private_key_path = self._client.private_key_file
        if check:
            assert_that(private_key_path, is_not(empty()))
            assert_that(os.path.exists(private_key_path))

        return private_key_path

    @steps_checker.step
    def download_file(self, node, file_path, check=True):
        """Step to download file from remote host to tempfile.

        Args:
            node (obj): node to fetch file from
            file_path (str): path to file on remote host
            check (bool): flag whether check step or not

        Returns:
            str: path to destination file

        Raises:
            ValueError: if destination file is not a regular file
            AssertionError: if file is empty
        """
        dest = tempfile.mktemp()
        task = {
            'fetch': {
                'src': file_path,
                'dest': dest,
                'flat': True,
            }
        }
        node.run_task(task)
        if check:
            if not os.path.isfile(dest):
                raise ValueError('{!r} is not a regular file'.format(dest))
            file_stat = os.stat(dest)
            assert_that(file_stat.st_size, is_not(0))
        return dest

    @steps_checker.step
    def upload_file(self, node, local_path, remote_path=None, check=True):
        """Step to upload file from local host to remote nodes.

        Args:
            node (obj): node to upload file to
            local_path (str): path to file on local host
            remote_path (str, optional): path to file on remote host. Will be
                generated if omitted.
            check (bool): flag whether check step or not

        Returns:
            str: path to remote file

        Raises:
            AssertionError: if file not exists on remote node after uploading
        """
        if not remote_path:
            remote_path = '/tmp/{}'.format(next(utils.generate_ids('file')))
        task = {
            'copy': {
                'src': local_path,
                'dest': remote_path,
            }
        }
        node.run_task(task)
        if check:
            self.check_file_exists(node, remote_path)

        return remote_path

    @steps_checker.step
    def check_file_contains_line(self, nodes, file_path, line, all=True):
        """Step to check that remote file contains line.

        Args:
            nodes (obj): nodes to check file on them
            file_path (str): path to file on remote hosts
            line (str): line to search in files
            all (bool): presents on all node / any node
        Raises:
            AssertionError: if any of files doesn't contain `line`
        """
        task = {
            'command': 'grep "{line}" "{path}"'.format(
                line=line, path=file_path)
        }
        result = nodes.run_task(task, raise_on_error=all)
        if all:
            assert_that(result,
                        only_contains(has_properties(status=config.STATUS_OK)))
        else:
            assert_that(result,
                        has_item(has_properties(status=config.STATUS_OK)))

    @steps_checker.step
    def make_backup(self, nodes, file_path, suffix=None, check=True):
        """Step to make backup of file with **path** on remote nodes.

        It makes a copy of file to new file with **suffix** in same folder.

        Args:
            nodes (obj): nodes to backup file on them
            file_path (str): path to file on remote hosts
            suffix (str): suffix to append to original file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file not exists after step.

        Returns:
            str: path to backup file

        See also:
            :meth:`restore_backup`
        """
        suffix = suffix or next(utils.generate_ids('backup', length=30))
        backup_path = "{}.{}".format(file_path, suffix)

        task = {
            'command': 'cp --preserve=mode,ownership "{path}" '
                       '"{backup_path}"'.format(path=file_path,
                                                backup_path=backup_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, backup_path)

        return backup_path

    @steps_checker.step
    def restore_backup(self, nodes, file_path, backup_path, check=True):
        """Step to restore file with **path** from backup on remote nodes.

        It restores file from backup with **suffix** placed in same folder.

        Args:
            nodes (obj): nodes to restore file on them
            file_path (str): path to file on remote hosts
            backup_path (str): path to backup
            suffix (str): suffix to make backup file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file exists after step.

        See also:
            :meth:`make_backup`
        """
        task = {
            'command': 'mv "{backup_path}" "{path}"'.format(
                backup_path=backup_path, path=file_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, backup_path, present=False)

    @steps_checker.step
    def check_file_exists(self, nodes, file_path, present=True):
        """Step to check that remote file exists.

        Args:
            nodes (obj): nodes to check file on them
            file_path (str): path to file on remote hosts
            present (bool): should file be present or not

        Raises:
            AssertionError: if any of nodes doesn't contain file
        """
        command = 'ls "{path}"'.format(path=file_path)
        if not present:
            command = '! ' + command
        task = {'shell': command}
        result = nodes.run_task(task, raise_on_error=False)
        assert_that(result, only_contains(has_properties(status='OK')))

    @steps_checker.step
    def patch_ini_file(self, nodes, file_path, option, value,
                       section=None, check=True):
        """Step to patch INI like file.

        Args:
            nodes (obj): nodes hostnames to patch file on it
            file_path (str): path to ini file on remote host
            option (str): name of option to add/override
            value (str): value to add/override
            section (str): name of section to process. 'DEFAULT' will be used
                if `section` is None
            check (bool): flag whether check step or not

        Returns:
            str: path to original file

        Raises:
            AssertionError: if file doesn't contain changes after patching

        See also:
            :meth:`make_backup`
        """
        backup_path = self.make_backup(nodes, file_path)
        task = {
            'ini_file': {
                'backup': False,
                'dest': file_path,
                'section': section or 'DEFAULT',
                'option': option,
                'value': value,
            }
        }
        nodes.run_task(task)
        if check:
            self.check_file_contains_line(
                nodes, file_path, "{} = {}".format(option, value))
        return backup_path

    @steps_checker.step
    def execute_cmd(self, nodes, cmd,
                    timeout=config.ANSIBLE_EXECUTION_MAX_TIMEOUT, check=True):
        """Execute provided bash command on nodes.

        Args:
            nodes (NodeCollection): nodes to execute command on them
            cmd (str): bash command to execute
            timeout (int): seconds to wait command executed
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            list: AnsibleExecutionRecord(s)
        """
        cmd = (u"timeout {timeout} "
               u"bash -c {cmd}").format(timeout=timeout,
                                        cmd=moves.shlex_quote(cmd))

        task = {'shell': cmd.encode('utf-8')}
        result = nodes.run_task(task, raise_on_error=check)

        if check:
            assert_that(
                result, only_contains(has_properties(status=config.STATUS_OK)))

        return result

    @steps_checker.step
    def check_no_nova_server_artifacts(self, server):
        """Step to check that compute doesn't contain server's artifacts.

        Args:
            server (obj): nova server

        Raises:
            AssertionError: if compute contains server's artifacts
        """
        compute = self.get_nodes(
            fqdns=[getattr(server, 'OS-EXT-SRV-ATTR:hypervisor_hostname')])
        cmd = "ls {} | grep {}".format(config.NOVA_INSTANCES_PATH, server.id)
        result = self.execute_cmd(compute, cmd, check=False)
        assert_that(
            result, only_contains(has_properties(status=config.STATUS_FAILED)))

    @steps_checker.step
    def store_file_line_count(self, node, file_name, check=True):
        """Step to store line count in a textual file on nodes.

        Args:
            node (NodeCollection): nodes
            file_name (str): name of textual file
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            str: path to file with stored lines counts
        """
        file_to_store = tempfile.mktemp()
        cmd = "cat {} | wc -l > {}".format(file_name, file_to_store)
        self.execute_cmd(node, cmd, check=check)
        return file_to_store

    @steps_checker.step
    def get_process_pid(self, node, process_name, get_parent=True,
                        check=True):
        """Step to get process pid on a single node.

        It returns pid of a parent or child process with specified name.
        It's supposed that several processes can be found - one main process
        (ppid=1) and one or more child processes.

        Args:
            node (NodeCollection): node
            process_name (str): partial name of process
            get_parent (bool): flag which pid should be returned -
                parent's or child's one. For parent_process=False and
                several children, minimal pid is returned.
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True or list of pids is empty

        Returns:
            int: process pid
        """
        cmd = "ps -ef | grep {} | grep -v grep".format(process_name)
        cmd += " | awk '{print $2, $3}'"
        result = self.execute_cmd(node, cmd, check=check)
        stdout = result[0].payload['stdout']
        # ex: 3468 1
        #     3672 3468
        #     3673 3468
        # or: 1234 1
        pids = map(int, stdout.split())
        assert_that(pids, is_not(empty()))
        pids.remove(1)
        main_pids = [pid for pid in pids if pids.count(pid) > 1]
        if len(main_pids) == 0:
            # no children
            main_pids = pids
            children_pids = []
        else:
            children_pids = [pid for pid in pids if pids.count(pid) == 1]
        if get_parent:
            return main_pids[0]
        else:
            assert_that(children_pids, is_not(empty()))
            return min(children_pids)

    @steps_checker.step
    def check_process_pid(self, node, process_name, expected_pid,
                          check_parent=True):
        """Step to check the process pid on a single node.

        Args:
            node (NodeCollection): node
            process_name (str): partial name of process
            expected_pid (int): expected pid
            check_parent (bool): flag which pid should be checked -
                parent's or child's one.

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed or pid is not equal to expected one
        """
        pid = self.get_process_pid(node, process_name, get_parent=check_parent)
        assert_that(pid, is_(expected_pid))

    @steps_checker.step
    def send_signal_to_process(self, node, pid, signal, delay=None,
                               check=True):
        """Step to send a signal to a process on a single node.

        Args:
            node (NodeCollection): node
            pid (int): process pid
            signal (int): signal id
            delay (int): delay after signal sending, in seconds
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True
        """
        cmd = "kill -{0} {1}".format(signal, pid)
        self.execute_cmd(node, cmd, check=check)
        if delay:
            time.sleep(delay)

    @steps_checker.step
    def send_signal_to_processes_by_name(self, nodes, name, signal, delay=None,
                                         check=True):
        """Step to send a signal to processes using name.

        Args:
            nodes (NodeCollection): nodes
            name (str): partial name of processes
            signal (int): signal id
            delay (int): delay after signal sending, in seconds
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True
        """
        cmd = "killall -{0} {1}".format(signal, name)
        self.execute_cmd(nodes, cmd, check=check)
        if delay:
            time.sleep(delay)

    @steps_checker.step
    def check_string_in_file(self,
                             node,
                             file_name,
                             keyword,
                             non_matching=None,
                             start_line_number_file=None,
                             must_present=True,
                             expected_count=None):
        """Step to check number of keywords in a textual file on a single node.

        Args:
            node (NodeCollection): nodes
            file_name (str): name of textual file
            keyword (str): string to search
            non_matching (str|None): string to be absent in result
            start_line_number_file (str|None): file path with number of first
                line for searching
            must_present (bool): flag that keyword must be present or not
            expected_count (int|None): expected count of lines containing
                keyword

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True or real count of lines with
                keyword is not equal to expected one
        """
        if start_line_number_file:
            start_line_number_cmd = 'cat ' + start_line_number_file
        else:
            start_line_number_cmd = 'echo 0'
        cmd = "tail -n +$({0}) {1} | grep {2}".format(
            start_line_number_cmd, file_name,
            moves.shlex_quote(keyword))
        if non_matching:
            cmd += " | grep -v {0}".format(moves.shlex_quote(non_matching))

        if expected_count is None:
            if must_present:
                matcher = greater_than(0)
            else:
                matcher = 0
        else:
            matcher = expected_count
        result = self.execute_cmd(node, cmd, check=False)
        for node_result in result:
            lines = node_result.payload['stdout_lines']
            assert_that(lines, has_length(matcher))

    @steps_checker.step
    def get_ovs_flows_cookies(self, node, check=True):
        """Step to retrieve ovs flows cookies from node.

        Args:
            node (obj): NodeCollection to retrieve flows from
            check (bool, optional): flag whether check step or not

        Returns:
            set: flows cookies

        Raises:
            AssertionError: if flows cookies has more than one value
        """
        cmd = "ovs-ofctl dump-flows br-int"
        result = self.execute_cmd(node, cmd)
        stdout = result[0].payload['stdout']
        cookies = re.findall(r'cookie=(?P<value>[^,]+)', stdout)
        uniq_cookies = set(cookies)
        if check:
            assert_that(uniq_cookies, has_length(1))
        return uniq_cookies

    @steps_checker.step
    def check_ovs_flow_cookies(self, node, not_contain):
        """Verify step to check ovs flows cookies.

        This step check that ovs actual flows cookies doesn't contain any value
        from ``not_contain`` set.

        Args:
            node (obj): NodeCollection instance to get ovs flow cookies from
            not_contain (set|list|tuple): values which actual cookies should
                not contain

        Raises:
            AssertionError: if cookie values contains any of ``not_contain``
                value
        """
        actual_cookies = self.get_ovs_flows_cookies(node, check=False)
        assert_that(actual_cookies, is_not(contains_inanyorder(not_contain)))

    @steps_checker.step
    def get_ovs_vsctl_tags(self, check=True):
        """Step to get ovs-vsctl tags.

        Args:
            check (bool): flag whether check step or not

        Returns:
            dict: ovs-vsctl tags for all nodes

        Raises:
            AssertionError: if ovs-vsctl tags dict is empty
        """
        def get_ports_tags_data(lines):
            """Return ovs-vsctl tags in dict format."""
            port_tags = {}
            last_offset = 0
            port = None
            for line in lines[1:]:
                line = line.rstrip()
                key, val = line.split(None, 1)
                offset = len(line) - len(line.lstrip())
                if port is None:
                    if key.lower() == 'port':
                        port = val.strip('"')
                        last_offset = offset
                elif offset <= last_offset:
                    port = None
                elif key.lower() == 'tag:':
                    port_tags[port] = val
                    port = None
            return port_tags

        nodes = self.get_nodes(service_names=[config.NEUTRON_OVS_SERVICE])
        result_records = self.execute_cmd(nodes, 'ovs-vsctl show')
        ovs_vsctl_tags = {
            record.host: get_ports_tags_data(record.payload['stdout_lines'])
            for record in result_records}

        if check:
            assert_that(ovs_vsctl_tags, is_not(empty()))

        return ovs_vsctl_tags

    @steps_checker.step
    def check_ovs_vsctl_tags(self, expected_tags):
        """Step to check ovs-vsctl tags.

        Args:
            expected_tags (dict): ovs-vsctl tags for all nodes

        Raises:
            AssertionError: if ovs-vsctl tags not equal to expected ones.
        """
        actual_tags = self.get_ovs_vsctl_tags()
        assert_that(actual_tags, equal_to(expected_tags))

    @steps_checker.step
    def check_io_limits_in_virsh_dumpxml(self, node, instance_name, limit):
        """Step to check I/O limit in results of 'virsh dumpxml'.

        Args:
            node (NodeCollection): node
            instance_name (str): instance name
            limit (int): I/O limit value

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed or result of 'virsh dumpxml' doesn't contain expected
                data
        """
        cmd = "virsh dumpxml {}".format(instance_name)
        stdout = self.execute_cmd(node, cmd)[0].payload['stdout']
        expected_strings = [
            "<read_bytes_sec>{}</read_bytes_sec>".format(limit),
            "<write_bytes_sec>{}</write_bytes_sec>".format(limit)]
        for expected_string in expected_strings:
            assert_that(expected_string, is_in(stdout))

    @steps_checker.step
    def check_io_limits_in_ps(self, node, limit):
        """Step to check I/O limit in results of 'ps'.

        Args:
            node (NodeCollection): node
            limit (int): I/O limit value

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed or result of 'ps' doesn't contain expected data
        """
        cmd = "ps aux | grep qemu | grep 'drive file=rbd'"
        stdout = self.execute_cmd(node, cmd)[0].payload['stdout']
        matchers = [contains_string(tpl.format(limit))
                    for tpl in ("bps_rd={}", "bps_wr={}")]
        assert_that(stdout, all_of(*matchers))

    @steps_checker.step
    def get_network_type(self):
        """Step to retrieve network type from neutron config.

        Network type can be VLAN or VxLAN

        Returns:
            str: network type (vlan or vxlan)
        """
        cmd = "grep -P '^tenant_network_types\s*=\s*.+vxlan' {}".format(
            config.NEUTRON_ML2_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.NEUTRON_OVS_SERVICE])
        result = self.execute_cmd(nodes, cmd, check=False)
        if any(node_result.status == config.STATUS_OK
               for node_result in result):
            return config.NETWORK_TYPE_VXLAN
        else:
            return config.NETWORK_TYPE_VLAN

    @steps_checker.step
    def get_nodes_for_agents(self, agents, check=True):
        """Step to retrieve nodes for L3 or DHCP agents.

        Args:
            agents (list): list of dicts of L3 or DHCP agents
            check (bool): flag whether check step or not

        Returns:
            NodeCollection: nodes for L3 or DHCP agents
        """
        fqdns = [self.get_fqdn_by_host_name(agent['host']) for agent in agents]
        nodes = self.get_nodes(fqdns=fqdns, check=check)

        return nodes

    @steps_checker.step
    def get_neutron_l3_ha(self):
        """Step to retrieve neutron L3 HA feature enabled or not.

        Returns:
            bool: is neutron L3 HA feature enabled
        """
        cmd = "grep -iP '^l3_ha\s*=\s*true' {}".format(
            config.NEUTRON_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.NEUTRON_L3_SERVICE])
        result = self.execute_cmd(nodes, cmd, check=False)
        return any(node_result.status == config.STATUS_OK
                   for node_result in result)

    @steps_checker.step
    def get_neutron_dvr(self):
        """Step to retrieve neutron DVR feature enabled or not.

        Returns:
            bool: is neutron DVR feature enabled
        """
        cmd = "grep -iP '^agent_mode\s*=\s*dvr' {}".format(
            config.NEUTRON_L3_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.NEUTRON_L3_SERVICE])
        result = self.execute_cmd(nodes, cmd, check=False)
        return all(node_result.status == config.STATUS_OK
                   for node_result in result)

    @steps_checker.step
    def get_neutron_l2pop(self):
        """Step to retrieve neutron L2 population driver enabled or not.

        Returns:
            bool: is neutron L2 population driver enabled
        """
        cmd = "grep -iP '^mechanism_drivers\s*=\s*.+l2population' {}".format(
            config.NEUTRON_ML2_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.NEUTRON_L3_SERVICE])
        result = self.execute_cmd(nodes, cmd, check=False)
        return all(node_result.status == config.STATUS_OK
                   for node_result in result)

    @steps_checker.step
    def get_horizon_cinder_backups(self):
        """Step to retrieve horizon cinder backup enabled or not.

        Returns:
            bool: is horizon cinder backup enabled
        """
        pattern = moves.shlex_quote('^\s+["\']enable_backup["\']\s*:\s*True')
        cmd = "grep -P {} {}".format(pattern, config.HORIZON_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.HORIZON])
        result = self.execute_cmd(nodes, cmd, check=False)
        return all(node_result.status == config.STATUS_OK
                   for node_result in result)

    @steps_checker.step
    def get_neutron_debug(self):
        """Step to get debug mode in neutron config files.

        Returns:
            bool: debug mode
        """
        cmd = "grep -iP '^debug\s*=\s*True' {}".format(
            config.NEUTRON_CONFIG_PATH)
        nodes = self.get_nodes(service_names=[config.NEUTRON_L3_SERVICE])
        result = self.execute_cmd(nodes, cmd, check=False)
        return all(node_result.status == config.STATUS_OK
                   for node_result in result)

    @steps_checker.step
    def get_default_glance_backend(self):
        """Step to retrieve default glance backend name.

        Returns:
            str: default glance backend name
        """
        cmd = "awk -F'=' '/^default_store/{{ print $2 }}' {}".format(
            config.GLANCE_API_CONFIG_PATH)
        nodes = self.get_node(service_names=[config.GLANCE_API])
        result = self.execute_cmd(nodes, cmd, check=False)
        return result[0].payload['stdout'].strip()

    @steps_checker.step
    def get_ceilometer(self):
        """Step to retrieve whether ceilometer is enabled or not.

        Returns:
            bool: is ceilometer enabled or not
        """
        node = self.get_node(service_names=[config.NOVA_API])
        try:
            self.check_file_exists(node, config.CEILOMETER_CONFIG_PATH)
            is_present = True
        except AssertionError:
            is_present = False

        return is_present

    @steps_checker.step
    def check_router_namespace_presence(self, router, node, must_present=True,
                                        timeout=0):
        """Step to check router namespace presence on compute node.

        Args:
            router (object): neutron router
            node (NodeCollection): node
            must_present (bool): flag to check is namespace present or absent
            timeout (int, optional): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        router_namespace = "qrouter-{0}".format(router['id'])
        cmd = 'ip net | grep {}'.format(router_namespace)
        status = config.STATUS_OK if must_present else config.STATUS_FAILED

        def _check_router_namespace_presence():
            result = self.execute_cmd(node, cmd, check=False)
            return waiter.expect_that(
                result, only_contains(has_properties(status=status)))

        waiter.wait(_check_router_namespace_presence, timeout_seconds=timeout)

    @steps_checker.step
    def delete_router_namespace(self, nodes, router, check=True):
        """Step to delete router namespace on nodes.

        Args:
            nodes (obj): NodeCollection to delete router namespace on
            router (dict): neutron router
            check (bool, optional): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed or router namespace was not deleted
        """
        cmd = "ip net delete qrouter-{}".format(router['id'])
        self.execute_cmd(nodes, cmd, check=check)
        if check:
            self.check_router_namespace_presence(router, nodes,
                                                 must_present=False)

    @steps_checker.step
    def get_nodes_by_cmd(self, cmd):
        """Step to retrieve nodes with `0` exit code for `cmd` executing.

        Args:
            cmd (str): command to check should node be filtered or not. If
                command exit code on node is not `0` - node will be skipped.

        Returns:
            obj: NodeCollection with filtered nodes

        Raises:
            AssertionError: if no nodes filtered
        """
        nodes = self.get_nodes()
        result = self.execute_cmd(nodes, cmd, check=False)
        filtered_hosts_ips = set(record.host for record in result
                                 if record.status == config.STATUS_OK)
        fqdns = []
        for node in nodes:
            if node.ip in filtered_hosts_ips:
                fqdns.append(node.fqdn)
        if not fqdns:
            return NodeCollection(hosts=[])
        return self.get_nodes(fqdns=fqdns)

    @steps_checker.step
    def get_node_by_cmd(self, cmd):
        """Step to retrieve one node with `0` exit code for `cmd` executing.

        Args:
            cmd (str): command to check should node be filtered or not. If
                command exit code on node is not `0` - node will be skipped.

        Returns:
            obj: NodeCollection with one filtered random node

        Raises:
            AssertionError: if there are no nodes after filtering
        """
        return self.get_nodes_by_cmd(cmd).pick()

    @steps_checker.step
    def check_all_nodes_availability(self, timeout=0):
        """Step to check availability of all nodes.

        Args:
            timeout (int, optional): seconds to wait result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _verify_connect():
            try:
                self._client.verify()
                return True
            except AnsibleExecutionException:
                return False

        waiter.wait(_verify_connect, timeout_seconds=timeout)

    @steps_checker.step
    def check_nodes_tcp_availability(self, nodes, must_available=True,
                                     timeout=0):
        """Step to check that all nodes available (or not) on 22 TCP port.


        Args:
            nodes (obj): NodeCollection to check availability
            must_available (bool, optional): flag whether nodes should be
                available or not
            timeout (int, optional): seconds to wait a result of check

        Raises:
            TimeoutExpired: if all nodes availability not equal
                ``must_available`` argument after timeout.
        """
        ips = nodes.get_ips()
        expected_availability = dict.fromkeys(ips, must_available)

        def _check_nodes_ssh_availability():
            actual_availability = dict.fromkeys(ips)
            for ip in ips:
                actual_availability[ip] = network_checks.check_tcp_connect(ip)
            return waiter.expect_that(actual_availability,
                                      equal_to(expected_availability))

        waiter.wait(_check_nodes_ssh_availability, timeout_seconds=timeout)

    @steps_checker.step
    def shutdown_nodes(self, nodes, check=True):
        """Step to shutdown nodes gracefully.

        Args:
            nodes (obj): NodeCollection to shutdown
            check (bool, optional): flag whether to check this step or not

        Raises:
            TimeoutExpired: if nodes are available on 22 TCP port after
                shutdown
        """
        # TODO(ssokolov) poweroff -> shutdown when implemented in os-faults
        nodes.poweroff()
        # nodes.shutdown()
        if check:
            self.check_nodes_tcp_availability(
                nodes, must_available=False,
                timeout=config.NODE_SHUTDOWN_TIMEOUT)

    @steps_checker.step
    def poweroff_nodes(self, nodes, check=True):
        """Step to power off nodes.

        Args:
            nodes (obj): NodeCollection to power off
            check (bool, optional): flag whether to check this step or not

        Raises:
            TimeoutExpired: if nodes are available on 22 TCP port after power
                off
        """
        nodes.poweroff()
        if check:
            self.check_nodes_tcp_availability(
                nodes, must_available=False,
                timeout=config.NODE_POWEROFF_TIMEOUT)

    @steps_checker.step
    def poweron_nodes(self, nodes, check=True):
        """Step to power on nodes.

        Args:
            nodes (obj): NodeCollection to power on
            check (bool, optional): flag whether to check this step or not

        Raises:
            TimeoutExpired: if nodes are not available on 22 TCP port after
                power on
        """
        nodes.poweron()
        if check:
            self.check_nodes_tcp_availability(
                nodes, timeout=config.NODE_REBOOT_TIMEOUT)

    @steps_checker.step
    def reset_nodes(self, nodes, native=True, wait_reboot=True, check=True):
        """Step to reset nodes.

        Args:
            nodes (obj): NodeCollection to reset
            native (bool, optional): flag whether to use reset or
                poweroff/poweron. By default reset is used
            wait_reboot (bool, optional): flag whether to wait for nodes
                availability
            check (bool, optional): flag whether to check this step or not
        """
        if native:
            nodes.reset()
            if check:
                self.check_nodes_tcp_availability(
                    nodes, must_available=False,
                    timeout=config.NODE_SHUTDOWN_TIMEOUT)
            if wait_reboot:
                self.check_nodes_tcp_availability(
                    nodes, timeout=config.NODE_REBOOT_TIMEOUT)
        else:
            # workaround for libvirt issue that node is not powered
            # on sometimes after native reset
            self.poweroff_nodes(nodes, check=check)
            self.poweron_nodes(nodes, check=wait_reboot)

    @steps_checker.step
    def add_rule_to_drop_port(self, nodes, port, check=True):
        """Step to add rule to drop port on nodes.

        Args:
            nodes (obj): NodeCollection to drop port
            port (int): port number to drop
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed
        """
        cmd = "iptables -I OUTPUT 1 -p tcp --dport {0} -j DROP".format(port)
        self.execute_cmd(nodes, cmd, check=check)

    @steps_checker.step
    def remove_rule_to_drop_port(self, nodes, port, check=True):
        """Step to remove rule to drop port on nodes.

        Args:
            nodes (obj): NodeCollection to remove rule
            port (int): port number for removing the rule
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed
        """
        cmd = "iptables -D OUTPUT -p tcp --dport {0} -j DROP".format(port)
        self.execute_cmd(nodes, cmd, check=check)

    @steps_checker.step
    def start_tcpdump(self, nodes, args='', prefix=None, check=True):
        """Step to start tcpdump on nodes in backgroud.

        Args:
            nodes (NodeCollection): nodes to start tcpdump on
            args (str, optional): additional ``tcpdump`` args
            prefix (str, optional): prefix for command. It can be useful for
                executing tcpdump on ip namespace.
            check (bool, optional): flag whether to check this step or not

        Returns:
            str: base path for cap, pid, stdout, stderr files for tcpdump

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed
        """
        base_path = tempfile.mktemp()
        cmd = ("( ( nohup {prefix} tcpdump -w{base_path}.cap {args} "
               "<&- >{base_path}.stdout 2>{base_path}.stderr ) & "
               "echo $! > {base_path}.pid )").format(
                   args=args, base_path=base_path, prefix=prefix or '')
        self.execute_cmd(nodes, cmd, check=check)
        if check:
            # Check that commands is running
            cmd = "ps -eo pid | grep $(cat {}.pid)".format(base_path)
            self.execute_cmd(nodes, cmd)
            # Check that pcap file is appear
            cmd = 'while [ ! -f {}.cap ]; do sleep 1; done'.format(base_path)
            self.execute_cmd(nodes, cmd)
            # tcpdump need some more time to start packets capturing
            time.sleep(config.TCPDUMP_LATENCY)

        return base_path

    @steps_checker.step
    def stop_tcpdump(self, nodes, base_path, check=True):
        """Step stop background tcpdump.

        Args:
            nodes (NodeCollection): nodes to stop tcpdump on
            base_path (str): base path for cap, pid, stdout, stderr files for
                tcpdump
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed
        """
        # Wait some time to allow tcpdump to process all packets
        time.sleep(config.TCPDUMP_LATENCY)

        # Send SIGINT
        cmd = 'kill -s INT $(cat {}.pid) || true'.format(base_path)
        self.execute_cmd(nodes, cmd, check=check)

        # Wait until process to be stopped
        cmd = ('while kill -0 $(cat {}.pid) 2> /dev/null; '
               'do sleep 1; done;').format(base_path)

    @steps_checker.step
    def download_tcpdump_results(self, nodes, base_path, check=True):
        """Step to copy tcpdump cap files to local server.

        Args:
            nodes (NodeCollection): nodes to start tcpdump
            base_path (str): base path for cap, pid, stdout, stderr files for
                tcpdump
            check (bool, optional): flag whether to check this step or not

        Returns:
            dict: node fqdn -> local cap file path

        Raises:
            ValueError: if any of local cap files are not a regular file
            AssertionError|AnsibleExecutionException: if command execution
                failed
        """
        dest_dir = tempfile.mkdtemp()
        task = {
            'fetch': {
                'src': base_path + '.cap',
                'dest': dest_dir,
            }
        }
        nodes.run_task(task)

        # Clear tcpdump results on nodes
        cmd = "rm -f {}*".format(base_path)
        self.execute_cmd(nodes, cmd)

        cap_files = {}
        for node in nodes:
            path = os.path.join(dest_dir, node.ip)
            cap_files[node.fqdn] = path + base_path + '.cap'

        if check:
            for path in cap_files.values():
                if not os.path.isfile(path):
                    raise ValueError('{!r} is not a regular file'.format(path))
                file_stat = os.stat(path)
                assert_that(file_stat.st_size, is_not(0))

        return cap_files

    @steps_checker.step
    def check_last_pings_replies_timestamp(self, file1, matcher, file2):
        """Compare last ICMP echo response timestamp from 2 files.

        Args:
            file1 (str): path to 1'st file
            matcher (obj): hamcrest matcher
            file2 (str): path to 2'nd file

        Raises:
            AssertionError: if check failed
        """
        ts_1 = tcpdump.get_last_ping_reply_ts(file1)
        ts_2 = tcpdump.get_last_ping_reply_ts(file2)
        assert_that(ts_1, matcher(ts_2))

    @steps_checker.step
    def move_ha_router_interface_to_down_state(self, node, router, check=True):
        """Step to move router's HA interface to down state.

        Args:
            node (NodeCollection): node to perform operation on
            router (dict): neutron router
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        ns_cmd = "ip net e qrouter-{}".format(router['id'])
        cmd = ("{ns_cmd} ip link set dev "
               "$({ns_cmd} ip -o l | grep -oE 'ha-[^:]+') "
               "down").format(ns_cmd=ns_cmd)
        self.execute_cmd(node, cmd, check=check)

    @steps_checker.step
    def ping_ip_with_router_namescape(self, node, ip, router, count=3,
                                      check=True):
        """Step to ping ip from node with router namespace.

        Args:
            node (NodeCollection): node to start ping on
            ip (str): ip address to ping
            router (dict): neutron router
            count (int, optional): count of ping requests
            check (bool, optional): flag whether to check this step or not
        """
        ns_cmd = "ip net e qrouter-{}".format(router['id'])
        cmd = "{ns_cmd} ping -c{count} {ip}".format(
            ns_cmd=ns_cmd, ip=ip, count=count)
        self.execute_cmd(node, cmd, check=check)

    @steps_checker.step
    def check_vxlan_enabled(self, node):
        """Step check that vxlan enabled on ovs on node.

        Args:
            node (NodeCollection): node to check vxlan on

        Raises:
            AssertionError: if check failed
        """
        cmd = "ovs-vsctl show | grep 'type: vxlan'"
        result = self.execute_cmd(node, cmd)
        assert_that(
            result, only_contains(has_properties(status=config.STATUS_OK)))

    @steps_checker.step
    def check_vni_segmentation(self, pcap_path, network, add_filters=None):
        """Check that vni for vxlan packets equal to network segmentation_id.

        Args:
            pcap_path (path): path to pcap file
            network (dict): neutron network
            add_filters (list, optional): additional filters to packets. By
                default all vxlan packets will be filteres.

        Raises:
            AssertionError: if check failed
        """
        filters = add_filters or []
        filters.append(tcpdump.filter_vxlan)
        lfilter = lambda x: all(filter_(x) for filter_ in filters)
        vnis = set()
        for packet in tcpdump.read_pcap(
                pcap_path, lfilter=lfilter):
            vnis.add(packet.getlayer('VXLAN').vni)

        assert_that(vnis, only_contains(network['provider:segmentation_id']))

    @steps_checker.step
    def check_arp_traffic_from_ip(self, pcap_path, psrc, must_present=True):
        """Check that pcap file contains (or not) ARP packets from psrc.

        Args:
            pcap_path (path): path to pcap file
            psrc (str): source ip address
            must_present (bool, optional): flag whether packets should to be in
                pcap file or not

        Raises:
            AssertionError: if check failed
        """
        def lfilter(packet):
            return (packet.haslayer('ARP') and
                    packet.getlayer('ARP').psrc == psrc)

        packets = list(tcpdump.read_pcap(pcap_path, lfilter))
        matcher = is_not(empty()) if must_present else is_(empty())
        assert_that(packets, matcher)

    @steps_checker.step
    def check_vxlan_icmp_traffic(self, pcap_path, src):
        """Check that pcap file contains VXLAN packets with ICMP from src.

        Args:
            pcap_path (path): path to pcap file
            src (str): source ip address

        Raises:
            AssertionError: if check failed
        """
        def lfilter(packet):
            vxlan = packet.getlayer('VXLAN')
            if vxlan is None:
                return False
            return vxlan.haslayer('ICMP') and vxlan.getlayer('IP').src == src

        packets = list(tcpdump.read_pcap(pcap_path, lfilter))
        assert_that(packets, is_not(empty()))

    @steps_checker.step
    def get_nodes_ips(self, nodes=None, ipv6=False, check=True):
        """Step to retrieve nodes IP addresses.

        Args:
            nodes (NodeCollection, optional): nodes to retrieve IP addresses
                for. By default IP addresses will be retrieved from all nodes.
            ipv6 (bool, optional): flag whether to filter ipv6 ip addresses.
                By default only ipv4 addreses will be filtered.
            check (bool, optional): flag whether to check this step or not

        Returns:
            dict: node's fqdn -> list of node ip addresses

        Raises:
            AssertionError: if check failed
        """
        nodes = nodes or self.get_nodes()
        cmd = "ip -o a | grep -v ' lo '"
        if ipv6:
            cmd += "| awk '/inet6 /{split($4,ip,\"/\"); print ip[1]}'"
        else:
            cmd += "| awk '/inet /{split($4,ip,\"/\"); print ip[1]}'"
        result = self.execute_cmd(nodes, cmd, check=check)

        ips = {}
        for node_result in result:
            for node in nodes:
                if node.ip == node_result.host:
                    ips[node.fqdn] = node_result.payload['stdout_lines']
                    break
        if check:
            assert_that(ips.values(), only_contains(is_not(empty())))
        return ips

    @steps_checker.step
    def check_ovs_tunnels(self, from_nodes, to_nodes, must_established=True):
        """Step to check that OVS tunnels established (or not) to nodes.

        Args:
            from_nodes (NodeCollection): nodes to check OVS tunnels on
            to_nodes (NodeCollection): nodes to check are OVS tunnels
                established to
            must_established (bool, optional): flag whether tunnels should be
                established or should be not established

        Raises:
            AssertionError: if check failed
        """
        cmd = "ovs-vsctl show"
        result = self.execute_cmd(from_nodes, cmd)
        for node_result in result:
            stdout = node_result.payload['stdout']
            tunnels_remotes = re.findall(
                r'remote_ip="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"', stdout)
            to_nodes_ips = self.get_nodes_ips(nodes=to_nodes)
            for node in to_nodes:
                matchers = [has_item(ip) for ip in to_nodes_ips[node.fqdn]]
                if must_established:
                    assert_that(tunnels_remotes, any_of(*matchers))
                else:
                    assert_that(tunnels_remotes, is_not(any_of(*matchers)))

    @steps_checker.step
    def get_services_for_component(self, component, nodes):
        """Step to get list of component services.

        Args:
            component (str): component name to filter out
            nodes (NodeCollection): nodes to get services

        Returns:
            dict: node's fqdn -> list of services
        """
        warnings.warn("This method will be deleted in future. You should use "
                      "`get_services_names` instead", DeprecationWarning)
        cmd = "initctl list | grep running | grep {0}".format(component)
        cmd += " | awk '{ print $1 }'"
        services = {}
        results = self.execute_cmd(nodes=nodes, cmd=cmd)
        for node_result in results:
            for node in nodes:
                if node_result.host == node.ip:
                    services[node.fqdn] = node_result.payload['stdout_lines']
        return services

    @steps_checker.step
    def check_zones_assigment_to_devices(self, node):
        """Step to check conntack zones.

        This step gets `conntrack` and `iptables` outputs and check that each
        zone has 2 devices - tap and qvb.

        Args:
            node (NodeCollection): node to execute check

        Raises:
            AssertionError: if check failed
        """
        conntrack_output = self.execute_cmd(
            node, 'conntrack -L -p icmp')[0].payload['stdout']
        iptables_output = self.execute_cmd(
            node, 'iptables -L -t raw')[0].payload['stdout_lines']

        zones = re.findall(r'zone=(?P<zone>\d+)', conntrack_output)
        zones = set(zones)

        for start, line in enumerate(iptables_output):
            if 'Chain neutron-openvswi-PREROUTING' in line:
                break
        start += 2
        zones_devices = collections.defaultdict(list)

        for line in iptables_output[start:]:
            data = re.split('\s+', line, maxsplit=6)
            if data[:-1] != [
                    'CT', 'all', '--', 'anywhere', 'anywhere', 'PHYSDEV'
            ]:
                continue
            dev_data = re.search(
                r'match --physdev-in (?P<dev>.+?) CTzone (?P<zone>\d+)',
                data[-1]).groupdict()
            if dev_data['zone'] not in zones:
                continue
            zones_devices[dev_data['zone']].append(dev_data['dev'])

        for devices in zones_devices.values():
            assert_that(devices, has_length(2))
            dev_types = {x[:3] for x in devices}
            assert_that(dev_types, equal_to({'tap', 'qvb'}))

    @steps_checker.step
    def check_glance_fs_usage(self, nodes, quota):
        """Step check that glance summary FS usage is not more than quota.

        Args:
            nodes (NodeCollection): nodes to get glance FS usage
            quota (int): maximum allowed glance FS usage

        Raises:
            AssertionError: if glance disk usage is greater than quota
        """
        cmd = "du -s {} | awk '{{print $1}}'".format(config.GLANCE_IMAGES_PATH)
        results = self.execute_cmd(nodes, cmd)
        for node_result in results:
            assert_that(int(node_result.payload['stdout']),
                        less_than_or_equal_to(quota))

    @steps_checker.step
    def delete_ports_bindings_for_dhcp_agents(self, node, check=True):
        """Step to delete ports bindings for all DHCP agents.

        Args:
            node (NodeCollection): controller to execute command for deleting
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True
        """
        cmd = ('mysql --database="neutron" -e '
               '"delete from networkdhcpagentbindings;"')

        self.execute_cmd(node, cmd, check=check)

    @steps_checker.step
    def check_tap_interfaces_are_unique(self, nodes, network, timeout=0):
        """Step to check that tap interfaces ids for net are unique on nodes.

        Args:
            nodes (NodeCollection): nodes to check tap interfaces ids
            network (dict): network dict
            timeout (int, optional): seconds to wait for a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _parse_tap_id(output):
            tap_id = re.findall(r'(?:\d+): (tap[^:]+)', output)
            assert_that(tap_id, has_length(1))
            return tap_id[0]

        def _check_tap_interfaces_are_unique():
            cmd = "ip netns exec qdhcp-{} ip a | grep tap".format(
                network['id'])
            results = self.execute_cmd(nodes, cmd, check=False)
            nodes_stdout = [result.payload['stdout'] for result in results
                            if result.status == config.STATUS_OK]
            # tap interfaces for net should exist on more than 1 controller
            # according to developers
            waiter.expect_that(nodes_stdout, has_length(greater_than(1)))

            tap_ids = [_parse_tap_id(stdout) for stdout in nodes_stdout]

            return waiter.expect_that(sorted(tap_ids), sorted(set(tap_ids)))

        waiter.wait(_check_tap_interfaces_are_unique, timeout_seconds=timeout)

    @steps_checker.step
    def get_glance_password(self):
        """Step to retrieve glance password.

        Returns:
            str: glance password
        """
        cmd = ("awk '/^password=/{split($1,val,\"=\"); print val[2]}' " +
               config.GLANCE_API_CONFIG_PATH)
        glance_nodes = self._client.get_service(config.GLANCE_API).get_nodes()
        return self.execute_cmd(glance_nodes.pick(), cmd)[0].payload['stdout']

    @steps_checker.step
    def nova_compute_force_down(self, nova_api_node, failed_node, check=True):
        """Step to set nova-compute service to Forced down status.

           It's executed on compute node where nova-compute service is stopped.
           It's required for nova evacuate tests.

        Args:
            nova_api_node (NodeCollection): node with nova-api service
            failed_node (str): fqdn of node with stopped nova-compute service
            check (bool, optional): flag whether to check this step or not
        """
        cmd = '{0} && nova service-force-down {1} {2}'.format(
            config.OPENRC_ACTIVATE_CMD,
            failed_node,
            config.NOVA_COMPUTE)

        self.execute_cmd(nova_api_node, cmd, check=check)

    @steps_checker.step
    def get_fqdn_by_host_name(self, host_name, check=True):
        """Step to get FQDN by host name.

        Ex: cmp01 -> cmp01.mk22-lab-dvr.local
        This step usage is valid also if 'host_name' is equal to 'fqdn'.

        Args:
            host_name (str): host name
            check (bool, optional): flag whether to check step or not

        Raises:
            AssertionError: if number of nodes with proper FQDN != 1

        Returns:
            str: FQDN
        """
        nodes = self._client.get_nodes()
        fqdns = [node.fqdn for node in nodes
                 if node.fqdn.startswith(host_name)]
        if check:
            assert_that(fqdns, has_length(1))
        return fqdns[0]

    @steps_checker.step
    def get_mysql_credentials(self, mysql_nodes):
        """Step to get mysql username and password from config file.

        Args:
            mysql_nodes (NodeCollection): nodes with mysql

        Returns:
            tuple: (username, password)

        Raises:
            ValueError|IndexError: if unexpected format of config files
        """
        cmd = "grep wsrep_sst_auth {}".format(config.MYSQL_CONFIG_FILE)
        results = self.execute_cmd(mysql_nodes, cmd)
        stdout = results[0].payload['stdout']
        # wsrep_sst_auth=root:sJI8rf5YGypAnuf4
        username, password = stdout.split('=')[1].split(':')
        return username, password

    @steps_checker.step
    def check_galera_cluster_state(self, member_nodes, nodes_to_check=None):
        """Step to check galera cluster parameters.

        This step checks that cluster is in 'Operational' state with 'Primary'
        status. 'Synced' state of nodes is checked too as well as cluster size
        and its members.

        wsrep_local_state_comment: Synced
        wsrep_incoming_addresses: 172.16.10.102:3306, 172.16.10.101:3306
        wsrep_evs_state: OPERATIONAL
        wsrep_cluster_size: 2
        wsrep_cluster_status: Primary

        Args:
            member_nodes (NodeCollection): expected nodes in cluster
            nodes_to_check (NodeCollection): nodes to check cluster from

        Raises:
            AssertionError: if values of cluster parameters are unexpected
            TimeoutException: if no response from cluster after timeout
        """
        cluster_params = {}
        username, password = self.get_mysql_credentials(member_nodes)
        cmd = "mysql -u {0} -p{1} -e \"{2}\"".format(
            username, password, config.GALERA_CLUSTER_STATUS_CHECK_CMD)
        nodes_to_check = nodes_to_check or member_nodes

        def _wait_successful_command_response():
            results = self.execute_cmd(nodes_to_check, cmd, check=False)
            return all(
                waiter.expect_that(result.status, equal_to(config.STATUS_OK))
                for result in results)

        waiter.wait(_wait_successful_command_response,
                    timeout_seconds=config.GALERA_CLUSTER_UP_TIMEOUT)

        results = self.execute_cmd(nodes_to_check, cmd)
        for result in results:
            cluster_params[result.host] = {}
            for parameter in result.payload['stdout_lines'][1:]:
                parameter_name, value = parameter.split('\t')
                cluster_params[result.host].update({parameter_name: value})

        expected_incoming_addr = [
            '{}:{}'.format(ip, config.MYSQL_PORT)
            for ip in self.get_nodes_ip_for_interface(member_nodes, 'eth1')]

        for host, param in cluster_params.items():
            actual_incoming_addr = sorted(
                param[config.GALERA_CLUSTER_MEMBERS_PARAM].split(','))
            assert_that(
                param, has_entries(config.GALERA_CLUSTER_STATUS_PARAMS))
            assert_that(param[config.GALERA_CLUSTER_SIZE_PARAM],
                        equal_to(str(len(member_nodes))))
            assert_that(actual_incoming_addr, equal_to(expected_incoming_addr))

    @steps_checker.step
    def check_galera_data_replication(self, nodes):
        """Step to check galera data replication.

        This step checks that a new table created in database on one node is
        visible on other nodes.

        Args:
            nodes (NodeCollection): nodes of Galera cluster

        Raises:
            AnsibleExecutionException: if command execution failed
            AssertionError: if result of 'select' command is wrong
        """
        username, password = self.get_mysql_credentials(nodes)
        cmd = "mysql -u {0} -p{1}".format(username, password) + " -e \"{}\""
        for main_host in nodes:
            main_node = self.get_node(fqdns=[main_host.fqdn])
            # Create database and table
            self.execute_cmd(main_node,
                             cmd.format(config.MYSQL_CREATE_TABLE_CMD))
            # Execute 'select' on all nodes
            results = self.execute_cmd(
                nodes, cmd.format(config.MYSQL_CHECK_TABLE_CMD))
            for result in results:
                stdout = result.payload['stdout']
                assert_that(stdout, is_(config.MYSQL_EXPECTED_RESULT))
            # Delete database
            self.execute_cmd(main_node,
                             cmd.format(config.MYSQL_DELETE_DATABASE_CMD))

    @steps_checker.step
    def get_nodes_ip_for_interface(self, nodes, interface, check=True):
        """Step to get specific interface ips of nodes.

        Args:
            nodes (NodeCollection): nodes to get ips
            interface (str): interface name
            check (bool, optional): flag whether to check step or not

        Raises:
            AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            list: sorted ips
        """
        ips = []
        results = self.execute_cmd(
            nodes, "ifconfig {} | grep addr".format(interface), check=check)
        for result in results:
            ip = re.findall(r'inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
                            result.payload['stdout'])[0]
            ips.append(ip)
        if check:
            assert_that(ips, is_not(empty()))
        return sorted(ips)

    @steps_checker.step
    def get_rabbitmq_cluster_config_data(self, check=True):
        """Step to get names, FQDNs and IP addresses of RabbitMQ servers.

        IP addresses and other data are defined in RabbitMQ config files
        (in standard Erlang config format)

        Args:
            check (bool, optional): flag whether to check step or not

        Returns:
            tuple: (cluster_nodes, fqdns, ip_addresses)

        Raises:
            AssertionError: if unexpected format of config files
        """
        nodes = self.get_nodes(service_names=[config.RABBITMQ])
        cmd = "egrep -w 'cluster_nodes|ip' {}".format(config.RABBITMQ_CONFIG)
        results = self.execute_cmd(nodes, cmd, check=check)
        cluster_nodes = []
        ip_addresses = []
        fqdns = []
        for result in results:
            for node in nodes:
                if node.ip == result.host:
                    fqdns.append(node.fqdn)
                    break
            stdout = result.payload['stdout']
            # {cluster_nodes, {['rabbit@ctl01', 'rabbit@ctl02', ...], disc}} ->
            # rabbit@ctl01', rabbit@ctl02', ...
            # it's supposed that this line is identical on all nodes
            cluster_nodes = re.findall(r'\'(\w+@\w+)\'', stdout)
            # ex: {ip, "172.16.10.101" } -> 172.16.10.101
            ip_address = re.findall(r'(\d+\.\d+\.\d+\.\d+)', stdout)[0]
            ip_addresses.append(ip_address)

        assert_that(cluster_nodes, is_not(empty()))
        assert_that(len(cluster_nodes), is_(len(fqdns)))
        assert_that(len(ip_addresses), is_(len(fqdns)))

        return cluster_nodes, fqdns, ip_addresses

    @steps_checker.step
    def get_free_space(self, node, path, check=True):
        """Step to get free space in bytes.

        Args:
            node (NodeCollection): node to check free space
            path (str): path to check space
            check (bool, optional): flag whether to check step or not

        Raises:
            AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            int: free space on path in bytes
        """
        cmd = "df -hk {0} | awk 'NR==2 {{print $4}}'".format(path)
        results = self.execute_cmd(node, cmd, check=check)
        return results[0].payload['stdout']

    @steps_checker.step
    def block_iptables_input_output(self, node, duration, check=True):
        """Step to block input/output on node during some time.

        This step blocks input/output on node using iptables.
        Restoration of original iptables rules is scheduled i.e. it is done
        after finishing this step.

        Args:
            nodes (NodeCollection): nodes
            duration (int): time between block and unblock input/output
            check (bool, optional): flag whether to check step or not

        Raises:
            AnsibleExecutionException: if command execution
                failed in case of check=True
            AssertionError: if node is available after blocking
        """
        rule_file = '/tmp/iptables.rules'
        cmd = ("(sleep {0}; iptables-save > {1}; "
               "iptables -P INPUT DROP; iptables -P OUTPUT DROP; "
               "sleep {2}; iptables-restore < {1}) &".
               format(config.TIME_BEFORE_NETWORK_DOWN, rule_file, duration))
        # sleep before is necessary for correct execution of os-fault command
        self.execute_cmd(node, cmd, check=check)
        time.sleep(config.TIME_BEFORE_NETWORK_DOWN + 1)
        if check:
            # no access to node during some time
            results = self.execute_cmd(node, "date", check=False)
            assert_that(results, only_contains(
                has_properties(status=config.STATUS_UNREACHABLE)))
