import click

from cli.pmcli import generate_map, validate_file


@click.command()
@click.version_option()
@click.pass_context
@click.argument("token")
@click.option("--file", required=True)
@click.option("--action", type=click.Choice(["validate", "generate"]), required=True)
def main(
        ctx: click.Context,
        token: str,
        file: str,
        action: str
):
    """
        CLI for validating and generating maps for files using the ProductMap API.
        """
    try:
        if action == "validate":
            result = validate_file(ctx, token, file)
        elif action == "generate":
            result = generate_map(ctx, token, file)
        click.echo(result)
    except click.ClickException as e:
        ctx.fail(f"Operation failed: {e}")


if __name__ == "__main__":
    main()
