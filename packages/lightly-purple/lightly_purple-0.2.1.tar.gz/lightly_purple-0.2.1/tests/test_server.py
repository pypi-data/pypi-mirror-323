"""Test module for the Server class."""

from unittest.mock import patch

from server.server import Server


def test_server_initialization():
    """Test that the Server class initializes correctly."""
    host = "127.0.0.1"
    port = 8000
    server = Server(host, port)

    assert server.host == host
    assert server.port == port


@patch("uvicorn.run")
def test_server_start(mock_run):
    """Test that the start method calls uvicorn.run with correct arguments."""
    host = "127.0.0.1"
    port = 8000
    server = Server(host, port)

    # Call the start method
    server.start()

    # Assert uvicorn.run was called
    mock_run.assert_called_once()
