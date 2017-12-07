"""Entry point."""

import click

from .base import AcapelaGroup, AcapelaGroupError


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument("language")
@click.argument("voice")
@click.argument("text")
@click.option("--username", help="Acapela Group username (if authenticating).")
@click.option("--password", help="Acapela Group password (if authenticating).")
def main(language, voice, text, username=None, password=None):
    """Fetch generated tts sounds from Acapela Group."""
    click.echo("Use acapela_group as a library!")
    acapela_group = AcapelaGroup()

    # The two options must be provided together.
    if username is not None and password is None or \
            password is not None and username is None:
        click.secho("Please provide *BOTH* username and password, or nothing "
                    "at all.", fg="red")
        raise SystemExit(-1)
    else:
        do_authenticate = username is not None and password is not None

    if do_authenticate:
        try:
            acapela_group.authenticate(username, password)
        except AcapelaGroupError as exn:
            click.secho(str(exn), fg='red')
            raise SystemExit(-2)

    click.echo(acapela_group.get_mp3_url(language, voice, text))


if __name__ == '__main__':
    main()
