"""
----------------------------
Config for disk partitioning
----------------------------
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


# Default partitioning
VOLUMES_DEFAULT = [{"mount": "/",
                    "type": "partition",
                    "file_system": "ext4",
                    "size": 11000}]

BAREMETAL_DISK_INFO_DEFAULT = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_DEFAULT}]

BAREMETAL_VIRTUAL_DISK_INFO_DEFAULT = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_DEFAULT}]


# Format root as EXT4, EXT2 /boot, and mount EXT4 /home/ and /media/
VOLUMES_EXT4_EXT4 = [
    {"mount": "/", "type": "partition", "file_system": "ext4", "size": 5000},
    {"mount": "/boot", "type": "partition", "file_system": "ext2", "size": 1000},
    {"mount": "/home", "type": "partition", "file_system": "ext4", "size": 3000},
    {"mount": "/media/partition", "type": "partition", "file_system": "ext4", "size": 2000}
    ]

BAREMETAL_DISK_INFO_EXT4_EXT4 = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_EXT4_EXT4}]

BAREMETAL_VIRTUAL_DISK_INFO_EXT4_EXT4 = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_EXT4_EXT4}]


# Format root as EXT4, EXT2 /boot, and mount EXT3 /home/ and /media/
VOLUMES_EXT4_EXT3 = [
    {"mount": "/", "type": "partition", "file_system": "ext4", "size": 5000},
    {"mount": "/boot", "type": "partition", "file_system": "ext2", "size": 1000},
    {"mount": "/home", "type": "partition", "file_system": "ext3", "size": 3000},
    {"mount": "/media/partition", "type": "partition", "file_system": "ext3", "size": 2000}
    ]

BAREMETAL_DISK_INFO_EXT4_EXT3 = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_EXT4_EXT3}]

BAREMETAL_VIRTUAL_DISK_INFO_EXT4_EXT3 = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_EXT4_EXT3}]


# Format root as XFS, EXT2 /boot, and mount XFS /home/ and /media/
VOLUMES_XFS_XFS = [
    {"mount": "/", "type": "partition", "file_system": "xfs", "size": 5000},
    {"mount": "/boot", "type": "partition", "file_system": "ext2", "size": 1000},
    {"mount": "/home", "type": "partition", "file_system": "xfs", "size": 3000},
    {"mount": "/media/partition", "type": "partition", "file_system": "xfs", "size": 2000}
    ]

BAREMETAL_DISK_INFO_XFS_XFS = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_XFS_XFS}]

BAREMETAL_VIRTUAL_DISK_INFO_XFS_XFS = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_XFS_XFS}]


# Format root as JFS, EXT2 /boot, and mount JFS /home/ and /media/
VOLUMES_JFS_JFS = [
    {"mount": "/", "type": "partition", "file_system": "jfs", "size": 5000},
    {"mount": "/boot", "type": "partition", "file_system": "ext2", "size": 1000},
    {"mount": "/home", "type": "partition", "file_system": "jfs", "size": 3000},
    {"mount": "/media/partition", "type": "partition", "file_system": "jfs", "size": 2000}
    ]

BAREMETAL_DISK_INFO_JFS_JFS = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_JFS_JFS}]

BAREMETAL_VIRTUAL_DISK_INFO_JFS_JFS = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_JFS_JFS}]


# Format root as EXT4, EXT2 /boot, and mount EXT4 /home/ and NTFS /media/
VOLUMES_JFS_NTFS = [
    {"mount": "/", "type": "partition", "file_system": "jfs", "size": 5000},
    {"mount": "/boot", "type": "partition", "file_system": "ext2", "size": 1000},
    {"mount": "/home", "type": "partition", "file_system": "jfs", "size": 3000},
    {"mount": "/media/partition", "type": "partition", "file_system": "jfs", "size": 2000}
    ]

BAREMETAL_DISK_INFO_JFS_NTFS = [
    {"name": "sda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "sda", "size": 12000, "volumes": VOLUMES_JFS_NTFS}]

BAREMETAL_VIRTUAL_DISK_INFO_JFS_NTFS = [
    {"name": "vda", "extra": [], "free_space": 12000, "type": "disk",
     "id": "vda", "size": 12000, "volumes": VOLUMES_JFS_NTFS}]
