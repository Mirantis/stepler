=========
os_faults
=========

----------
Annotation
----------

os_faults is an external OpenStack fault-injection library.
The library does destructive actions inside an OpenStack cloud. It provides an abstraction layer over different types of cloud deployments. The actions are implemented as drivers (e.g. DevStack driver, Fuel driver, Libvirt driver, IPMI driver).
See https://github.com/openstack/os-faults for more details.

Stepler provides some fixtures and steps based on os_faults functions, ex: get list of nodes, restart services etc.
The library os_faults is installed during installation of Stepler.

-------------
Configuration
-------------

Before using os_faults, the cloud configuration file in JSON format must be created. This file defines cloud type, IP address and other data. Its example for a cloud based on Fuel is shown below.

{
  'cloud_management': {
    'driver': 'fuel',
    'args': {
      'address': '10.109.0.2',
      'username': 'root'
    }
  },
  'power_management': {
    'driver': 'libvirt',
    'args': {
      'connection_uri': "qemu+unix:///system"
    }
  }
}

Pathname of such configuration file must be set via the environment variable OS_FAULTS_CONFIG, ex:
export OS_FAULTS_CONFIG="/home/smith/os_fault_config.json"

``Important``

For correct running of os_faults, there should be provided access via keys from host where tests are running to all nodes. It can be done using the special script.
TODO: add later

