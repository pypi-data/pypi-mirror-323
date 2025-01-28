import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="User Group management commands, including listing, creating, updating, and deleting user groups"
)
def user_group():
    pass


@user_group.command("get", short_help="Read a User Group")
@click.argument(
    "args", nargs=-1, metavar="groupid=value groupname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_user_group(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.user_groups.get_user_group(**vars_dict)
    process_output(output, select, response)


@user_group.command("update", short_help="Modify a User Group")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value retain_sys_ids=value name=value email=value manager=value description=value parent=value ctrl_navigation_visibility=value navigation_visibility=value permissions=value group_roles=value group_members=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_user_group(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.user_groups.update_user_group(**vars_dict)
    process_output(output, select, response)


@user_group.command("create", short_help="Create a User Group")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_user_group(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.user_groups.create_user_group(**vars_dict)
    process_output(output, select, response)


@user_group.command("delete", short_help="Delete a User Group")
@click.argument(
    "args", nargs=-1, metavar="groupid=value groupname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_user_group(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.user_groups.delete_user_group(**vars_dict)
    process_output(output, select, response)


@user_group.command("list", short_help="List User Groups")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_user_groups(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.user_groups.list_user_groups(**vars_dict)
    process_output(output, select, response)
