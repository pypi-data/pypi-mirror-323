import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands to manage Email templates, including operations for creation, deletion, and updating templates"
)
def email_template():
    pass


@email_template.command(
    "get", short_help="Retrieves information on a specific Email Template"
)
@click.argument(
    "args", nargs=-1, metavar="templateid=value templatename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_email_template(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.email_templates.get_email_template(**vars_dict)
    process_output(output, select, response)


@email_template.command(
    "update", short_help="Modifies the Email Template specified by the sysId"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value template_name=value description=value opswise_groups=value connection=value reply_to=value to=value cc=value bcc=value subject=value body=value retain_sys_ids=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_email_template(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.email_templates.update_email_template(**vars_dict)
    process_output(output, select, response)


@email_template.command("create", short_help="Creates an Email Template")
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_email_template(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.email_templates.create_email_template(**vars_dict)
    process_output(output, select, response)


@email_template.command("delete", short_help="Deletes the specified Email Template")
@click.argument(
    "args", nargs=-1, metavar="templateid=value templatename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_email_template(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.email_templates.delete_email_template(**vars_dict)
    process_output(output, select, response)


@email_template.command(
    "list", short_help="Retrieves information on all Email Templates."
)
@click.argument("args", nargs=-1, metavar="")
@click.pass_obj
@output_option
@select_option
def list_email_template(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.email_templates.list_email_template(**vars_dict)
    process_output(output, select, response)
