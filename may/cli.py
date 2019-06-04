"""
File: cli.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A click cli for may
"""
from functools import wraps
from importlib.resources import read_text
import click
from requests.exceptions import ConnectionError
import requests

from .api import MayApi, GraphQLException
from quickconfig import Config
from graphjinj import run

conf = Config("may")
BASE_URL = "http://localhost:8000/graphql"

def fails_gracefully(command):
    """ Wraps a command so that it fails gracefully when exceptions are thrown """
    @wraps(command)
    def wrapper(*args, **kwargs):
        try:
            command(*args, **kwargs)
        except GraphQLException as e:
            click.echo("GraphQL Error: " + str(e), err=True)
        except ConnectionError as e:
            click.echo("Could not connect to url")
    return wrapper

def requires_auth(command):
    """ Wrapper for commands that require auth before executing """
    @wraps(command)
    @fails_gracefully
    def wrapper(*args, **kwargs):
        if "token" in conf:
            click.echo("Operation requires logging in, try may login", err=True)
            return
        command(*args, **kwargs)
    return wrapper

def run_view(template, variables=None):
    """ Runs a may view """
    session = requests.Session()
    if not variables:
        variables = {}
    if "token" in conf:
        session.headers.update({"Authorization": "JWT " + conf["token"]})
    return run(
        BASE_URL,
        read_text("may.views", template),
        variables,
        session=session,
    )


@click.group()
def cli():
    """ Click main cli group """


@cli.command()
@fails_gracefully
def login():
    """ Logs the token to file """
    username = click.prompt("Username")
    password = click.prompt("Password")

    result = run_view(
        "login.gjinj",
        {'username': username, 'password': password}
    )
    if "data" in result.json:
        conf["token"] = result.json["data"]["tokenAuth"]["token"]
    click.echo(result.display)

@cli.group()
def task():
    """ task related commands """

@task.command(name="add")
@click.argument("name")
@click.argument("duration", type=int)
@fails_gracefully
def task_add(name, duration):
    """ adds a task """
    click.echo(run_view("addTask.gjinj", {
        'input': {
            'name': name,
            'duration': duration
        }
    }).display)



@task.command(name="list")
@fails_gracefully
def task_list():
    """ returns a list of tasks """
    click.echo(run_view("getTasks.gjinj").display)
