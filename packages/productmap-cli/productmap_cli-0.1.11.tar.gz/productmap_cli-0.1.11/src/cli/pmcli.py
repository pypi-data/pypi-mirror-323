import os
import click
import httpx

from http import HTTPStatus

PRODUCT_MAP_DOMAIN_URL = "https://product-map.ai"
PRODUCT_MAP_API_DOMAIN_URL = "https://api.product-map.ai"


def read_file(ctx: click.Context, file_path: str) -> None:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        # Read the file as binary
        with open(file_path, 'rb') as file:
            file.read()
            file_size = os.path.getsize(file_path)
            click.echo(f"File '{file_path}' successfully read! Size: {file_size} bytes.")

    except FileNotFoundError as e:
        ctx.fail(str(e))
    except Exception as e:
        ctx.fail(f"An unexpected error occurred: {e}")


def set_sharing_status(ctx: click.Context, token: str, salt: str, is_shared: bool) -> None:
    click.secho(f"Setting public sharing status to : {is_shared}")
    try:
        # Open the file and send it to the API
        response = httpx.put(
            f"{PRODUCT_MAP_API_DOMAIN_URL}/llm/upload/share/{salt}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "shared": is_shared
            }
        )

        if response.status_code != HTTPStatus.OK:
            raise click.ClickException(
                f"Failed to switching sharing status. Server response: {response.text}"
            )

        map_status = "Public" if is_shared is True else "Restricted"
        click.secho(f"Public map status set to {map_status}", fg="green")

    except Exception as e:
        ctx.fail(f"An error occurred during validation: {e}")


def validate_file(ctx: click.Context, token: str, file: str) -> str:
    click.secho(f"Validating file {file}")
    read_file(ctx, file)

    try:
        # Open the file and send it to the API
        with open(file, "rb") as f:
            response = httpx.post(
                f"{PRODUCT_MAP_API_DOMAIN_URL}/llm/upload/validate",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": f}
            )

        if response.status_code != HTTPStatus.OK:
            raise click.ClickException(
                f"Failed to validate file '{file}'. Server response: {response.text}"
            )

        click.secho(f"File '{file}' validated successfully!")
        return response.text

    except Exception as e:
        ctx.fail(f"An error occurred during validation: {e}")


def generate_map(ctx: click.Context, token: str, file: str) -> str:
    click.secho(f"Generating map for file: {file}")
    read_file(ctx, file)

    try:
        # Send the file to the map generation API
        with open(file, "rb") as f:
            response = httpx.post(
                f"{PRODUCT_MAP_API_DOMAIN_URL}/llm/upload",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": f}
            )
        if response.status_code != HTTPStatus.OK:
            raise click.ClickException(
                f"Failed to generate map from file '{file}'. Server response: {response.text}"
            )

        # Parse response and construct output
        json_data = response.json()
        salt = json_data.get("salt")
        public_salt = json_data.get("public_salt")
        public_url = f"{PRODUCT_MAP_DOMAIN_URL}/app/public/{public_salt}"

        click.secho(f"Map generated successfully!")

        set_sharing_status(ctx, token, salt, True)
        click.secho(f"File '{file}' mapped with salt: {salt}, public URL: {public_url}", fg="green")
        click.secho(f"Map can be visualized once the generation process finishes...", fg="blue")
        return public_url

    except Exception as e:
        ctx.fail(f"An error occurred during map generation: {e}")
