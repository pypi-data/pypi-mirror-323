import logging
import sys
import traceback

import click
import uac_api

from uac_cli import __version__
from uac_cli.commands.agent import agent
from uac_cli.commands.agent_cluster import agent_cluster
from uac_cli.commands.audit import audit
from uac_cli.commands.bundle import bundle, promotion, promotion_target
from uac_cli.commands.business_service import business_service
from uac_cli.commands.calendar import calendar
from uac_cli.commands.cluster_node import cluster_node
from uac_cli.commands.config import config
from uac_cli.commands.connection import connection
from uac_cli.commands.credential import credential
from uac_cli.commands.custom_day import custom_day
from uac_cli.commands.email_template import email_template
from uac_cli.commands.ldap import ldap
from uac_cli.commands.metric import metrics
from uac_cli.commands.oauth_client import oauth_client
from uac_cli.commands.oms_server import oms_server
from uac_cli.commands.property import property
from uac_cli.commands.report import report
from uac_cli.commands.script import script
from uac_cli.commands.server_operation import server_operation
from uac_cli.commands.simulation import simulation
from uac_cli.commands.system import system
from uac_cli.commands.task import task
from uac_cli.commands.task_instance import task_instance
from uac_cli.commands.trigger import trigger
from uac_cli.commands.universal_event import universal_event
from uac_cli.commands.universal_event_template import universal_event_template
from uac_cli.commands.universal_template import universal_template
from uac_cli.commands.user import user
from uac_cli.commands.user_group import user_group
from uac_cli.commands.variable import variable
from uac_cli.commands.virtual_resource import virtual_resource
from uac_cli.commands.webhook import webhook
from uac_cli.commands.workflow import workflow
from uac_cli.utils.config import read_profile

__output = None
__select = None


gl_debug_on = False


class CatchAllExceptions(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as any_exception:
            if gl_debug_on:
                click.echo("{}".format(any_exception), err=True)
                click.echo(traceback.format_exc(), err=True)
            sys.exit(1)


def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help(), err=True)
    ctx.exit(1)


class UacCli:
    def __init__(
        self,
        profile_name="default",
        log_level="ERROR",
        temp_profile=None,
        ssl_verify=True,
    ):
        self.log_level = log_level

        if "url" not in temp_profile or "token" not in temp_profile:
            from_profile = read_profile(profile_name)
            if from_profile:
                if "url" not in temp_profile:
                    if "url" in from_profile:
                        temp_profile["url"] = from_profile["url"]
                if "token" not in temp_profile:
                    if "token" in from_profile:
                        temp_profile["token"] = from_profile["token"]
        self.profile = temp_profile
        self.setup_logging()
        self.ssl_verify = ssl_verify
        if self.profile:
            self.log.debug(f'Profile URL: {self.profile.get("url")}')

    def setup_logging(self):
        if self.log_level != "DEBUG":
            sys.tracebacklimit = 0
        logging.basicConfig(level=self.log_level)
        logging.info(f"UAC CLI is running. (Version: {__version__})")
        self.log = logging

    def main(self):
        if not self.profile:
            return None

        if self.profile.get("token", None):
            self.uac = uac_api.UniversalController(
                base_url=self.profile["url"],
                token=self.profile["token"],
                logger=self.log,
                ssl_verify=self.ssl_verify,
            )
        else:
            return None
        self.log.info(f'UAC URL: {self.profile["url"]}')

        return self.uac


@click.group(cls=CatchAllExceptions)
@click.version_option(version=__version__)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="ERROR",
)
@click.option("--debug", "-d", is_flag=True, default=False, help="Enable debug mode")
@click.option(
    "--profile",
    "-p",
    help="Profile to use for the CLI. The profiles must be added to ~/.uac/profiles.yml EnvVar=UAC_CLI_PROFILE",
    default="default",
)
@click.option(
    "--url",
    type=str,
    help="The Base Universal Controller Endpoint of REST APIs. EnvVar=UAC_CLI_URL",
)
@click.option(
    "--token",
    type=str,
    help="The Universal Controller authentication token. EnvVar=UAC_CLI_TOKEN",
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    default=False,
    help="Skip SSL Verification. EnvVar=UAC_CLI_NO_VERIFY_SSL",
)
@click.option(
    "--argument-file",
    "-a",
    type=click.File("r"),
    help="Enter the arguments from a file. Each argument will be in a new line like key=value without quotes around the value",
)
@click.pass_context
def main(
    ctx,
    log_level,
    debug,
    profile,
    url,
    token,
    no_verify_ssl,
    argument_file,
):
    """
    UAC CLI


    This tool is a command line utility interfacing with Universal Controller REST API. Below you can see the list of commands. Each command will have sub-commands and you can see the details of the commands by adding --help to the end of the command.

    The create or update commands require an input file. You can also change the values in the input file from the command line. For example, you will create a new user and all the information will be the same as for another user. In this case you can first write the existing user's information to a json file with the `get` command and then run a command like the following.

    uac user create -input existing_user.json name="New Name"

    In this case it will overwrite the name field but will keep the other fields. For some special values you can use the following format.

    :none:, :true:, :false:, :[]:, :{}:, :1234567890:


    ====== Quick Start ======

    You can use the following environment variables.

    UAC_CLI_URL, UAC_CLI_TOKEN, UAC_CLI_PROFILE, UAC_CLI_NO_VERIFY_SSL

    To create a profile use the `uac config init` command. You can pass values as parameters of the command like --url, --token, OR you can use environment variables OR it will prompt you for the values.

    """
    if debug:
        global gl_debug_on
        gl_debug_on = debug
        log_level = "DEBUG"
    temp_profile = {}
    if url:
        temp_profile["url"] = url
    if token:
        temp_profile["token"] = token

    ssl_verify = not no_verify_ssl
    cli = UacCli(
        log_level=log_level,
        profile_name=profile,
        temp_profile=temp_profile,
        ssl_verify=ssl_verify,
    )
    ctx.obj = cli.main()
    if (
        ctx.obj is None
        and ctx.invoked_subcommand != "config"
        and "--help" not in sys.argv
    ):
        click.echo(
            "Incomplete Profile Information: No Credentials and/or Controller URL provided via profile or environment variables, or options. See help",
            err=True,
        )
        print_help()


main.add_command(config)
main.add_command(agent)
main.add_command(agent_cluster)
main.add_command(audit)
main.add_command(bundle)
main.add_command(business_service)
main.add_command(calendar)
main.add_command(cluster_node)
main.add_command(connection)
main.add_command(credential)
main.add_command(custom_day)
main.add_command(email_template)
main.add_command(ldap)
main.add_command(metrics)
main.add_command(oauth_client)
main.add_command(oms_server)
main.add_command(property)
main.add_command(report)
main.add_command(script)
main.add_command(server_operation)
main.add_command(simulation)
main.add_command(system)
main.add_command(task)
main.add_command(task_instance)
main.add_command(trigger)
main.add_command(universal_event)
main.add_command(universal_event_template)
main.add_command(universal_template)
main.add_command(user)
main.add_command(user_group)
main.add_command(variable)
main.add_command(virtual_resource)
main.add_command(webhook)
main.add_command(workflow)
main.add_command(promotion)
main.add_command(promotion_target)


def run():
    try:
        main(auto_envvar_prefix="UAC_CLI")
    except Exception as any_exception:
        click.echo("{}".format(any_exception), err=True)
        click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main(auto_envvar_prefix="UAC_CLI")
    except Exception as any_exception:
        click.echo("{}".format(any_exception), err=True)
        click.echo(traceback.format_exc(), err=True)
        sys.exit(1)
