"""
A simple api wrapper for calling the backend with the given config
"""

import json

import requests

from quickconfig import Config

BASE_URL = "http://localhost:8000/graphql"
conf = Config("may")

def call(query, variables):
    """
    Calls the backend with a GraphQL Query
    """
    # Add Auth token
    session = requests.Session()
    if "token" in conf:
        session.headers.update({"Authorization": "JWT " + conf["token"]})

    return session.post(
        BASE_URL,
        data={
            "query": query,
            "variables": json.dumps(variables),
        },
    ).json()
