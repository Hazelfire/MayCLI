"""
File: cli.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A click cli for may
"""
from functools import wraps
from importlib.resources import read_text
from requests.exceptions import ConnectionError
import requests

from quickconfig import Config
from graphjinj import run
import docsep
from jinja2 import Template
from docopt import docopt
import sys
import yaml

conf = Config("may")
BASE_URL = "http://localhost:8000/graphql"

def run_view(docs, arguments):
    """ Runs a may view """
    view_file = None
    try:
        if len(arguments) > 1 and not arguments[1].startswith("--"):
            view_file = read_text("may.views." + arguments[0], arguments[1] + ".gjinj")
        else:
            view_file = read_text("may.views", arguments[0] + ".gjinj")
    except FileNotFoundError:
        print(docs.strip())
        return
    documents = docsep.parse(view_file)
    args = docopt(documents["command"].body, argv=arguments, help=True)

    variables = {}
    if "variables" in documents:
        variables = yaml.load(Template(documents["variables"].body).render(args))


    session = requests.Session()
    if "token" in conf:
        session.headers.update({"Authorization": "JWT " + conf["token"]})
    res = run(
        BASE_URL,
        view_file,
        variables,
        session=session,
    )
    print(res.display)

doc = """
Usage: may [--version] [--help] [<command>] [<args>...]

Commands include:
    task
    folder
    login
"""

def cli():
    """ Main entry point """
    args = docopt(doc, version="May version 0.0.1", options_first=True, help=True)
    if args["<command>"]:
        run_view(doc, [args["<command>"]] + args["<args>"])
    else:
        print(doc.strip())
            





