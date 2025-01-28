import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands related to managing Agent Clusters, including creation, deletion, and listing"
)
def agent_cluster():
    pass


@agent_cluster.command(
    "get", short_help="Retrieves information on a specific Agent Cluster"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="agentclusterid=value agentclustername=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def get_agent_cluster(uac: UniversalController, args, output=None, select=None):
    """
    Gets details of anAgent Cluster.

    Args:
        agent_cluster_id: agentclusterid
        agent_cluster_name: agentclustername
    """
    vars_dict = process_input(args)
    response = uac.agent_clusters.get_agent_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command(
    "update", short_help="Modifies the Agent Cluster specified by the sysId"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value opswise_groups=value strict_bsrvc_membership=value distribution=value network_alias=value network_alias_port=value resolution_status=value resolution_description=value last_resolution=value limit_type=value limit_amount=value current_count=value suspended=value suspended_on=value resumed_on=value agent_limit_type=value agent_limit_amount=value last_agent_used=value ignore_inactive_agents=value ignore_suspended_agents=value retain_sys_ids=value agents=value notifications=value type=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_agent_cluster(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.agent_clusters.update_agent_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command("create", short_help="Creates a new Agent Cluster")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_agent_cluster(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.agent_clusters.create_agent_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command("delete", short_help="Deletes a specific Agent Cluster")
@click.argument(
    "args",
    nargs=-1,
    metavar="agentclusterid=value agentclustername=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def delete_agent_cluster(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.delete_agent_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command("list", short_help="Retrieves information on all Agent Clusters")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_agent_clusters(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.list_agent_clusters(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command(
    "list-advanced",
    short_help="Retrieves Agent Cluster details using specific query parameters",
)
@click.argument(
    "args",
    nargs=-1,
    metavar="agentclustername=value type=value business_services=value",
)
@click.pass_obj
@output_option
@select_option
def list_agent_clusters_advanced(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.agent_clusters.list_agent_clusters_advanced(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command(
    "get-selected-agent",
    short_help="Retrieves information on a specific Agent from an Agent Cluster for which a Distribution method of Any or Lowest CPU Utilization is specified",
)
@click.argument(
    "args", nargs=-1, metavar="agentclustername=value ignoreexecutionlimit=value"
)
@click.pass_obj
@output_option
@select_option
def get_selected_agent(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.get_selected_agent(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command(
    "resolve-cluster",
    short_help="Resolves the Network Alias for the specified Agent Cluster",
)
@click.argument("args", nargs=-1, metavar="agent_cluster_name=value", required=True)
@click.pass_obj
@output_option
@select_option
def resolve_cluster(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.resolve_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command("resume", short_help="Resumes the specified Agent Cluster")
@click.argument("args", nargs=-1, metavar="agent_cluster_name=value", required=True)
@click.pass_obj
@output_option
@select_option
def resume_cluster(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.resume_cluster(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command(
    "set-task-execution-limit",
    short_help="Sets the task execution limit for the specified Agent Cluster",
)
@click.argument(
    "args",
    nargs=-1,
    metavar="agent_cluster_name=value limit_type=value limit_amount=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def set_cluster_task_execution_limit(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.agent_clusters.set_cluster_task_execution_limit(**vars_dict)
    process_output(output, select, response)


@agent_cluster.command("suspend", short_help="Suspends the specified Agent Cluster")
@click.argument("args", nargs=-1, metavar="agent_cluster_name=value", required=True)
@click.pass_obj
@output_option
@select_option
def suspend_cluster(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.agent_clusters.suspend_cluster(**vars_dict)
    process_output(output, select, response)
