import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Property management commands, allowing users to list, create, update, and delete Properties"
)
def property():
    pass


@property.command("get", short_help="Retrieves information on a specific Property")
@click.argument("args", nargs=-1, metavar="propertyname=value", required=True)
@click.pass_obj
@output_option
@select_option
def get_property(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.properties.get_property(**vars_dict)
    process_output(output, select, response)


@property.command("update", short_help="Modifies the specified Property")
@click.argument("args", nargs=-1, metavar="propertyname=name value=value")
@click.pass_obj
@output_option
@input_option
@select_option
def update_property(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.properties.update_property(**vars_dict)
    process_output(output, select, response)


@property.command("list", short_help="Retrieves information on all Properties")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_properties(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.properties.list_properties(**vars_dict)
    process_output(output, select, response)
