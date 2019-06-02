"""
File: cli.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A click cli for may
"""
import click

from .api import MayApi, GraphQLException
from .config import save_token, has_token, get_token


@click.group()
def cli():
    """ Click main cli group """


@cli.command()
def login():
    """ Logs the token to file """
    username = click.prompt("Username")
    password = click.prompt("Password")
    try:
        token = MayApi.login(username, password)
        save_token(token)
        click.echo("Successfully logged in")
    except GraphQLException as e:
        click.echo("GraphQL Error: " + str(e), err=True)

@cli.command()
def tasks():
    """ Returns a list of tasks """
    if not has_token():
        click.echo("Operation requires logging in, try may login", err=True)

    token = get_token()
    api = MayApi(token)
    click.echo("\n".join([task["name"] for task in api.get_tasks()]))
