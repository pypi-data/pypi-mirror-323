import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(short_help="Commands for managing custom days within calendars")
def custom_day():
    pass


@custom_day.command("get", short_help="Retrieves information on a specific Custom Day")
@click.argument(
    "args", nargs=-1, metavar="customdayid=value customdayname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_custom_day(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.custom_days.get_custom_day(**vars_dict)
    process_output(output, select, response)


@custom_day.command(
    "update", short_help="Modifies the Custom Day specified by the sysId"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value comments=value category=value ctype=value month=value dayofweek=value relfreq=value day=value date=value date_list=value adjustment=value adjustment_amount=value adjustment_type=value nth_amount=value nth_type=value retain_sys_ids=value observed_rules=value period=value holiday=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_custom_day(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.custom_days.update_custom_day(**vars_dict)
    process_output(output, select, response)


@custom_day.command("create", short_help="Creates a new Custom Day")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_custom_day(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.custom_days.create_custom_day(**vars_dict)
    process_output(output, select, response)


@custom_day.command("delete", short_help="Deletes a specific Custom Day")
@click.argument(
    "args", nargs=-1, metavar="customdayid=value customdayname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_custom_day(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.custom_days.delete_custom_day(**vars_dict)
    process_output(output, select, response)


@custom_day.command("list", short_help="Retrieves information on all Custom Days")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_custom_days(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.custom_days.list_custom_days(**vars_dict)
    process_output(output, select, response)


@custom_day.command(
    "list-qualifying-dates",
    short_help="Retrieves information on Qualifying Dates for a specific Custom Day",
)
@click.argument(
    "args",
    nargs=-1,
    metavar="customdayid=value customdayname=value calendarid=value calendarname=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def list_qualifying_dates(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.custom_days.list_qualifying_dates(**vars_dict)
    process_output(output, select, response)
