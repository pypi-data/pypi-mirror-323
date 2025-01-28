import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="User management commands, including operations for creating, updating, and deleting users, as well as managing authentication tokens"
)
def user():
    pass


@user.command(
    "change-password", short_help="Change a Universal Controller User Password"
)
@click.argument(
    "args", nargs=-1, metavar="name=value new_password=value", required=True
)
@click.pass_obj
@output_option
@select_option
def change_user_password(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.change_user_password(**vars_dict)
    process_output(output, select, response)


@user.command("get", short_help="Read a User")
@click.argument(
    "args",
    nargs=-1,
    metavar="userid=value username=value show_tokens=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_user(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.get_user(**vars_dict)
    process_output(output, select, response)


@user.command("update", short_help="Modify a User")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value retain_sys_ids=value user_name=value user_password=value first_name=value middle_name=value last_name=value email=value title=value active=value locked_out=value password_needs_reset=value business_phone=value mobile_phone=value time_zone=value department=value manager=value browser_access=value command_line_access=value web_service_access=value login_method=value impersonate=value permissions=value user_roles=value tokens=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_user(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.users.update_user(**vars_dict)
    process_output(output, select, response)


@user.command("create", short_help="Create a User")
@click.argument("args", nargs=-1, metavar='user_name="newuser" user_password="abc123"')
@click.pass_obj
@output_option
@input_option
@select_option
def create_user(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    uac.log.debug(vars_dict)
    uac.log.debug(args)
    vars_dict["payload"]["userPassword"] = vars_dict.get(
        "userPassword", vars_dict.get("user_password")
    )
    response = uac.users.create_user(**vars_dict)
    process_output(output, select, response)


@user.command("delete", short_help="Delete a User")
@click.argument("args", nargs=-1, metavar="userid=value username=value", required=True)
@click.pass_obj
@output_option
@select_option
def delete_user(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.delete_user(**vars_dict)
    process_output(output, select, response)


@user.command("create-token", short_help="Create Personal Access Token")
@click.argument(
    "args",
    nargs=-1,
    metavar="retain_sys_ids=value user_id=uuid user_name=userName name=token_name expiration=yyyy-mm-dd",
)
@click.pass_obj
@output_option
@input_option
@select_option
def create_user_token(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.users.create_user_token(**vars_dict)
    process_output(output, select, response)


@user.command("revoke-token", short_help="Revoke Personal Access Token")
@click.argument(
    "args",
    nargs=-1,
    metavar="userid=value username=value tokenname=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def revoke_user_token(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.revoke_user_token(**vars_dict)
    process_output(output, select, response)


@user.command("list-auth-tokens", short_help="List Personal Access Tokens")
@click.argument("args", nargs=-1, metavar="userid=value username=value")
@click.pass_obj
@output_option
@select_option
def list_auth_tokens(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.list_auth_tokens(**vars_dict)
    process_output(output, select, response)


@user.command("list", short_help="List Users")
@click.argument("args", nargs=-1, metavar="show_tokens=value")
@click.pass_obj
@output_option
@select_option
def list_users(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.users.list_users(**vars_dict)
    process_output(output, select, response)
