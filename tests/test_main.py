from click.testing import CliRunner

from acapela_group.__main__ import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert result.output == 'Hello world!\n'
