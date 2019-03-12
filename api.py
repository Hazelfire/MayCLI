import requests
BASE_URL = 'https://api.may.hazelfire.net/taskapi/'


class MayApi:
    def __init__(self, token):
        self.token = token

    def get_tasks(self):
        return requests.get(BASE_URL + 'tasks/', headers={
            "authorization": "Token {}".format(self.token),
            "Content-Type": "application/json"
        }).json()

    def get_folders(self):
        return requests.get(BASE_URL + 'folders/', headers={
            "authorization": "Token {}".format(self.token),
            "Content-Type": "application/json"
        }).json()
