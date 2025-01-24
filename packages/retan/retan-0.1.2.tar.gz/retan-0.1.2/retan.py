import click

from utils.config import Config, config as config_group
from bot.cyborg import cyborg

@click.group()
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    """Main CLI group."""
    # Initialize ctx.obj as a dictionary if not already set
    if ctx.obj is None:
        ctx.obj = {}
    local_config = Config.load()
    ctx.obj["config"] = local_config


# Register the `config` commands
cli.add_command(config_group)
cli.add_command(cyborg)

if __name__ == "__main__":
    cli()
