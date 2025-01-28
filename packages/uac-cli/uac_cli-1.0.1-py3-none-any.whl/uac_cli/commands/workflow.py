import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Workflow management commands, including operations for managing workflow vertices and edges, as well as running workflow forecasts"
)
def workflow():
    pass


@workflow.command("get-edges", short_help="Gets an edge")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value sourceid=value targetid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_edges(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.get_edges(**vars_dict)
    process_output(output, select, response)


@workflow.command("update-edge", short_help="Updates an edge")
@click.argument(
    "args",
    nargs=-1,
    metavar="sys_id=value workflow_id=value condition=value straight_edge=value points=value source_id=value target_id=value",
    required=True,
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_edge(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.workflows.update_edge(**vars_dict)
    process_output(output, select, response)


@workflow.command("add-edge", short_help="Adds an edge")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value condition=value straight_edge=value points=value source_id=value target_id=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def add_edge(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.add_edge(**vars_dict)
    process_output(output, select, response)


@workflow.command("delete-edge", short_help="Deletes an edge")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value sourceid=value targetid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def delete_edge(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.delete_edge(**vars_dict)
    process_output(output, select, response)


@workflow.command("get-vertices", short_help="Gets a vertex")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value taskid=value taskname=value taskalias=value vertexid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_vertices(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.get_vertices(**vars_dict)
    process_output(output, select, response)


@workflow.command("update-vertex", short_help="Updates a vertex")
@click.argument(
    "args",
    nargs=-1,
    metavar="sys_id=value workflow_id=value task=value alias=value vertex_id=value vertex_x=value vertex_y=value",
    required=True,
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_vertex(uac: UniversalController, args, output=None, input=None, select=None):
    vars_dict = process_input(args, input)
    response = uac.workflows.update_vertex(**vars_dict)
    process_output(output, select, response)


@workflow.command("add-vertex", short_help="Add a Task to a Workflow")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value task=value alias=value vertex_id=value vertex_x=value vertex_y=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def add_vertex(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.add_vertex(**vars_dict)
    process_output(output, select, response)


@workflow.command("add-child-vertex", short_help="Adds a vertex and edge")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflow_name=value parent_task_name=name parent_vertex_id=[optional] task_name=new_task vertex_id=[optional] vertexX=None vertexY=None vertex_x_offset=100 vertex_y_offset=100",
)
@click.pass_obj
@output_option
@select_option
def add_child_vertex(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.add_child_vertex(**vars_dict)
    process_output(output, select, response)


@workflow.command("delete-vertice", short_help="Deletes a vertice")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value taskid=value taskname=value taskalias=value vertexid=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def delete_vertice(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.delete_vertices(**vars_dict)
    process_output(output, select, response)


@workflow.command("get-forecast", short_help="Gets the forecast for a workflow")
@click.argument(
    "args",
    nargs=-1,
    metavar="workflowid=value workflowname=value calendarid=value calendarname=value triggerid=value triggername=value date=value time=value timezone=value forecast_timezone=value exclude=value variable=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_forecast(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.get_forecast(**vars_dict)
    process_output(output, select, response)


@workflow.command(
    "auto-arrange-vertices", short_help="Auto arrange the vertex locations"
)
@click.argument("args", nargs=-1, metavar="workflow_name=value", required=True)
@click.pass_obj
@output_option
@select_option
def auto_arrange_vertices(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.workflows.auto_arrange_vertices(**vars_dict)
    process_output(output, select, response)
