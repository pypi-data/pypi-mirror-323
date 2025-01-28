import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Parent group for Connection-related commands, serving as a namespace for database, email, and other Connection types"
)
def connection():
    pass


@connection.group(
    short_help="Commands related to Database Connections, including listing, creating, and updating Database Connection details"
)
def database():
    pass


@connection.group(
    short_help="Commands for managing Email Connections, allowing users to create, update, and delete Email Connection configurations"
)
def email():
    pass


@connection.group(
    short_help="Commands for managing PeopleSoft connections, including operations to create, update, and delete PeopleSoft Connection details"
)
def peoplesoft():
    pass


@connection.group(
    short_help="Commands related to SAP connections, including operations for managing SAP Connection configurations"
)
def sap():
    pass


@database.command("get", short_help="Read a Database Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_database_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.get_database_connection(**vars_dict)
    process_output(output, select, response)


@database.command("update", short_help="Modify a Database Connection")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value db_type=value db_url=value db_driver=value db_max_rows=value db_description=value credentials=value retain_sys_ids=value opswise_groups=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_database_connection(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.connections.update_database_connection(**vars_dict)
    process_output(output, select, response)


@database.command("create", short_help="Create a Database Connection")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_database_connection(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.connections.create_database_connection(**vars_dict)
    process_output(output, select, response)


@database.command("delete", short_help="Delete a Database Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_database_connection(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.connections.delete_database_connection(**vars_dict)
    process_output(output, select, response)


@database.command(
    "list", short_help="Retrieves information on all Database Connections"
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_database_connections(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.list_database_connections(**vars_dict)
    process_output(output, select, response)


@email.command("get", short_help="Read an Email Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_email_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.get_email_connection(**vars_dict)
    process_output(output, select, response)


@email.command("update", short_help="Modify an Email Connection")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value smtp=value smtp_port=value smtp_ssl=value smtp_starttls=value email_addr=value default_user=value default_pwd=value authentication=value authentication_type=value oauth_client=value system_connection=value type=value imap=value imap_port=value imap_ssl=value imap_starttls=value trash_folder=value opswise_groups=value description=value authorized=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_email_connection(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.connections.update_email_connection(**vars_dict)
    process_output(output, select, response)


@email.command("create", short_help="Create an Email Connection")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_email_connection(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.connections.create_email_connection(**vars_dict)
    process_output(output, select, response)


@email.command("delete", short_help="Delete a Email Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_email_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.delete_email_connection(**vars_dict)
    process_output(output, select, response)


@email.command("list", short_help="Retrieves information on all Email Connections")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_email_connections(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.list_email_connections(**vars_dict)
    process_output(output, select, response)


@peoplesoft.command("get", short_help="Read a PeopleSoft Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_peoplesoft_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.get_peoplesoft_connection(**vars_dict)
    process_output(output, select, response)


@peoplesoft.command("update", short_help="Modify a PeopleSoft Connection")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value server=value port=value endpoint=value credentials=value retain_sys_ids=value opswise_groups=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_peoplesoft_connection(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.connections.update_peoplesoft_connection(**vars_dict)
    process_output(output, select, response)


@peoplesoft.command("create", short_help="Create a PeopleSoft Connection")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_peoplesoft_connection(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.connections.create_peoplesoft_connection(**vars_dict)
    process_output(output, select, response)


@peoplesoft.command("delete", short_help="Delete a PeopleSoft Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_peoplesoft_connection(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.connections.delete_peoplesoft_connection(**vars_dict)
    process_output(output, select, response)


@peoplesoft.command("list", short_help="List PeopleSoft Connections")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_peoplesoft_connections(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.connections.list_peoplesoft_connections(**vars_dict)
    process_output(output, select, response)


@sap.command("get", short_help="Read an SAP Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_sap_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.get_sap_connection(**vars_dict)
    process_output(output, select, response)


@sap.command("update", short_help="Modify an SAP Connection")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value sap_connection_type=value sap_ashost=value sap_client=value sap_sysnr=value sap_gwhost=value sap_gwserv=value sap_r3name=value sap_mshost=value sap_group=value opswise_groups=value description=value sap_saprouter=value sap_snc_mode=value sap_snc_lib=value sap_snc_myname=value sap_snc_partnername=value sap_snc_qop=value sap_snc_sso=value sap_mysapsso2=value sap_x509cert=value sap_use_symbolic_names=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_sap_connection(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.connections.update_sap_connection(**vars_dict)
    process_output(output, select, response)


@sap.command("create", short_help="Create an SAP Connection")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_sap_connection(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.connections.create_sap_connection(**vars_dict)
    process_output(output, select, response)


@sap.command("delete", short_help="Delete an SAP Connection")
@click.argument(
    "args", nargs=-1, metavar="connectionid=value connectionname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_sap_connection(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.delete_sap_connection(**vars_dict)
    process_output(output, select, response)


@sap.command("list", short_help="Retrieves information on all SAP Connections")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_sap_connections(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.connections.list_sap_connections(**vars_dict)
    process_output(output, select, response)
