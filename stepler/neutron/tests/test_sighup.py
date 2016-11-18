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

import pytest

from stepler import config

AGENT_LOGS = {
    'neutron-l3-agent': 'l3-agent.log',
    'neutron-dhcp-agent': 'dhcp-agent.log',
    'neutron-openvswitch-agent': 'openvswitch-agent.log',
}


@pytest.mark.idempotent_id('4f4c6072-d528-4488-b0a6-75a7753a0783',
                           agent_name='neutron-l3-agent')
@pytest.mark.idempotent_id('cd3fc092-6305-4659-ad88-a477e73588f7',
                           agent_name='neutron-dhcp-agent')
@pytest.mark.idempotent_id('e3c9814f-db44-4243-83b8-8ca5e74c676e',
                           agent_name='neutron-openvswitch-agent')
@pytest.mark.parametrize('agent_name', ['neutron-l3-agent',
                                        'neutron-dhcp-agent',
                                        'neutron-openvswitch-agent'])
def test_restart_agent_with_kill_sighup(agent_steps,
                                        os_faults_steps,
                                        agent_name):
    """**Scenario:** Restart neutron agent with kill SIGHUP command.

    **Steps:**

    #. Get PID of agent process on a host
    #. Kill a process with SIGHUP and wait for 10 seconds
    #. Check state of l3-agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent = agent_steps.get_agents(name=agent_name, alive=True)[0]
    host_name = agent['host']
    node = os_faults_steps.get_nodes(fqdns=[host_name])

    log_file = "{}/{}".format(config.NEUTRON_LOG_DIR, AGENT_LOGS[agent_name])
    line_count = os_faults_steps.get_file_line_count(node, log_file)

    pid = os_faults_steps.get_process_pid(node, agent_name)

    os_faults_steps.send_signal_to_process(node, pid=pid, signal='HUP',
                                           delay=10)

    agent_steps.get_agents(name=agent_name, host_name=host_name, alive=True)

    os_faults_steps.get_process_pid(node, process_name=agent_name,
                                    expected_pid=pid)

    os_faults_steps.check_keyword_in_file(node, file_name=log_file,
                                          keyword='ERROR', expected_count=0,
                                          start_line_number=line_count)
    os_faults_steps.check_keyword_in_file(node, file_name=log_file,
                                          keyword='TRACE', expected_count=0,
                                          start_line_number=line_count)
    os_faults_steps.check_keyword_in_file(node, file_name=log_file,
                                          keyword='SIGHUP', expected_count=1,
                                          start_line_number=line_count)
