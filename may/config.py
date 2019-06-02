"""
File: config.py
Author: Sam Nolan
Email: sam.nolan@rmit.edu.au
Github: https://github.com/Hazelfire
Description: Config data for the may cli
"""

import os

CONFIG_DIR = os.path.expanduser("~/.config/may")
TOKEN_FILE = CONFIG_DIR + "/token"


def has_token():
    """ Returns if the token file has been saved to file """
    return os.path.exists(TOKEN_FILE)


def save_token(token):
    """ Saves the given token to file """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    open(TOKEN_FILE, "w").write(token)


def get_token():
    """ Gets the token from file """
    return open(TOKEN_FILE).read()
