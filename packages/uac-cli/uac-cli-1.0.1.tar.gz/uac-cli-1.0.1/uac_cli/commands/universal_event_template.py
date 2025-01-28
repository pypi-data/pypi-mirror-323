import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing universal event templates, including creating, updating, and deleting templates"
)
def universal_event_template():
    pass


@universal_event_template.command("get", short_help="Read a Universal Event Template")
@click.argument(
    "args", nargs=-1, metavar="templateid=value templatename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def get_universal_event_template(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.universal_event_templates.get_universal_event_template(**vars_dict)
    process_output(output, select, response)


@universal_event_template.command(
    "update", short_help="Modify a Universal Event Template"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="version=value sys_id=value exclude_related=value export_release_level=value export_table=value name=value label=value description=value ttl=value attributes_policy=value attributes=value metric_type=value metric_name=value metric_value_attribute=value metric_unit=value metric_label_attributes=value metric_optional_labels=value retain_sys_ids=value attributes_from_string=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_universal_event_template(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.universal_event_templates.update_universal_event_template(
        **vars_dict
    )
    process_output(output, select, response)


@universal_event_template.command(
    "create", short_help="Create a Universal Event Template"
)
@click.argument("args", nargs=-1, metavar="retain_sys_ids=value")
@click.pass_obj
@output_option
@input_option
@select_option
def create_universal_event_template(
    uac: UniversalController,
    args,
    output=None,
    input=None,
    select=None,
):
    vars_dict = process_input(args, input)
    response = uac.universal_event_templates.create_universal_event_template(
        **vars_dict
    )
    process_output(output, select, response)


@universal_event_template.command(
    "delete", short_help="Delete a Universal Event Template"
)
@click.argument(
    "args", nargs=-1, metavar="templateid=value templatename=value", required=True
)
@click.pass_obj
@output_option
@select_option
def delete_universal_event_template(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.universal_event_templates.delete_universal_event_template(
        **vars_dict
    )
    process_output(output, select, response)


@universal_event_template.command("list", short_help="List Universal Event Templates")
@click.argument("args", nargs=-1, metavar="templatename=value")
@click.pass_obj
@output_option
@select_option
def list_universal_event_templates(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.universal_event_templates.list_universal_event_templates(**vars_dict)
    process_output(output, select, response)
