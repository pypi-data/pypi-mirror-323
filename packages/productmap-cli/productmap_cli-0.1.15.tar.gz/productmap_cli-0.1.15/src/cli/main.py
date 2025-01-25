import click

from cli.pmcli import generate_map, validate_file, get_map_generation_status


@click.command()
@click.version_option()
@click.pass_context
@click.argument("token")
@click.option("--file")
@click.option("--salt")
@click.option("--action", type=click.Choice(["validate", "generate", "status"]), required=True)
def main(
        ctx: click.Context,
        token: str,
        file: str,
        salt: str,
        action: str
):
    """
        CLI for validating and generating maps for files using the ProductMap API.
        """
    try:
        if action == "validate":
            result = validate_file(ctx, token, file)
            click.echo(result)
        elif action == "generate":
            result = generate_map(ctx, token, file)
            click.echo(result)
        elif action == "status":
            get_map_generation_status(ctx, token, salt)
    except click.ClickException as e:
        ctx.fail(f"Operation failed: {e}")


if __name__ == "__main__":
    main()
