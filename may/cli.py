"""
File: cli.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A click cli for may
"""
from importlib.resources import read_text
from requests.exceptions import ConnectionError
import requests

from quickconfig import Config
import docsep
from jinja2 import Template
from docopt import docopt
import sys
import yaml
import json

conf = Config("may")
BASE_URL = "http://localhost:8000/graphql"

def get_view_file(arguments):
    if len(arguments) > 1 and not arguments[1].startswith("-"):
        try:
            return read_text("may.views." + arguments[0], arguments[1] + ".gjinj")
        except ModuleNotFoundError:
            return read_text("may.views", arguments[0] + ".gjinj")
    else:
        view_file = read_text("may.views", arguments[0] + ".gjinj")
    return view_file


def run_view(docs, arguments, verbose=False):
    """ Runs a may view """

    # Getting the view
    view_file = None
    try:
        view_file = get_view_file(arguments)
    except FileNotFoundError:
        print(docs.strip())
        return

    documents = docsep.parse(view_file)

    # Parse the help doc string
    args = docopt(documents["command"].body, argv=arguments, help=True)


    # Create graphql variables from that
    variables = {}
    if "variables" in documents:
        variables = yaml.load(Template(documents["variables"].body).render({'args': args}))


    # Add Auth token
    session = requests.Session()
    if "token" in conf:
        session.headers.update({"Authorization": "JWT " + conf["token"]})

    if verbose:
        print("Query:")
        print(documents["query"].body)

        print("Variables:")
        print(variables)

    
    # Make request
    response= session.post(
        BASE_URL,
        data={
            "query": documents["query"].body,
            "variables": json.dumps(variables),
        },
    ).json()

    if verbose:
        print("Response:")
        print(response)

    # View request
    display = Template(documents["display"].body.strip()).render({
        **response,
        'args': dict(args)
    }).strip()
    print(display)

doc = """
Usage: may [-v] [--version] [--help] [<command>] [<args>...]

Commands include:
    task
    folder
    login

Options:
    -v         Verbose, prints query and response information
    --version  Prints the version and then exist
    --help     Displays this help page
"""

def cli():
    """ Main entry point """
    args = docopt(doc, version="May version 0.0.1", options_first=True, help=True)
    if args["<command>"]:
        run_view(doc, [args["<command>"]] + args["<args>"], verbose=args["-v"])
    else:
        print(doc.strip())
            





