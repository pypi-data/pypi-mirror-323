import click
from uac_api import UniversalController

from uac_cli.utils.options import (
    input_option,
    output_option,
    output_option_binary,
    select_option,
)
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands to run and manage reports, including running reports in various formats"
)
def report():
    pass


@report.command(
    "run-report",
    short_help="Runs a Report. Chart Reports are generated in png format (image/png). Use the Accept HTTP Header to specify format of List Reports. List Report default is pdf format (application/pdf)",
)
@click.argument(
    "args",
    nargs=-1,
    metavar="reporttitle=value visibility=value groupname=value format=",
)
@click.pass_obj
@output_option_binary
@select_option
@click.option(
    "--format", type=click.Choice(["csv", "tab", "pdf", "png", "xml", "json"])
)
def run_report(uac: UniversalController, args, output=None, select=None, format="csv"):
    vars_dict = process_input(args)
    response = uac.reports.run_report(report_format=format, **vars_dict)
    process_output(
        output, select, response, text=True, binary=(format in ["pdf", "png"])
    )
