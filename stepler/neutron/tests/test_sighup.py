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
    'neutron-l3-agent': 'l3-agent.log'
}


@pytest.mark.idempotent_id('4f4c6072-d528-4488-b0a6-75a7753a0783',
                           agent_name='neutron-l3-agent')
@pytest.mark.parametrize('agent_name', ['neutron-l3-agent'])
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

    cmd = "cat {} | wc -l".format(log_file)
    old_length = os_faults_steps.execute_cmd(node, cmd)[0].payload['stdout']

    cmd_pid = "ps aux | grep -v root | grep {}".format(agent_name)
    cmd_pid += " | awk '{print $2}'"
    pid = os_faults_steps.execute_cmd(node, cmd_pid)[0].payload['stdout']

    cmd = "kill -HUP {} && sleep 10".format(pid)
    os_faults_steps.execute_cmd(node, cmd)

    agent_steps.get_agents(name=agent_name, host_name=host_name, alive=True)

    os_faults_steps.execute_cmd(node, cmd_pid, expected_strings=[pid])

    cmd = ("tail -n +{0} {1} | egrep -q 'ERROR|TRACE' | wc -l".
           format(old_length, log_file))
    os_faults_steps.execute_cmd(node, cmd, expected_strings=['0'])

    cmd = ("tail -n +{0} {1} | grep 'SIGHUP' | wc -l".
           format(old_length, log_file))
    os_faults_steps.execute_cmd(node, cmd, expected_strings=['1'])
