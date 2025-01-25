from pathlib import Path
from time import sleep

import click
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from bagels.locations import config_file, database_file, set_custom_root
from bagels.versioning import get_current_version, get_pypi_version, needs_update


@click.group(invoke_without_command=True)
@click.option(
    "--at",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
    help="Specify the path.",
)
@click.pass_context
def cli(ctx, at: click.Path | None):
    """Bagels CLI."""
    if at:
        set_custom_root(at)
    if ctx.invoked_subcommand is None:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(f"Loading configuration from '{at}'...", total=3)

            from bagels.config import load_config

            load_config()

            from bagels.config import CONFIG

            if CONFIG.state.check_for_updates:
                progress.update(task, advance=1, description="Checking for updates...")

                if needs_update():
                    new = get_pypi_version()
                    cur = get_current_version()
                    click.echo(
                        click.style(
                            f"New version available ({cur} -> {new})! Update with:",
                            fg="yellow",
                        )
                    )
                    click.echo(click.style("```uv tool upgrade bagels```", fg="cyan"))
                    click.echo(
                        click.style(
                            "You can disable this check in-app using the command palette.",
                            fg="bright_black",
                        )
                    )
                    sleep(2)

            progress.update(task, advance=1, description="Initializing database...")

            from bagels.models.database.app import init_db

            init_db()
            progress.update(task, advance=1, description="Starting application...")

            from bagels.app import App

            app = App()
            progress.update(task, advance=1)

        app.run()


@cli.command()
@click.argument("thing_to_locate", type=click.Choice(["config", "database"]))
def locate(thing_to_locate: str) -> None:
    if thing_to_locate == "config":
        print("Config file:")
        print(config_file())
    elif thing_to_locate == "database":
        print("Database file:")
        print(database_file())


if __name__ == "__main__":
    cli()
