# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
CalDAV tool
'''

import click

import caldavctl.calendar_dav as calendar
import caldavctl.event as event
import caldavctl.todo as todo
import caldavctl.journal as journal
import caldavctl.ics as ics
import caldavctl.backup as backup

from caldavctl.config import Config


# General options

@click.group()
@click.option('-c', '--config', 'config_file', envvar='CALDAV_CONFIG', help='Configuration file')
@click.option('--name', envvar='CALDAV_NAME', help='Server nickname')
@click.option('--username', envvar='CALDAV_USERNAME', help='Username on the CalDAV server')
@click.option('--passwd', envvar='CALDAV_PASSWD', help='Password on the CalDAV server')
@click.option('--url', envvar='CALDAV_URL', help='Calendar CalDAV url')
@click.option('--timezone', envvar='CALDAV_TIMEZONE', help='Your time zone')
@click.option('--server', help='Default server (use nickname)')
@click.option('--calendar', help='Default calendar id')
@click.pass_context
def cli_group(context,
              config_file,
              name, username, passwd, url, timezone,
              server, calendar):
    '''
    caldavctl - command line CalDAV client
    '''

    config = Config(
        config_file,
        name,
        username,
        passwd,
        url,
        timezone,
        server,
        calendar
    )

    context.obj = {
        'config': config,
        'option': []
    }


# CALENDAR

@cli_group.group('calendar')
@click.pass_context
def calendar_commands(context):
    '''Commands that deal with the calendars on the server'''
    pass


calendar_commands.add_command(calendar.list_calendars)
calendar_commands.add_command(calendar.create_calendar)
calendar_commands.add_command(calendar.delete_calendar)


# EVENTS

@cli_group.group('event')
@click.pass_context
def event_commands(context):
    '''Event management'''
    pass


event_commands.add_command(event.list_events)
event_commands.add_command(event.create_event)
event_commands.add_command(event.delete_event)


# TODOS

@cli_group.group('todo')
@click.pass_context
def todo_commands(context):
    '''Todo management'''
    pass


todo_commands.add_command(todo.list_todos)
todo_commands.add_command(todo.create_todo)
todo_commands.add_command(todo.delete_todo)
todo_commands.add_command(todo.toggle_todo_complete)
todo_commands.add_command(todo.percentage_complete)


# JOURNALS

@cli_group.group('journal')
@click.pass_context
def journal_commands(context):
    '''Journal management'''
    pass


journal_commands.add_command(journal.list_journals)


# ICS

@cli_group.group('ics')
@click.pass_context
def ics_commands(context):
    '''iCalendar file operations'''
    pass


ics_commands.add_command(ics.get_todo)
ics_commands.add_command(ics.create_todo)
ics_commands.add_command(ics.get_event)


# Backup

@cli_group.group('br')
@click.pass_context
def backup_and_restore_commands(context):
    '''Backup or restore a calendar'''
    pass


backup_and_restore_commands.add_command(backup.backup_calendar)
backup_and_restore_commands.add_command(backup.restore_calendar)


def main():
    cli_group()
