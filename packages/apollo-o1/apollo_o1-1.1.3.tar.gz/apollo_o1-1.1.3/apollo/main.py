import click
import os
import getpass
from dotenv import load_dotenv

from apollo.commands.gh_create import gh_create  # Import subcommands
from apollo.commands.gh_add import gh_add
from apollo.commands.gh_delete import gh_delete
from apollo.commands.build import build
from apollo.commands.deploy import deploy
from apollo.commands.linear import linear
from apollo.commands.clean_up import clean_up

# Load the environment variables
env_file = ".env.dev" if os.getenv("ENV") == "dev" else ".env.prod"
load_dotenv(env_file)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help=f"""
        Apollo CLI - An AI-powered CLI for DevOps and project management workflows.

        Specify configs in the config.json file:\n
            /Users/{getpass.getuser()}/.config/apollo

        More configuration info: apollo --help config
    """,
    epilog="\nRun 'apollo <command> --help, -h' for more details on a specific command.\n",
)
def apollo():
    """"""


pass

# Access APOLLO_DEV_MODE
if os.getenv("APOLLO_DEV_MODE") == "1":
    print("Developer mode enabled.")

    apollo.command("build")(build)
    apollo.command("deploy")(deploy)
    apollo.command("clean-up")(clean_up)


# Add subcommands to the CLI
apollo.command("gh-create")(gh_create)
apollo.command("gh-add")(gh_add)
apollo.command("gh-delete")(gh_delete)
apollo.command("linear")(linear)

# Add future commands here
# apollo.command("data-utils")(data_utils)
# apollo.command("schedule-task")(schedule_task)

if __name__ == "__main__":
    apollo()
