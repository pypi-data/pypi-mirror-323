import click
from uac_api import UniversalController

from uac_cli.utils.options import input_option, output_option, select_option
from uac_cli.utils.process import create_payload, process_input, process_output


@click.group(
    short_help="Commands for managing task instances, including listing, updating, and controlling the execution of task instances"
)
def task_instance():
    pass


@task_instance.command("delete", short_help="Delete a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def delete_task_instance(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.delete_task_instance(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "show-variables", short_help="List Task Instance Variables (Show Variables)"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="taskinstancename=value taskinstanceid=value workflowinstancename=value criteria=value fetchglobal=value",
)
@click.pass_obj
@output_option
@select_option
def show_variables(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.show_variables(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "update-operational-memo", short_help="Update a Task Instance Operational Memo"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="memo=message taskinstancename=value taskinstanceid=value workflowinstancename=value criteria=value",
)
@click.pass_obj
@output_option
@input_option
@select_option
def update_operational_memo(
    uac: UniversalController, args, output=None, input=None, select=None
):
    vars_dict = process_input(args, input)
    response = uac.task_instances.update_operational_memo(**vars_dict)
    process_output(output, select, response)


@task_instance.command("set-priority", short_help="Set Priority for a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_set_priority(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.set_priority(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "set-complete", short_help="Issue Set Completed Command for a Manual Task Instance"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value operationalMemo=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_set_priority(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.set_complete(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "set-timewait", short_help="Set or Modify Wait Time/Duration for Task Instance"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def set_timewait(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.set_timewait(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "list-dependency-list",
    short_help="List Predecessors / Successors of a Task Instance in a Workflow",
)
@click.argument(
    "args",
    nargs=-1,
    metavar="taskinstancename=value taskinstanceid=value workflowinstancename=value criteria=value dependencytype=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def list_dependency_list(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.list_dependency_list(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "task-insert", short_help="Insert a Task into a Workflow with Dependencies"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="id=value name=value alias=value workflow_instance_id=value workflow_instance_name=value workflow_instance_criteria=value predecessors=value successors=value vertex_x=value vertex_y=value inherit_trigger_time=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_insert(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    if "predecessors" in vars_dict:
        vars_dict["predecessors"] = vars_dict["predecessors"].split(",")
    if "successors" in vars_dict:
        vars_dict["successors"] = vars_dict["successors"].split(",")
    response = uac.task_instances.task_insert(**vars_dict)
    process_output(output, select, response)


@task_instance.command("cancel", short_help="Cancel a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_cancel(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.cancel(**vars_dict)
    process_output(output, select, response)


@task_instance.command("clear-dependencies", short_help="Clear All Dependencies")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_dependencies(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_dependencies(**vars_dict)
    process_output(output, select, response)


@task_instance.command("clear-exclusive", short_help="Clear Exclusive Dependencies")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_exclusive(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_exclusive(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "clear-instance-wait", short_help="Clear Instance Wait Dependencies"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_instance_wait(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_instance_wait(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "clear-predecessors", short_help="Clear Predecessor Dependencies"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_predecessors(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_predecessors(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "clear-resources", short_help="Clear Virtual Resource Dependencies"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_resources(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_resources(**vars_dict)
    process_output(output, select, response)


@task_instance.command("clear-timewait", short_help="Clear Time Dependency")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_clear_timewait(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.clear_timewait(**vars_dict)
    process_output(output, select, response)


@task_instance.command("force-finish", short_help="Force Finish a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_force_finish(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.force_finish(**vars_dict)
    process_output(output, select, response)


@task_instance.command(
    "force-finish-cancel", short_help="Force Finish/Cancel a Task Instance"
)
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_force_finish_cancel(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.force_finish_cancel(**vars_dict)
    process_output(output, select, response)


@task_instance.command("hold", short_help="Hold a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_hold(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.hold(**vars_dict)
    process_output(output, select, response)


@task_instance.command("release", short_help="Release a Task Instance from Hold")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_release(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.release(**vars_dict)
    process_output(output, select, response)


@task_instance.command("rerun", short_help="Rerun a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
@click.option("--wait", "-w", is_flag=True)
@click.option("--timeout", "-t", type=int, default=300)
@click.option("--interval", "-i", type=int, default=10)
@click.option("--return_rc", "-r", is_flag=True)
def task_instance_rerun(
    uac: UniversalController,
    args,
    output=None,
    select=None,
    wait=False,
    timeout=300,
    interval=10,
    return_rc=False,
):
    vars_dict = process_input(args)
    response = uac.task_instances.rerun(**vars_dict)
    if wait:
        if "id" in vars_dict:
            response = uac.task_instances.wait_for_status(
                id=vars_dict["id"], timeout=timeout, interval=interval
            )
        else:
            click.echo(
                click.style(f"Wait option only works with id", fg="red"), err=True
            )
            exit(1)

    process_output(output, select, response)
    if wait and return_rc:
        if "exitCode" in response:
            exit(int(response["exitCode"]))
        else:
            if response.get("status", "UNKNOWN") in uac.task_instances.SUCCESS_STATUSES:
                exit(0)
            else:
                exit(1)


@task_instance.command("retrieve-output", short_help="Retrieve Task Instance Output")
@click.argument(
    "args",
    nargs=-1,
    metavar="taskinstancename=value taskinstanceid=value workflowinstancename=value criteria=value outputtype=value startline=value numlines=value scantext=value operational_memo=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_retrieve_output(
    uac: UniversalController, args, output=None, select=None
):
    vars_dict = process_input(args)
    response = uac.task_instances.retrieve_output(**vars_dict)
    process_output(output, select, response)


@task_instance.command("skip", short_help="Skip a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_skip(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.skip(**vars_dict)
    process_output(output, select, response)


@task_instance.command("skip-path", short_help="Skip a Task Instance Path")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_skip_path(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.skip_path(**vars_dict)
    process_output(output, select, response)


@task_instance.command("unskip", short_help="Unskip a Task Instance")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value",
    required=True,
)
@click.pass_obj
@output_option
@select_option
def task_instance_unskip(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.unskip(**vars_dict)
    process_output(output, select, response)


@task_instance.command("list", short_help="List Task Instances")
@click.argument(
    "args",
    nargs=-1,
    metavar="name=value id=value criteria=value workflow_instance_name=value resource_name=value recursive=value predecessor_name=value wait_type=value wait_time=value wait_duration=value wait_seconds=value wait_day_constraint=value delay_type=value delay_duration=value delay_seconds=value halt=value priority_type=value task_status=value operational_memo=value hold_reason=value agent_name=value workflow_instance_criteria=value workflow_instance_id=value status=value type=value execution_user=value late_start=value late_finish=value early_finish=value started_late=value finished_late=value finished_early=value late=value late_early=value business_services=value updated_time_type=value updated_time=value sys_id=value instance_number=value task_id=value task_name=value custom_field1=value custom_field2=value trigger_id=value trigger_name=value workflow_definition_id=value workflow_definition_name=value status_description=value template_id=value template_name=value response_fields=value instance_output_type=value",
)
@click.pass_obj
@output_option
@select_option
def list_status(uac: UniversalController, args, output=None, select=None):
    vars_dict = process_input(args)
    response = uac.task_instances.list_status(**vars_dict)
    process_output(output, select, response)
