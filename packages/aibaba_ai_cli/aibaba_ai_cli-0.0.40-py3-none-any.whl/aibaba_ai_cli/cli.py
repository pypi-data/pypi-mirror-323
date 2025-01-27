from typing import Optional

import typer
from typing_extensions import Annotated

from aibaba_ai_cli._version import __version__
from aibaba_ai_cli.namespaces import app as app_namespace
from aibaba_ai_cli.namespaces import integration as integration_namespace
from aibaba_ai_cli.namespaces import template as template_namespace
from aibaba_ai_cli.namespaces.migrate import main as migrate_namespace
from aibaba_ai_cli.utils.packages import get_aibaba_ai_export, get_package_root
from aibaba_ai_cli.utils.docker import build_docker_image

app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(
    template_namespace.package_cli, name="template", help=template_namespace.__doc__
)
app.add_typer(app_namespace.app_cli, name="app", help=app_namespace.__doc__)
app.add_typer(
    integration_namespace.integration_cli,
    name="integration",
    help=integration_namespace.__doc__,
)

app.command(
    name="migrate",
    context_settings={
        # Let Grit handle the arguments
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)(
    migrate_namespace.migrate,
)


def version_callback(show_version: bool) -> None:
    if show_version:
        typer.echo(f"aibaba_ai_cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Print the current CLI version.",
        callback=version_callback,
        is_eager=True,
    ),
):
    pass


@app.command()
def serve(
    *,
    port: Annotated[
        Optional[int], typer.Option(help="The port to run the server on")
    ] = None,
    host: Annotated[
        Optional[str], typer.Option(help="The host to run the server on")
    ] = None,
) -> None:
    """
    Start the Aibaba AI app, whether it's a template or an app.
    """

    # see if is a template
    try:
        project_dir = get_package_root()
        pyproject = project_dir / "pyproject.toml"
        get_aibaba_ai_export(pyproject)
    except KeyError:
        # not a template
        app_namespace.serve(port=port, host=host)
    else:
        # is a template
        template_namespace.serve(port=port, host=host)


@app.command()
def image(
    *,
    tag: Annotated[
        Optional[str], 
        typer.Option(help="The tag for the Docker image. Defaults to 'latest'")
    ] = "latest",
    port: Annotated[
        Optional[int], 
        typer.Option(help="The port to expose the REST API on. Defaults to 8000")
    ] = 8000,
) -> None:
    """
    Build a Docker image for the Python application with REST API exposed.
    """
    project_dir = get_package_root()
    build_docker_image(project_dir, tag=tag, port=port)


if __name__ == "__main__":
    app()
