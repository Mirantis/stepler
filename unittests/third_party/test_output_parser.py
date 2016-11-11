# -*- coding: utf-8 -*-
"""
-----------------------
Output parser unittests
-----------------------
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

from stepler.third_party import output_parser


def test_parse_non_ascii_table():
    """Test correct find indentation for tables with non-ASCII symbols."""
    raw_data = (u'+-------------+--------------------------------------+\n'
                u'|   Property  |                Value                 |\n'
                u'+-------------+--------------------------------------+\n'
                u'|     name    |               シンダー                 |\n'
                u'+-------------+--------------------------------------+')
    table = output_parser.table(raw_data)
    assert table['values'][0][1] == u"シンダー"


def test_parse_multiline_cells():
    """Test correct parsing multiline cells for 2-columns tables."""
    raw_data = (u'+------+-------+\n'
                u'| foo  | bar   |\n'
                u'+------+-------+\n'
                u'| data | [     |\n'
                u'|      |   1,  |\n'
                u'|      |   2,  |\n'
                u'|      |   3   |\n'
                u'|      | ]     |\n'
                u'+------+-------+')
    table = output_parser.table(raw_data)
    assert len(table['values']) == 1
