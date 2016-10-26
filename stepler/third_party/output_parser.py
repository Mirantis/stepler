"""
------------------------------------------------------
Collection of utilities for parsing CLI clients output
------------------------------------------------------
"""
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re

from stepler.third_party import logger

LOG = logger.LOGGER
delimiter_line = re.compile('^\+\-[\+\-]+\-\+$')


# TODO(gdyuldin): refactor after coping from tempest
def listing(output_lines):
    """Return list of dicts with basic item info parsed from cli output."""

    items = []
    table_ = table(output_lines)
    for row in table_['values']:
        item = {}
        for col_idx, col_key in enumerate(table_['headers']):
            item[col_key] = row[col_idx]
        items.append(item)
    return items


# TODO(gdyuldin): refactor after coping from tempest
def table(output_lines):
    """Parse single table from cli output.

    Return dict with list of column names in 'headers' key and
    rows in 'values' key.
    """
    table_ = {'headers': [], 'values': []}
    columns = None

    if not isinstance(output_lines, list):
        output_lines = output_lines.split('\n')

    if not output_lines[-1]:
        # skip last line if empty (just newline at the end)
        output_lines = output_lines[:-1]

    for line in output_lines:
        if delimiter_line.match(line):
            columns = _table_columns(line)
            continue
        if '|' not in line:
            LOG.warning('skipping invalid table line: %s' % line)
            continue
        row = []
        for col in columns:
            row.append(line[col[0]:col[1]].strip())
        if table_['headers']:
            table_['values'].append(row)
        else:
            table_['headers'] = row

    return table_


# TODO(gdyuldin): refactor after coping from tempest
def _table_columns(first_table_row):
    """Find column ranges in output line.

    Return list of tuples (start,end) for each column
    detected by plus (+) characters in delimiter line.
    """
    positions = []
    start = 1  # there is '+' at 0
    while start < len(first_table_row):
        end = first_table_row.find('+', start)
        if end == -1:
            break
        positions.append((start, end))
        start = end + 1
    return positions
