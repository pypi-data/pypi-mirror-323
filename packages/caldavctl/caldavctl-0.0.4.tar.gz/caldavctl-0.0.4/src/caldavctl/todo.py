# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
import uuid

import click

from caldavctl import dav

from icalendar import Todo


@click.command('list')
@click.option('-d', '--description', is_flag=True, show_default=True, default=False,
              help='Show the event\'s description.')
@click.option('-a', '--all', is_flag=True, show_default=True, default=False,
              help='Show all todos, including completed todos.')
@click.pass_obj
def list_todos(context, description, all):
    '''
    List todos from the default server and default calendar
    '''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        # Check if the calendar supports events:
        if 'VTODO' not in calendar.get_supported_components():
            raise click.UsageError(f'This calendar "{calendar.name}" '
                                   'does not support todos.')
        # Get events in time range
        todos = calendar.todos(include_completed=all)
        for todo in todos:
            td = todo.icalendar_component
            summary = td.get('summary')
            status = '[✓]' if td.get('status', '') else '[ ]'
            percentage = td.get('percent-complete', 0)
            desc = td.get('description', '')
            uid = td.get('uid')

            click.echo(f'{status} {percentage:3}% {summary} - {uid}')
            if description and desc.strip():
                click.echo(desc)


@click.command('create')
@click.argument('summary')
@click.option('--description')
@click.option('--due-date')
@click.option('--priority')
@click.pass_obj
def create_todo(context, summary, description, due_date, priority):
    '''Create a todo on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar(server, calendar_id) as calendar:
        todo = Todo()

        todo.add('uid', str(uuid.uuid4()))
        todo.add('summary', summary)
        if description:
            todo.add('description', description)
        if due_date:
            try:
                dt = tz.localize(datetime.fromisoformat(due_date))
            except ValueError:
                raise click.UsageError(f'Invalid value for due date "{due_date}"')
            todo.add('due', dt)
        if priority:
            todo.add('priority', priority)
        todo.add('created', datetime.now(tz))
        todo.add('last-modified', datetime.now(tz))

        # Convert the todo to a string
        todo_string = todo.to_ical().decode('utf-8')

        try:
            calendar.save_event(todo_string)
            click.echo(f"todo created successfully: {summary}")
        except Exception as e:
            click.echo(f"Error creating todo: {e}")


@click.command('delete')
@click.argument('todo_id')
@click.pass_obj
def delete_todo(context, todo_id):
    '''Delete a todo on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        todo.delete()
    click.echo('Todo deleted')


@click.command('toggle')
@click.argument('todo_id')
@click.pass_obj
def toggle_todo_complete(context, todo_id):
    '''Toggle todo completed'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        if todo.icalendar_component.get('status', ''):
            del todo.icalendar_component['status']
            del todo.icalendar_component['completed']
        else:
            todo.icalendar_component.add('status', 'COMPLETED')
            todo.icalendar_component.add('completed', datetime.now(tz))
        todo.save()
        click.echo('Todo completed')


@click.command('percentage')
@click.argument('todo_id')
@click.argument('percent', type=click.IntRange(0, 100))
@click.pass_obj
def percentage_complete(context, todo_id, percent):
    '''Set percentage completed'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        if percent == todo.icalendar_component.get('percent-complete', 0):
            click.echo('No change!')
            return
        if 'percent-complete' in todo.icalendar_component:
            del todo.icalendar_component['percent-complete']
        todo.icalendar_component.add('percent-complete', percent)
        if todo.icalendar_component.get('status', ''):
            del todo.icalendar_component['status']
            del todo.icalendar_component['completed']
        if percent == 100:
            todo.icalendar_component.add('status', 'COMPLETED')
            todo.icalendar_component.add('completed', datetime.now(tz))
        todo.save()
        click.echo('Percentage set.')
