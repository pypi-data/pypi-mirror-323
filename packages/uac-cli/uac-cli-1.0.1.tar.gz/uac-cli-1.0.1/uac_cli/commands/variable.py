import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing variables, including setting, updating, and listing variables"
)
def variable():
    pass


@variable.command("get", short_help="Read a Global Variable")
@click.argument(
    "args", nargs=-1, metavar="variableid=value variablename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_variable(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.variables.get_variable(**vars_dict)
    process_output(output, select, response)


@variable.command("update", short_help="Modify a Global Variable")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value value=value description=value opswise_groups=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_variable(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.variables.update_variable(**vars_dict)
    process_output(output, select, response)


@variable.command("create", short_help="Create a Global Variable")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_variable(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.variables.create_variable(**vars_dict)
    process_output(output, select, response)


@variable.command("delete", short_help="Delete a Global Variable")
@click.argument(
    "args", nargs=-1, metavar="variableid=value variablename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_variable(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.variables.delete_variable(**vars_dict)
    process_output(output, select, response)


@variable.command("list", short_help="List Variables")
@click.argument(
    "args",
    nargs=-1,
    metavar="variable_name=value scope=value task_name=value trigger_name=value",
)
@click.pass_obj
@output_option
@select_option
def list_variables(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.variables.list_variables(**vars_dict)
    process_output(output, select, response)


@variable.command("list-advanced", short_help="List Variables - Advanced")
@click.argument(
    "args",
    nargs=-1,
    metavar="scope=value variablename=value taskname=value triggername=value business_services=value",
)
@click.pass_obj
@output_option
@select_option
def list_variables_advanced(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.variables.list_variables_advanced(**vars_dict)
    process_output(output, select, response)


@variable.command("set", short_help="Set Variable")
@click.argument(
    "args",
    nargs=-1,
    metavar="scope=value create=value trigger=value task=value variable=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def variable_set(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.variables.variable_set(**vars_dict)
    process_output(output, select, response)
