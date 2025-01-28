import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands related to virtual resources, including listing, creating, updating, and deleting virtual resources"
)
def virtual_resource():
    pass


@virtual_resource.command("get", short_help="Read a Virtual Resource")
@click.argument(
    "args", nargs=-1, metavar="resourceid=value resourcename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_virtual_resource(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.virtual_resources.get_virtual_resource(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command("update", short_help="Modify a Virtual Resource")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value limit=value summary=value type=value opswise_groups=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_virtual_resource(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.virtual_resources.update_virtual_resource(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command("create", short_help="Create a Virtual Resource")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_virtual_resource(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.virtual_resources.create_virtual_resource(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command("delete", short_help="Delete a Virtual Resource")
@click.argument(
    "args", nargs=-1, metavar="resourceid=value resourcename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_virtual_resource(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.virtual_resources.delete_virtual_resource(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command("list", short_help="List Virtual Resources")
@click.argument("args", nargs=-1, metavar="name=value resourcename=value type=value")
@click.pass_obj
@output_option
@select_option
def list_virtual_resources(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.virtual_resources.list_virtual_resources(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command(
    "list-advanced", short_help="List Virtual Resources - Advanced"
)
@click.argument(
    "args", nargs=-1, metavar="resourcename=value type=value business_services=value"
)
@click.pass_obj
@output_option
@select_option
def list_virtual_resources_advanced(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.virtual_resources.list_virtual_resources_advanced(**vars_dict)
    process_output(output, select, response)


@virtual_resource.command("update-limit", short_help="Set Limit on a Virtual Resource")
@click.argument(
    "args",
    nargs=-1,
    metavar="sys_id=value name=value limit=value description=value type=value",
    required=True,
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_limit(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.virtual_resources.update_limit(**vars_dict)
    process_output(output, select, response)
