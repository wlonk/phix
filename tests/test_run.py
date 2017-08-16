from click.testing import CliRunner

import phix
from phix import main


def test_run(mocker):
    mock_TCPServer = mocker.patch.object(phix.socketserver, 'TCPServer')

    runner = CliRunner()
    result = runner.invoke(main)

    assert result.exit_code == 0
    assert mock_TCPServer.call_count == 1
