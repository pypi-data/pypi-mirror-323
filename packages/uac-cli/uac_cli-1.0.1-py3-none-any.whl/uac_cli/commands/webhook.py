import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Webhook management commands, including creating, updating, enabling, and disabling webhooks"
)
def webhook():
    pass


@webhook.command(
    "unassign-execution-user", short_help="Unassign an Execution User from a Webhook"
)
@click.argument(
    "args", nargs=-1, metavar="webhookid=value webhookname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def unassign_execution_user(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.unassign_execution_user(**vars_dict)
    process_output(output, select, response)


@webhook.command("get", short_help="Read a Webhook")
@click.argument(
    "args", nargs=-1, metavar="webhookid=value webhookname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_webhook(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.get_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("update", short_help="Modify a Webhook")
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value description=value retain_sys_ids=value opswise_groups=value event=value action=value task=value url=value filter=value enabled_by=value enabled_time=value disabled_by=value disabled_time=value execution_user=value status=value status_description=value url_parameters=value http_headers=value http_auth=value credentials=value url_parameters_from_string=value http_headers_from_string=value event_business_service_criteria=value event_business_services=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_webhook(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.webhooks.update_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("create", short_help="Register a Webhook")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_webhook(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.webhooks.create_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("delete", short_help="Unregister a Webhook")
@click.argument(
    "args", nargs=-1, metavar="webhookid=value webhookname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_webhook(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.delete_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("disable", short_help="Disable a Webhook")
@click.argument(
    "args", nargs=-1, metavar="webhookid=value webhookname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def disable_webhook(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.disable_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("enable", short_help="Enable a Webhook")
@click.argument(
    "args", nargs=-1, metavar="webhookid=value webhookname=value", required=True
)
@click.pass_obj
@output_option
@select_option
def enable_webhook(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.enable_webhook(**vars_dict)
    process_output(output, select, response)


@webhook.command("list", short_help="List Webhooks")
@click.argument(
    "args",
    nargs=-1,
    metavar="webhookname=value action=value business_services=value description=value event=value task=value taskname=value url=value",
)
@click.pass_obj
@output_option
@select_option
def list_webhooks(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.webhooks.list_webhooks(**vars_dict)
    process_output(output, select, response)
