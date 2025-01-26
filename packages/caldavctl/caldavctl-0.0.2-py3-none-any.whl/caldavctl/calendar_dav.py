# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import caldav
import click
from caldav.lib import error

from caldavctl import dav


# CALENDARS

@click.command('list')
@click.pass_obj
def list_calendars(context):
    '''
    List the available calendars present on the server or servers
    '''
    for name, server in context['config'].servers():
        with caldav.DAVClient(**server) as client:
            for calendar in client.principal().calendars():
                click.echo(f'Server {name}:')
                click.echo(f'    CALENDAR = {calendar.name}')
                click.echo(f'    ID = {calendar.id}')
                click.echo(f'    COMPONENTS = {', '.join(calendar.get_supported_components())}')
                click.echo(f'    URL = {calendar.url}')
                click.echo()


@click.command('create')
@click.argument('name')
@click.option('--cal-id')
@click.pass_obj
def create_calendar(context, name, cal_id=None):
    '''
    Create a calendar on the default server or optionally in another server
    '''
    _, server = context['config'].get_server()

    with caldav.DAVClient(**server) as client:
        principal = client.principal()
        try:
            new_calendar = principal.make_calendar(name=name, cal_id=cal_id)
        except error.AuthorizationError as msg:
            raise click.UsageError(f'Error creating the calendar (maybe duplicate UID?) with: {msg}')

        print(f'Calendar "{name}" created.')
    return new_calendar


@click.command('delete')
@click.argument('calendar_id')
@click.pass_obj
def delete_calendar(context, calendar_id):
    '''
    Delete a calendar from the default server or optionally from another
    server. It's possible to have calendars with the same name, so we use the
    id to identify the calendar to delete.
    '''
    _, server = context['config'].get_server()

    with dav.caldav_calendar(server, calendar_id) as calendar:
        name = calendar.name
        calendar.delete()
        print(f'Calendar "{name}" deleted.')
