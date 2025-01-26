# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from caldavctl.todo import (
    list_todos, create_todo, delete_todo, toggle_todo_complete, percentage_complete
)


def test_list_todos():
    runner = CliRunner()
    mock_calendar = MagicMock()
    mock_calendar.todos.return_value = [
        MagicMock(icalendar_component={
            'summary': 'Test Todo',
            'status': '',
            'percent-complete': 50,
            'description': 'Test Description',
            'uid': '1234'
        })
    ]

    with patch('caldavctl.dav.caldav_calendar', return_value=mock_calendar):
        result = runner.invoke(list_todos, ['--description'])

    assert result.exit_code == 0
    assert '[ ]  50% Test Todo - 1234' in result.output
    assert 'Test Description' in result.output


def test_create_todo():
    runner = CliRunner()
    mock_calendar = MagicMock()

    with patch('caldavctl.dav.caldav_calendar', return_value=mock_calendar):
        result = runner.invoke(
            create_todo, [
                'Test Todo',
                '--description', 'Test Description',
                '--due-date', '2024-12-31T23:59:59',
                '--priority', '1'
            ]
        )

    assert result.exit_code == 0
    assert 'todo created successfully: Test Todo' in result.output
    assert mock_calendar.save_event.called

# def test_delete_todo():
#     runner = CliRunner()
#     mock_todo = MagicMock()
#
#     with patch('caldavctl.dav.caldav_calendar_todo', return_value=mock_todo):
#         result = runner.invoke(delete_todo, ['1234'])
#
#     assert result.exit_code == 0
#     assert 'Todo deleted' in result.output
#     assert mock_todo.delete.called
#
# def test_toggle_todo_complete():
#     runner = CliRunner()
#     mock_todo = MagicMock()
#
#     # Test marking as completed
#     mock_todo.icalendar_component.get.return_value = ''
#
#     with patch('caldavctl.dav.caldav_calendar_todo', return_value=mock_todo):
#         result = runner.invoke(toggle_todo_complete, ['1234'])
#
#     assert result.exit_code == 0
#     assert 'Todo completed' in result.output
#     mock_todo.save.assert_called()
#
#     # Test marking as not completed
#     mock_todo.icalendar_component.get.return_value = 'COMPLETED'
#
#     with patch('caldavctl.dav.caldav_calendar_todo', return_value=mock_todo):
#         result = runner.invoke(toggle_todo_complete, ['1234'])
#
#     assert result.exit_code == 0
#     assert 'Todo completed' in result.output
#     mock_todo.save.assert_called()
#
# def test_percentage_complete():
#     runner = CliRunner()
#     mock_todo = MagicMock()
#     mock_todo.icalendar_component.get.side_effect = lambda key, default: {
#         'percent-complete': 50
#     }.get(key, default)
#
#     with patch('caldavctl.dav.caldav_calendar_todo', return_value=mock_todo):
#         result = runner.invoke(percentage_complete, ['1234', '75'])
#
#     assert result.exit_code == 0
#     assert 'Percentage set.' in result.output
#     mock_todo.save.assert_called()
