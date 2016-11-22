"""
--------------------
Neutron SIGHUP tests
--------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import signal

import pytest

from stepler import config


@pytest.mark.idempotent_id('4f4c6072-d528-4488-b0a6-75a7753a0783',
                           agent_name=config.NEUTRON_L3_SERVICE)
@pytest.mark.idempotent_id('cd3fc092-6305-4659-ad88-a477e73588f7',
                           agent_name=config.NEUTRON_DHCP_SERVICE)
@pytest.mark.idempotent_id('e3c9814f-db44-4243-83b8-8ca5e74c676e',
                           agent_name=config.NEUTRON_OVS_SERVICE)
@pytest.mark.parametrize('agent_name', [config.NEUTRON_L3_SERVICE,
                                        config.NEUTRON_DHCP_SERVICE,
                                        config.NEUTRON_OVS_SERVICE])
def test_restart_agent_with_kill_sighup(agent_steps,
                                        os_faults_steps,
                                        agent_name):
    """**Scenario:** Restart neutron agent with kill SIGHUP command.

    **Steps:**

    #. Get PID of agent process on a host
    #. Kill a process with SIGHUP and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent = agent_steps.get_agents(name=agent_name, alive=True)[0]
    host_name = agent['host']
    node = os_faults_steps.get_nodes(fqdns=[host_name])

    log_file = config.AGENT_LOGS[agent_name]
    line_count = os_faults_steps.get_file_line_count(node, log_file)

    pid = os_faults_steps.get_process_pid(node, agent_name)

    os_faults_steps.send_signal_to_process(node, pid=pid,
                                           signal=signal.SIGHUP,
                                           delay=10)

    agent_steps.get_agents(name=agent_name, host_name=host_name, alive=True)

    os_faults_steps.check_process_pid(node, process_name=agent_name,
                                      expected_pid=pid)

    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_ERROR,
                                         expected_count=0,
                                         start_line_number=line_count)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         expected_count=0,
                                         start_line_number=line_count)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         expected_count=1,
                                         start_line_number=line_count)


@pytest.mark.idempotent_id('7e1a9733-df65-49af-9557-06274dd65bf4',
                           is_parent=True)
@pytest.mark.idempotent_id('5a943659-1fe2-460c-9ca5-6007095a355d',
                           is_parent=False)
@pytest.mark.parametrize('is_parent', [True, False], ids=['parent', 'child'])
def test_restart_metadata_agent_with_kill_sighup(agent_steps,
                                                 os_faults_steps,
                                                 is_parent):
    """**Scenario:** Restart metadata agent (parent or child) with SIGHUP.

    **Steps:**

    #. Get PID of metadata agent process (parent or child) on a host
    #. Kill a process with SIGHUP and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent_name = config.NEUTRON_METADATA_SERVICE
    agent = agent_steps.get_agents(name=agent_name, alive=True)[0]
    host_name = agent['host']
    node = os_faults_steps.get_nodes(fqdns=[host_name])

    log_file = config.AGENT_LOGS[agent_name]
    line_count = os_faults_steps.get_file_line_count(node, log_file)

    pid = os_faults_steps.get_process_pid(node, agent_name,
                                          get_parent=is_parent)

    os_faults_steps.send_signal_to_process(node, pid=pid,
                                           signal=signal.SIGHUP,
                                           delay=10)

    agent_steps.get_agents(name=agent_name, host_name=host_name, alive=True)

    os_faults_steps.check_process_pid(node, process_name=agent_name,
                                      check_parent=is_parent,
                                      expected_pid=pid)

    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_ERROR,
                                         expected_count=0,
                                         start_line_number=line_count)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         expected_count=0,
                                         start_line_number=line_count)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         expected_count=1,
                                         start_line_number=line_count)
