import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing simulations, including creating, updating, and deleting simulations"
)
def simulation():
    pass


@simulation.command("get", short_help="Read a Simulation")
@click.argument(
    "args",
    nargs=-1,
    metavar="simulationid=value taskname=value workflowname=value vertexid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_simulation(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.simulations.get_simulation(**vars_dict)
    process_output(output, select, response)


@simulation.command("update", short_help="Modify a Simulation")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value retain_sys_ids=value task=value workflow=value vertex_id=value status=value exit_code=value publish_status=value publish_late_start=value publish_late_finish=value publish_early_finish=value abort_actions=value email_notification_actions=value variable_actions=value snmp_notification_actions=value system_operation_actions=value other_options=value outputs=value variables_from_string=value variables=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_simulation(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.simulations.update_simulation(**vars_dict)
    process_output(output, select, response)


@simulation.command("create", short_help="Create a Simulation")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_simulation(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.simulations.create_simulation(**vars_dict)
    process_output(output, select, response)


@simulation.command("delete", short_help="Delete a Simulation")
@click.argument(
    "args",
    nargs=-1,
    metavar="simulationid=value taskname=value workflowname=value vertexid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def delete_simulation(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.simulations.delete_simulation(**vars_dict)
    process_output(output, select, response)


@simulation.command("list-simulations", short_help="List Simulations")
@click.argument("args", nargs=-1, metavar="taskname=value workflowname=value")
@click.pass_obj
@output_option
@select_option
def list_simulations(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.simulations.list_simulations(**vars_dict)
    process_output(output, select, response)
