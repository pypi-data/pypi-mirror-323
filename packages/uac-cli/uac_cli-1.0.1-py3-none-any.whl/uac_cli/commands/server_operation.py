import click
from uac_api import UniversalController

from uac_cli.utils.options import (
    input_option,
    output_option,
    output_option_binary,
    select_option,
)
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for server operations, such as log rolling and temporary Property changes"
)
def server_operation():
    pass


@server_operation.command("roll-log", short_help="Roll Log")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def roll_log(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.roll_log(**vars_dict)
    process_output(output, select, response)


@server_operation.command(
    "temporary-property-change", short_help="Temporary Property Change"
)
@click.argument("args", nargs=-1, metavar="name=value value=value", required=True)
@click.pass_obj
@output_option
@select_option
def temporary_property_change(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.temporary_property_change(**vars_dict)
    process_output(output, select, response)


@server_operation.command("bulk-export", short_help="Bulk Export")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def bulk_export(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.bulk_export(**vars_dict)
    process_output(output, select, response)


@server_operation.command(
    "bulk-export-with-versions", short_help="Bulk Export with Versions"
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def bulk_export_with_versions(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.bulk_export_with_versions(**vars_dict)
    process_output(output, select, response)


@server_operation.command("bulk-import", short_help="Bulk Import")
@click.argument("args", nargs=-1, metavar="path=[path of bulk import files]")
@click.pass_obj
@output_option
@select_option
def bulk_import(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.bulk_import(**vars_dict)
    process_output(output, select, response)


@server_operation.command("list-log", short_help="List Log Files")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_log(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.list_log(**vars_dict)
    process_output(output, select, response)


@server_operation.command("download-log", short_help="Download Log Files")
@click.argument("args", nargs=-1, metavar="name=log_name")
@click.pass_obj
@output_option_binary
def download_log(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.server_operations.download_log(**vars_dict)
    process_output(output, select, response, text=False, binary=True)
