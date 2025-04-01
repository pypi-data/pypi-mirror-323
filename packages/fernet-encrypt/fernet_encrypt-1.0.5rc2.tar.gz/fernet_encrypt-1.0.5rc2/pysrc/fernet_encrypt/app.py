from pathlib import Path

import typer

from fernet_encrypt import cli, logger
from fernet_encrypt.commands import create_key, decrypt, encrypt


@cli.command(name="create-fernet-key")
def create_fernet_key():
    create_key()


@cli.command(name="encrypt-file")
def encrypt_file(
    input_file: Path = typer.Argument(default=..., exists=True),
    output_file: Path | None = typer.Argument(default=None),
):
    with open(input_file, "rb") as f:
        input_data = f.read()

    result = encrypt(input_data)

    if output_file is not None:
        with open(output_file, "wb") as f:
            f.write(result)

        logger.info(f"Encrypted file: {input_file} -> {output_file}")

    else:
        try:
            result = result.decode("utf-8")
        except UnicodeDecodeError:
            pass

        typer.echo(f"Encrypted file: {input_file}:\n{result}")


@cli.command(name="decrypt-file")
def decrypt_file(
    input_file: Path = typer.Argument(default=..., exists=True),
    output_file: Path | None = typer.Argument(default=None),
):
    with open(input_file, "rb") as f:
        input_data = f.read()

    result = decrypt(input_data)

    if output_file is not None:
        with open(output_file, "wb") as f:
            f.write(result)

        logger.info(f"Decrypted file: {input_file} -> {output_file}")

    else:
        try:
            result = result.decode("utf-8")
        except UnicodeDecodeError:
            pass

        typer.echo(f"Decrypted file: {input_file}:\n{result}")
