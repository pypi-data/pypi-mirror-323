# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import os
import subprocess
import tempfile

from datetime import datetime

import click


def edit_text_with_editor(initial_text: str, suffix: str = '.tmp') -> str:
    # Determine the editor from $EDITOR or $VISUAL, defaulting to 'vi'
    editor = os.environ.get('VISUAL') or os.environ.get('EDITOR') or 'vi'

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w+') as temp_file:
        temp_filename = temp_file.name
        temp_file.write(initial_text)
        temp_file.flush()  # Ensure content is written to disk

    try:
        # Open the editor with the temporary file
        subprocess.run([editor, temp_filename])

        # Read the modified content back
        with open(temp_filename, 'r') as temp_file:
            modified_text = temp_file.read()
    finally:
        # Clean up the temporary file
        os.unlink(temp_filename)

    return modified_text


def deep_merge_dict(source, destination):
    """
    Merge two dictionaries, if key exists on both dictionaries then the source will prevail

    Based on:
    From: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            if isinstance(node, dict):
                # see test_deep_merge_dict_conflicting_types
                deep_merge_dict(value, node)
            else:
                destination[key] = value
        else:
            destination[key] = value
    return destination


def check_if_naive(date, tz):
    '''
    Check if a date is naïve and if it is localize it with the timezone defined
    in tz.
    '''
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date = tz.localize(date)
    return date


def to_datetime(dt_str, tz):
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        raise click.UsageError(f'Invalid date "{dt_str}", use iso format.')
    return dt
