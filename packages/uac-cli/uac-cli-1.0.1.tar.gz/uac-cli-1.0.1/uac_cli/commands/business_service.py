import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands to manage business services, enabling operations like listing, creating, and updating business services"
)
def business_service():
    pass


@business_service.command(
    "get", short_help="Retrieves information on a specific Business Service"
)
@click.argument(
    "args", nargs=-1, metavar="busserviceid=value busservicename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_business_service(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.business_services.get_business_service(**vars_dict)
    process_output(output, select, response)


@business_service.command(
    "update", short_help="Modifies the Business Service specified by the sysId"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_business_service(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.business_services.update_business_service(**vars_dict)
    process_output(output, select, response)


@business_service.command("create", short_help="Creates a Business Service")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value retain_sys_ids=value",
    required=True,
)
@click.pass_obj
@output_option
@input_option
@select_option
def create_business_service(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.business_services.create_business_service(**vars_dict)
    process_output(output, select, response)


@business_service.command("delete", short_help="Deletes a Business Service")
@click.argument(
    "args", nargs=-1, metavar="busserviceid=value busservicename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_business_service(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.business_services.delete_business_service(**vars_dict)
    process_output(output, select, response)


@business_service.command(
    "list", short_help="Retrieves information on all Business Services"
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_business_services(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.business_services.list_business_services(**vars_dict)
    process_output(output, select, response)
