"""
File: api.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: A wrapper for the may api
"""
from importlib import import_module
from importlib.resources import read_text
import json

BASE_URL = "http://localhost:8000/graphql"
QUERY_BASE = "queries/"


def get_requests():
    """ Dynamically loads requsts, for faster local operations """
    return import_module("requests")

class GraphQLException(Exception):
    """ Represents an error thrown by graphql """

def graphql(query_file, operation, parameters = {}):
    """ Sends a graphql request to the backend """
    response = get_requests().post(
        BASE_URL,
        data={
            "query": read_text("may.queries", query_file),
            "operationName": operation,
            "variables": json.dumps(parameters),
        },
    )
    result = response.json()
    if not "data" in result:
        raise GraphQLException("\n".join([error["message"] for error in result["errors"]]))

    return result["data"]

class MayApi:
    """ A python utility for accessing the backend for may """

    def __init__(self, token):
        self.token = token

    @staticmethod
    def login(username, password):
        """ Requests the backend for a token """
        return graphql(
            "login.graphql", "login", {"username": username, "password": password}
        )["tokenAuth"]["token"]

    def get_tasks(self):
        """ Returns a list of tasks from the backend """
        return [node["node"] for node in graphql("tasks.graphql", "getTasks")["allTasks"]["edges"]]

    def get_folders(self):
        return requests.get(
            BASE_URL + "folders/",
            headers={
                "authorization": "Token {}".format(self.token),
                "Content-Type": "application/json",
            },
        ).json()
