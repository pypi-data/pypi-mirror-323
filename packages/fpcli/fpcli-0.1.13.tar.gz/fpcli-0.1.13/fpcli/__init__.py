from .commands import *
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main entry point."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
