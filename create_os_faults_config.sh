#!/bin/bash

echo "Checking keypair..."
KEYPAIR_PATH=$1
if [ -z "$1" ]; then
KEYPAIR_PATH=$HOME'/.ssh/os_faults'
fi

echo "Getting VM ip..."
VM_IP=$(ifconfig ens3 | grep 'inet addr' | cut -d: -f2 | awk '{ print $1 }')

echo "Generating os-fault config..."
cat << EOF > os_fault_config.json
{'cloud_management': {
   'driver': 'tcpcloud',
    'args': {
        'address': '$VM_IP',
        'username': 'ubuntu',
        'master_sudo': True,
        'slave_username': 'ubuntu',
        'slave_name_regexp': 'cfg*',
        'private_key_file': '$KEYPAIR_PATH'
        }
  }
}
EOF
