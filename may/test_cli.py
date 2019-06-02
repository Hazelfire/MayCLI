import click
from click.testing import CliRunner
from .cli import login

def test_login_cli():
    """ tests the login command. Checks if it correctly returns the token """
    runner = CliRunner()
    result = runner.invoke(login)
    assert result.exit_code = 0
    assert result.text = "login"
    
