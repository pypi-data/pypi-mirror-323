# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from datetime import datetime, timedelta

import click
from caldav.lib import error

from caldavctl import dav
from caldavctl.click_utils import create_compatibility_check
from caldavctl.event_builder import event_builder, parse_event
from caldavctl.object_parser import ParserError
from caldavctl.utils import edit_text_with_editor, to_datetime

# Configuration

EMPTY_EVENT = '''# Mandatory
DTSTART: %(start)s
DTEND: %(end)s

# Recommended
SUMMARY:

# Optional
LOCATION:
CATEGORIES:
TIMEZONE: %(tz)s
PRIORITY: 5
DESCRIPTION: [[ ]]

# NOTES:
#
#   * Date and time:
#       * The dates must be in iso format, for instance: 2024-12-29 13:45;
#       * The timezone used is the one defined by default or the one defined in
#         the "TIMEZONE" key;
#   * Categories: the categories are a comma separated list;
#   * Priority: 1 - highest priority, 9 - lowest priority
#   * Description: The description can be multi line, just make sure it's
#     delimited by [[ ]].
'''


# Commands:

exclusive_option = create_compatibility_check(
    ['today', 'week', 'dtstart', 'dtend', 'day'],  # Exclusive options
    [['dtstart', 'dtend']])  # Except these two that can be used together


@click.command('list')
@click.option('-t', '--today',
              is_flag=True, show_default=True, default=False,
              callback=exclusive_option, help='Today\'s events',)
@click.option('-w', '--week',
              is_flag=True, show_default=True, default=False,
              callback=exclusive_option, help='This week\'s events')
@click.option('-s', '--dtstart',
              callback=exclusive_option, help='Date range, start date')
@click.option('-e', '--dtend',
              callback=exclusive_option, help='Date range, end date')
@click.option('-d', '--day',
              callback=exclusive_option, help='Events on the day')
@click.option('-sd', '--show-description',
              is_flag=True, show_default=True, default=False,
              help='Show the event\'s description.')
@click.option('-si', '--show-uid',
              is_flag=True, show_default=True, default=False,
              help='Show the event\'s UID.')
@click.pass_obj
def list_events(context, today, week, dtstart, dtend, day, show_description, show_uid):
    '''
    List events from the server list.
    '''
    tz = context['config'].tz()
    start_date = None
    end_date = None

    if today:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=tz)
        end_date = datetime.now().replace(hour=23, minute=59, second=59, tzinfo=tz)
    elif week:
        today_date = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=tz)
        start_date = today_date - timedelta(days=today_date.weekday())
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif dtstart and dtend:
        if dtstart:
            start_date = to_datetime(dtstart, tz)
        else:
            start_date = datetime(1900, 1, 1, tzinfo=tz)
        if dtend:
            end_date = to_datetime(dtend, tz)
        else:
            end_date = datetime(5000, 1, 1, tzinfo=tz)
    elif day:
        try:
            dt = datetime.fromisoformat(day)
            start_date = dt.replace(hour=0, minute=0, second=0, tzinfo=tz)
            end_date = dt.replace(hour=23, minute=59, second=59, tzinfo=tz)
        except ValueError:
            raise click.UsageError(f'Invalid date "{day}"')
    else:
        raise click.UsageError('You have to specify a time frame, for example with -t or -w.')

    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        # Check if the calendar supports events:
        if 'VEVENT' not in calendar.get_supported_components():
            raise click.UsageError('This calendar does not support events.')

        # Get events in time range
        events = calendar.search(
            start=start_date,
            end=end_date,
            event=True,
            expand=True,
            sort_keys=['dtstart']
        )
        for event in events:
            ev = event.icalendar_component
            date = ev.get('dtstart').dt
            summary = ev.get('summary', '')
            description = ev.get('description', '')
            uid = ev.get('uid')

            if isinstance(date, datetime):
                msg = f'{date.strftime('%Y-%m-%d %H:%M')} - {summary}'
            else:
                msg = f'{date} (day) - {summary}'
            if show_uid:
                msg += f' - {uid}'
            click.echo(msg)
            if show_description and description.strip():
                click.echo(description)


@click.command('create')
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-e', '--edit', is_flag=True, default=False, help='Edit the event on a text editor?')
@click.option('--dry-run', is_flag=True, default=False, help='Show only the iCalendar generated')
@click.pass_obj
def create_event(context, file, edit, dry_run):
    '''
    Create new event

    The event data can be read from stdin or from a file. Optionally the event
    can be edited using the default $EDITOR. If the option to edit is enabled
    and no file is defined using -f/--file, then an empty event is opened.
    '''
    tz = context['config'].tz()
    # Read the event definition
    if edit and file is sys.stdin:
        tomorrow = datetime.now() + timedelta(days=1)
        event_string = EMPTY_EVENT % {
            'tz': f'{tz}',
            'start': tomorrow.replace(hour=9, minute=0, second=0).strftime('%Y-%m-%d %H:%M'),
            'end': tomorrow.replace(hour=9, minute=45, second=0).strftime('%Y-%m-%d %H:%M'),
        }
    else:
        event_string = file.read()

    if edit:
        # Edit the file in $VISUAL or $EDITOR
        event_string = edit_text_with_editor(event_string, suffix='.ics')

    try:
        event_data = parse_event(event_string, tz)
    except ParserError as msg:
        raise click.UsageError(msg)

    event_ics = event_builder(event_data, tz)

    if dry_run:
        click.echo(event_ics)
    else:
        # Save the event to the calendar
        _, server = context['config'].get_server()
        calendar_id = context['config'].get_calendar()
        with dav.caldav_calendar(server, calendar_id) as calendar:
            # Check if the calendar supports events:
            if 'VEVENT' not in calendar.get_supported_components():
                raise click.UsageError('This calendar does not support events.')
            try:
                calendar.save_event(event_ics)
            except error.AuthorizationError as msg:
                raise click.UsageError(f'Error saving the event to the server: {msg}')

        click.echo('Event created successfully')


@click.command('delete')
@click.argument('event_id')
@click.pass_obj
def delete_event(context, event_id):
    '''Delete an event on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_event(server, calendar_id, event_id) as event:
        event.delete()
    print('Event deleted')
