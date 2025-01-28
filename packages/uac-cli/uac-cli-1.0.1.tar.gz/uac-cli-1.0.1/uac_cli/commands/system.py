import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="System-related commands, including retrieving system status and information"
)
@click.pass_obj
def system(uac):
    if uac is None:
        click.echo(
            click.style("No profiles found. run `uac config init`", fg="bright_red"),
            err=True,
        )
        exit(1)


@system.command("get", short_help="Retrieve System Details")
@click.pass_obj
@output_option
@select_option
def get_status(uac: UniversalController, output=None, select=None):
    response = uac.system.get_status()
    process_output(output, select, response)
