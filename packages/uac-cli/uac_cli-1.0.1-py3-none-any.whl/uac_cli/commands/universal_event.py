import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands related to universal events, including publishing and managing universal events"
)
def universal_event():
    pass


@universal_event.command("publish", short_help="Publish Universal Event")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value business_services=value ttl=value attributes=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def publish(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.universal_events.publish(**vars_dict)
    process_output(output, select, response)


@universal_event.command("pushg", short_help="Push Universal Event")
@click.argument("args", nargs=-1, metavar="payload=value", required=True)
@click.pass_obj
@output_option
@select_option
def pushg(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.universal_events.pushg(**vars_dict)
    process_output(output, select, response)


@universal_event.command("push", short_help="Push Universal Event")
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def push(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.universal_events.push(**vars_dict)
    process_output(output, select, response)
