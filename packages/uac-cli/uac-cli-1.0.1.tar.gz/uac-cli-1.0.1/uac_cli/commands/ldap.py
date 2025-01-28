import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(short_help="LDAP configuration commands, including updating LDAP settings")
def ldap():
    pass


@ldap.command("get", short_help="Retrieves LDAP Settings")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def get_ldap(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.ldap.get_ldap(**vars_dict)
    process_output(output, select, response)


@ldap.command("update", short_help="Modifies LDAP Settings")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value url=value bind_dn=value bind_password=value use_for_authentication=value allow_local_login=value base_dn=value user_id_attribute=value user_filter=value group_filter=value connect_timeout=value read_timeout=value user_membership_attribute=value group_member_attribute=value login_method=value user_target_ou_list=value group_target_ou_list=value mappings=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_ldap(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.ldap.update_ldap(**vars_dict)
    process_output(output, select, response)
