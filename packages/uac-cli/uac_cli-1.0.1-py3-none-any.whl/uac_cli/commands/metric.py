import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands to scrape and retrieve metrics from the Universal Controller as Prometheus text"
)
def metrics():
    pass


@metrics.command(
    "get", short_help="Scrapes the Universal Controller metrics as Prometheus text"
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
def get_metrics(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.metrics.get_metrics(**vars_dict)
    process_output(output, select, response, text=True)
