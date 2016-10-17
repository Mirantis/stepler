"""
----------------
Chunk serializer
----------------

Nova instance metadata has restriction - keys and values of it can contains not
more than 255 symbols. This sesializer dumps passed metadata to json,
split to to cmall chanks and makes a dict with this chunks.
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
# limitations under the License.from functools import wraps

import json
from six import moves


# TODO(schipiga): add unittests for that
def dump(obj, prefix):
    """Transform object to dict with small chunks of jsoned object.


    Example:
        >>> dump({'keypair': 'a' * 260}, prefix='some_prefix_')
        {
            'some_prefix_0':
                '{"keypair": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                # cutted
                aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'some_prefix_1': 'aaaaaaaaaaaaaaaaaa"}'
        }

    Args:
        obj (object): object to serialize. Should be json-serializable
        prefix (str): prefix to result dict keys
    Returns:
        dict: dict with small chunks of json object representation
    """
    meta = {}
    buf = moves.StringIO(json.dumps(obj))
    i = 0
    while True:
        data = buf.read(255)
        if not data:
            break
        meta['{}{}'.format(prefix, i)] = data
        i += 1
    return meta


def load(meta, prefix):
    """Restore object from dict, created with `dump` function.

    Args:
        meta (dict): dict with serialized object
        prefix (str): serialized records keys prefix
    Return:
        object: deserialized object
    """
    items = []
    for k, v in meta.items():
        if not k.startswith(prefix):
            return
        i = int(k[len(prefix):])
        items.append((i, v))
    items = sorted(items, key=lambda x: x[0])
    value = ''.join(x[1] for x in items)
    return json.loads(value)
