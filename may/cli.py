"""
File: cli.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A click cli for may
"""
from importlib.resources import read_text
import json

import yaml
import dateparser
from jinja2 import Template
from docopt import docopt
from requests.exceptions import ConnectionError
import requests

from quickconfig import Config
import docsep


conf = Config("may")
BASE_URL = "http://localhost:8000/graphql"

def parse_date(date_string):
    """ Parses a human readable date to a iso string"""
    return dateparser.parse(
        date_string, settings={
            'PREFER_DATES_FROM': 'future'
        }).isoformat()

def get_view_file(arguments):
    if len(arguments) > 1 and not arguments[1].startswith("-"):
        try:
            return read_text("may.views." + arguments[0], arguments[1] + ".gjinj")
        except ModuleNotFoundError:
            return read_text("may.views", arguments[0] + ".gjinj")
    else:
        view_file = read_text("may.views", arguments[0] + ".gjinj")
    return view_file


def get_easy_id(big_id, hint=None):
    if big_id not in conf["ids"]:
        ids = conf["ids"]
        easy_id = "".join([word[0] for word in hint.split(" ")])
        if easy_id not in conf["ids"]:
            ids[big_id] = easy_id
            conf["ids"] = ids
            return easy_id
        else:
            ids[big_id] = big_id
            conf["ids"] = ids
            return big_id
    else:
        return conf["ids"][big_id]

def get_real_id(easy_id):
    for real_id, value in conf["ids"].items():
        if value == easy_id:
            return real_id
    return None


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
        variables = yaml.load(Template(documents["variables"].body).render({
            'args': args,
            'parse_date': parse_date,
            'get_real_id': get_real_id
        }))


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
    try:
        response = session.post(
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
            'args': dict(args),
            'get_real_id': get_real_id,
            'get_easy_id': get_easy_id
        }).strip()
        print(display)
    except ConnectionError:
        print("Could not connect to may")


doc = """
Usage: may [-v] [--version] [--help] [<command>] [<args>...]

Commands include:
    task
    folder
    login
    statistics
    urgency
    velocity
    ls
    todo

Options:
    -v         Verbose, prints query and response information
    --version  Prints the version and then exist
    --help     Displays this help page
"""

def cli():
    """ Main entry point """
    if "ids" not in conf:
        conf["ids"] = {}
    args = docopt(doc, version="May version 0.0.1", options_first=True, help=True)
    if args["<command>"]:
        run_view(doc, [args["<command>"]] + args["<args>"], verbose=args["-v"])
    else:
        print(doc.strip())
            





