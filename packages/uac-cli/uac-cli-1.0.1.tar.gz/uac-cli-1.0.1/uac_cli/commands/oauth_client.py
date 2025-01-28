import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing OAuth clients, including creating, updating, and listing OAuth clients"
)
def oauth_client():
    pass


@oauth_client.command("get", short_help="Read an OAuth Client")
@click.argument(
    "args", nargs=-1, metavar="oauthclientid=value oauthclientname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_o_auth_client(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.oauth_clients.get_oauth_client(**vars_dict)
    process_output(output, select, response)


@oauth_client.command("update", short_help="Modify an OAuth Client")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value opswise_groups=value provider=value cluster_redirect_urls=value authorization_endpoint=value token_endpoint=value tenant_id=value client_id=value client_secret=value scopes=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_o_auth_client(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.oauth_clients.update_oauth_client(**vars_dict)
    process_output(output, select, response)


@oauth_client.command("create", short_help="Creates an OAuth Client")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_o_auth_client(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.oauth_clients.create_oauth_client(**vars_dict)
    process_output(output, select, response)


@oauth_client.command("delete", short_help="Delete an OAuth Client")
@click.argument(
    "args", nargs=-1, metavar="oauthclientid=value oauthclientname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_o_auth_client(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.oauth_clients.delete_oauth_client(**vars_dict)
    process_output(output, select, response)


@oauth_client.command("list", short_help="List OAuth Clients")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_o_auth_clients(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.oauth_clients.list_oauth_clients(**vars_dict)
    process_output(output, select, response)
