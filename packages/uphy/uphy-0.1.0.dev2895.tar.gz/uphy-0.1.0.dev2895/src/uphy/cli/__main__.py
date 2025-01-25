import typer
import logging
from importlib.metadata import entry_points
from importlib import import_module

app = typer.Typer(pretty_exceptions_enable=False, no_args_is_help=True, name="uphy", help="U-Phy command line tools")
LOG = logging.getLogger(__name__)

for entry_point in entry_points(group='uphy.cli'):
    try:
        module_name, _, attribute = entry_point.value.partition(":")
        module = import_module(module_name)
        command = getattr(module, attribute)
        app.add_typer(command, name=entry_point.name)
    except Exception as exception:
        LOG.warning("Ignoring entry point '%s' due to error: %r", entry_point.name, exception)

@app.command()
def build():
    """Start device builder to generate configuration files."""
    typer.launch("https://devicebuilder.rt-labs.com/")

@app.command(name="help")
def help(ctx: typer.Context):
    typer.echo(ctx.get_help())

if __name__ == "__main__":
    app()
