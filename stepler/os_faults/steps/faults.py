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

import os
import re
import tempfile
import time

from hamcrest import (assert_that, empty, has_item, has_properties, is_not,
                      only_contains, has_items, has_length, is_, equal_to,
                      contains_inanyorder, is_in)  # noqa H301

from stepler import base
from stepler import config
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ['OsFaultsSteps']


class OsFaultsSteps(base.BaseSteps):
    """os-faults steps."""

    @steps_checker.step
    def get_nodes(self, fqdns=None, service_names=None, check=True):
        """Step to get nodes.

        Args:
            fqdns (list): nodes hostnames to filter
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            list of nodes
        """
        if service_names:
            service_fqdns = set()
            for service_name in service_names:
                nodes = self._client.get_service(service_name).get_nodes()
                for host in nodes.hosts:
                    service_fqdns.add(host.fqdn)
            if not fqdns:
                fqdns = service_fqdns
            else:
                fqdns = set(fqdns)
                fqdns &= service_fqdns
        nodes = self._client.get_nodes(fqdns=fqdns)

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
            FuelNodeCollection: one node
        """
        nodes = self.get_nodes(
            fqdns=fqdns, service_names=service_names, check=check)
        return nodes.pick()

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
            return expect_that(service.get_nodes(), matcher)

        waiter.wait(_check_service_state, timeout_seconds=timeout)

    @steps_checker.step
    def restart_services(self, names, check=True):
        """Step to restart services.

        Args:
            names (list): service names
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
        """
        services = []
        for name in names:
            service = self._client.get_service(name=name)
            services.append(service)
            service.restart()
        if check:
            # TODO(gdyuldin): make normal check
            assert_that(services, is_not(empty()))

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
            AssertioError: if any of files doesn't contains `line`
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
        """Step to make backup of file with `path`.

        This step makes a copy of file to new file with `suffix` in same
            folder.

        Args:
            nodes (obj): nodes to backup file on them
            file_path (str): path to file on remote hosts
            suffix (str): suffix to append to original file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file not exists after step.

        Returns:
            str: path to backup file
        """
        suffix = suffix or utils.generate_ids('backup', length=30)
        backup_path = "{}.{}".format(file_path, suffix)

        task = {
            'command': 'cp "{path}" "{backup_path}"'.format(
                path=file_path, backup_path=backup_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, backup_path)

        return backup_path

    @steps_checker.step
    def restore_backup(self, nodes, file_path, backup_path, check=True):
        """Step to restore file with `path` from backup.

        This step restore file from backup with `suffix` placed in same folder.

        Args:
            nodes (obj): nodes to restore file on them
            file_path (str): path to file on remote hosts
            backup_path (str): path to backup
            suffix (str): suffix to make backup file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file exists after step.
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
            AssertionError: if any of nodes doesn't contains file
        """
        command = 'ls "{path}"'.format(path=file_path)
        if not present:
            command = '! ' + command
        task = {'shell': command}
        result = nodes.run_task(task)
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
    def execute_cmd(self, nodes, cmd, check=True):
        """Execute provided bash command on nodes.

        Args:
            nodes (NodeCollection): nodes to execute command on them
            cmd (str): bash command to execute
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            list: AnsibleExecutionRecord(s)
        """
        task = {'shell': cmd}
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
    def get_file_line_count(self, node, file_name, check=True):
        """Step to get line count in a textual file on a single node.

        Args:
            node (NodeCollection): node
            file_name (str): name of textual file
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            int: line count
        """
        cmd = "cat {} | wc -l".format(file_name)
        result = self.execute_cmd(node, cmd, check=check)
        return int(result[0].payload['stdout'])

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
        pids.remove(1)
        main_pids = [pid for pid in pids if pids.count(pid) > 1]
        if len(main_pids) == 0:
            # no children
            main_pids = pids
            children_pids = []
        else:
            children_pids = [pid for pid in pids if pids.count(pid) == 1]
        assert_that(main_pids, is_not(empty()))
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
    def check_string_in_file(self, node, file_name, keyword, expected_count,
                             start_line_number=None):
        """Step to check number of keywords in a textual file on a single node.

        Args:
            node (NodeCollection): node
            file_name (str): name of textual file
            keyword (str): string to search
            expected_count (int): expected count of lines containing keyword
            start_line_number (int|None): number of first line for searching

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True or real count of lines with
                keyword is not equal to expected one
        """
        if start_line_number:
            cmd = "tail -n +{0} {1}".format(start_line_number, file_name)
        else:
            cmd = "cat {}".format(file_name)
        if expected_count == 0:
            cmd += " | grep -q '{}'; echo $?".format(keyword)
            expected_value = 1
        else:
            cmd += " | grep '{}' | wc -l".format(keyword)
            expected_value = expected_count
        result = self.execute_cmd(node, cmd)
        value = int(result[0].payload['stdout'])
        assert_that(value, is_(expected_value))

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

        nodes = self.get_nodes()
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
        expected_strings = ["bps_rd={}".format(limit),
                            "bps_wr={}".format(limit)]
        for expected_string in expected_strings:
            assert_that(expected_string, is_in(stdout))

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
        if all(node_result.status == config.STATUS_OK
               for node_result in result):
            return config.NETWORK_TYPE_VXLAN
        else:
            return config.NETWORK_TYPE_VLAN

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
