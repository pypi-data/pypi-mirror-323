# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
The tests on this file need a testing server that allows us to create a
calendar and that supports managing todos.

Is you have such calendar server configured, then you can run these tests by
defining the environment variable "RUN_NOMOCK_TESTS=yes".

The tests will create a new calendar, do the tests and then destroy the created
calendar.
'''

import os
import uuid

import pytest
from click.testing import CliRunner

from caldavctl import cli

RUN_NOMOCK_TESTS = os.environ.get('RUN_NOMOCK_TESTS', 'NO').upper() == 'YES'


@pytest.fixture(scope="module")
def test_calendar():
    calendar_id = str(uuid.uuid4())
    runner = CliRunner()

    # Setup the testing environment - Create Calendar
    result = runner.invoke(
        cli.cli_group,
        ["calendar", "create", "--cal-id", calendar_id, "TestCalendar"]
    )
    assert result.exit_code == 0, f"Failed to create test calendar: {result.output}"

    yield calendar_id

    # Delete Calendar
    result = runner.invoke(
        cli.cli_group,
        ["calendar", "delete", calendar_id]
    )
    assert result.exit_code == 0, f"Failed to delete test calendar: {result.output}"


@pytest.mark.skipif(not RUN_NOMOCK_TESTS, reason='RUN_NOMOCK_TESTS not set to "yes"')
def test_todo_create(test_calendar):
    calendar_id = test_calendar
    runner = CliRunner()
    result = runner.invoke(
        cli.cli_group,
        ["--calendar", calendar_id, "todo", "create", "This is an example TODO"]
    )
    breakpoint()
    assert True


@pytest.mark.skipif(not RUN_NOMOCK_TESTS, reason='RUN_NOMOCK_TESTS not set to "yes"')
def test_todo_delete(test_calendar):
    calendar_id = test_calendar
    assert True
