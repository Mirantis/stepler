#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(required=True, type='str')
        ))

    command = module.params['command']

    cmd = "bash -c 'source /root/openrc; {}'".format(command)
    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    module.exit_json(cmd=cmd, rc=rc, stderr=stderr, stdout=stdout)


if __name__ == '__main__':
    main()
