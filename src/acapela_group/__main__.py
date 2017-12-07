"""Entry point."""

import click


@click.command(context_settings={'help_option_names': ['-h', '--help']})
def main():
    """Fetch generated tts sounds from Acapela Group."""
    click.echo("Use acapela_group as a library!")


if __name__ == '__main__':
    main()
