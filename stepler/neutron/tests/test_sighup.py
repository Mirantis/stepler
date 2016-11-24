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
def test_restart_agent_controller_with_sighup(agent_steps,
                                              os_faults_steps,
                                              agent_name):
    """**Scenario:** Restart neutron agent with kill SIGHUP command.

    **Steps:**

    #. Find a controller with running neutron agent
    #. Get PID of agent process
    #. Send SIGHUP to process and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    node = os_faults_steps.get_node(
        service_names=[config.NOVA_API, agent_name],
        all_services_on_node=True)
    host_name = node.hosts[0].fqdn

    log_file = config.AGENT_LOGS[agent_name][0]
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
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         start_line_number=line_count,
                                         expected_count=1)


@pytest.mark.idempotent_id('336891a3-d68b-4069-be17-93431fe9b901',
                           is_parent=True)
@pytest.mark.idempotent_id('d4289bae-0fcf-4101-9ca1-c32c47471ce1',
                           is_parent=False)
@pytest.mark.parametrize('is_parent', [True, False], ids=['parent', 'child'])
def test_restart_neutron_server_with_sighup(os_faults_steps,
                                            is_parent):
    """**Scenario:** Restart neutron server (parent or child) with SIGHUP.

    **Steps:**

    #. Find a controller with running metadata agent
    #. Get PID of neutron server process (parent or child)
    #. Send SIGHUP to process and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    node = os_faults_steps.get_node(
        service_names=[config.NOVA_API, config.NEUTRON_SERVER_SERVICE],
        all_services_on_node=True)

    log_file = config.AGENT_LOGS[config.NEUTRON_SERVER_SERVICE][0]
    line_count = os_faults_steps.get_file_line_count(node, log_file)

    pid = os_faults_steps.get_process_pid(node, config.NEUTRON_SERVER_SERVICE,
                                          get_parent=is_parent)

    os_faults_steps.send_signal_to_process(node, pid=pid,
                                           signal=signal.SIGHUP,
                                           delay=10)

    os_faults_steps.check_service_state(config.NEUTRON_SERVER_SERVICE, node)

    os_faults_steps.check_process_pid(node, config.NEUTRON_SERVER_SERVICE,
                                      check_parent=is_parent,
                                      expected_pid=pid)

    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_ERROR,
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         start_line_number=line_count,
                                         must_present=False)
    if is_parent:
        os_faults_steps.check_string_in_file(node, file_name=log_file,
                                             keyword=config.STR_SIGHUP,
                                             start_line_number=line_count,
                                             must_present=True)
    else:
        os_faults_steps.check_string_in_file(node, file_name=log_file,
                                             keyword=config.STR_SIGHUP,
                                             start_line_number=line_count,
                                             expected_count=1)


@pytest.mark.idempotent_id('7e1a9733-df65-49af-9557-06274dd65bf4',
                           is_parent=True)
@pytest.mark.idempotent_id('5a943659-1fe2-460c-9ca5-6007095a355d',
                           is_parent=False)
@pytest.mark.parametrize('is_parent', [True, False], ids=['parent', 'child'])
def test_restart_metadata_agent_controller_with_sighup(agent_steps,
                                                       os_faults_steps,
                                                       is_parent):
    """**Scenario:** Restart metadata agent (parent or child) with SIGHUP.

    **Steps:**

    #. Find a controller with running metadata agent
    #. Get PID of metadata agent process (parent or child)
    #. Send SIGHUP to process and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent_name = config.NEUTRON_METADATA_SERVICE
    node = os_faults_steps.get_node(
        service_names=[config.NOVA_API, agent_name],
        all_services_on_node=True)
    host_name = node.hosts[0].fqdn

    log_file = config.AGENT_LOGS[agent_name][0]
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
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         start_line_number=line_count,
                                         expected_count=1)


# TODO (ssokolov) add condition 'dvr'
@pytest.mark.idempotent_id('9510de56-6d71-4c43-8429-cdcc3682550d',
                           is_parent=True)
@pytest.mark.idempotent_id('7565595b-6c3d-4dfc-a84f-98122c1a51ef',
                           is_parent=False)
@pytest.mark.parametrize('is_parent', [True, False], ids=['parent', 'child'])
def test_restart_metadata_agent_compute_with_sighup(agent_steps,
                                                    os_faults_steps,
                                                    is_parent):
    """**Scenario:** Restart metadata agent (parent or child) with SIGHUP.

    **Steps:**

    #. Find a compute with running metadata agent
    #. Get PID of metadata agent process (parent or child)
    #. Send SIGHUP to process and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent_name = config.NEUTRON_METADATA_SERVICE
    node = os_faults_steps.get_node(
        service_names=[config.NOVA_COMPUTE, agent_name],
        all_services_on_node=True)
    host_name = node.hosts[0].fqdn

    log_file = config.AGENT_LOGS[agent_name][1]
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
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         start_line_number=line_count,
                                         expected_count=1)


# TODO (ssokolov) add condition 'dvr'
@pytest.mark.idempotent_id('b61918e7-d9fc-4d8d-aec0-5b19695da4ef')
def test_restart_l3_agent_compute_with_sighup(agent_steps,
                                              os_faults_steps):
    """**Scenario:** Restart l3 agent with SIGHUP on compute.

    **Steps:**

    #. Find a compute with running l3 agent
    #. Get PID of l3 agent process
    #. Send SIGHUP to process and wait for 10 seconds
    #. Check state of agent
    #. Check that pid is not changed
    #. Check that no new ERROR and TRACE messages appear in log
    #. Check that only one SIGHUP message appear in log
    """
    agent_name = config.NEUTRON_L3_SERVICE
    node = os_faults_steps.get_node(
        service_names=[config.NOVA_COMPUTE, agent_name],
        all_services_on_node=True)
    host_name = node.hosts[0].fqdn

    log_file = config.AGENT_LOGS[agent_name][1]
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
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_TRACE,
                                         start_line_number=line_count,
                                         must_present=False)
    os_faults_steps.check_string_in_file(node, file_name=log_file,
                                         keyword=config.STR_SIGHUP,
                                         start_line_number=line_count,
                                         expected_count=1)
