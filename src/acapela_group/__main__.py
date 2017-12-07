"""Entry point."""

import click

from . import hello


@click.command(context_settings={'help_option_names': ['-h', '--help']})
def main():
    """Fetch generated tts sounds from Acapela Group."""
    click.echo(hello())


if __name__ == '__main__':
    main()
