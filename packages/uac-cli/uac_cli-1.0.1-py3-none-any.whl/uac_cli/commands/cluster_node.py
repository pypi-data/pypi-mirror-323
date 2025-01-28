import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing cluster nodes, including retrieving information about the current node"
)
def cluster_node():
    pass


@cluster_node.command(
    "get", short_help="Retrieves information on the current Cluster Node"
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def get_cluster_node(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.cluster_nodes.get_cluster_node(**vars_dict)
    process_output(output, select, response)


@cluster_node.command("list", short_help="Retrieves information on all Cluster Nodes")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_cluster_nodes(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.cluster_nodes.list_cluster_nodes(**vars_dict)
    process_output(output, select, response)
