"""
May task manager CLI
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone
import requests
import dateparser
from dateutil.parser import parse
from .todo import get_todo, get_due_dates, parse_timedelta
headers = {"authorization": "Token " +
           os.environ["MAY_TOKEN"], "Content-Type": "application/json"}
baseurl = 'https://api.may.hazelfire.net/taskapi/'


def get_folders():
    return requests.get(baseurl + 'folders/', headers=headers).json()


def get_tasks():
    return requests.get(baseurl + 'tasks/', headers=headers).json()


def parse_date(dateString):
    return dateparser.parse(dateString, settings={
        'PREFER_DATES_FROM': 'future'
    }).isoformat() + "Z"


def get_root(folders):
    for folder in folders:
        if folder["root"]:
            return folder


def traverse(pwd, path, folders):
    """ Traverses a path given through folders """
    if not path:
        return pwd
    for folder in folders:
        if folder["parent"] == pwd["id"] and folder["name"] == path[0]:
            return traverse(folder, path[1:], folders)
    return None


def list_folder(target, folders, tasks):
    for folder in folders:
        if folder["parent"] == target["id"]:
            print("{} - {} (folder)".format(folder["id"], folder["name"]))
    for task in tasks:
        if task["parent"] == target["id"]:
            print("{} - {} (task)".format(task["id"], task["name"]))


def find_folder(folders, path):
    root = get_root(folders)
    return traverse(root, path, folders)


def list_subparser(subparsers):
    """ List all tasks """
    parser = subparsers.add_parser("list", help=list_subparser.__doc__)
    parser.add_argument(
        "--due", "-d", help="Only select have due dates", action="store_true")
    parser.add_argument(
        "--incomplete", "-i", help="Only select tasks that aren't done", action="store_true")
    parser.add_argument(
        "--orphaned", "-o", help="Only select tasks that don't have due dates and are not done", action="store_true")

    def run(args):
        tasks = get_tasks()
        if args.due:
            tasks = [task for task in tasks if task["due"]]
        if args.incomplete:
            tasks = [task for task in tasks if not task["done"]]
        if args.orphaned:
            tasks = [task for task in tasks if not task["done"]
                     and not task["due"]]
        for task in tasks:
            print("{} - {}".format(task["id"], task["name"]))

    parser.set_defaults(run=run)
    return parser


def complete_subparser(subparsers):
    """ Completes a task with a given id """
    parser = subparsers.add_parser("complete", help=complete_subparser.__doc__)
    parser.add_argument("id", help="Id of task to complete")

    def run(args):
        response = requests.patch(
            baseurl + 'tasks/' + args.id + "/",
            headers=headers,
            data=json.dumps({"done": True})
        )
    parser.set_defaults(run=run)
    return parser


def ls_subparser(subparsers):
    """ Lists items in a given folder """
    parser = subparsers.add_parser("ls", help=ls_subparser.__doc__)
    parser.add_argument(
        "path", nargs="?", help="The path that you want to list the contents of", default="")

    def run(args):
        if args.path:
            path = args.path.split("/")
        else:
            path = []
        folders = get_folders()
        target = find_folder(folders, path)
        if target:
            list_folder(target, folders, get_tasks())
        else:
            print("Cannot find folder")

    parser.set_defaults(run=run)
    return parser


def mkdir_subparser(subparsers):
    """ Makes a folder given a path """
    parser = subparsers.add_parser("mkdir", help=mkdir_subparser.__doc__)
    parser.add_argument(
        "path", help="The path that you want to make the folder")

    def run(args):
        path = args.path.split("/")
        folders = get_folders()
        target = find_folder(folders, path[:-1])
        name = path[-1]
        requests.post(
            baseurl + "folders/",
            json={"name": name, "parent": target["id"]},
            headers=headers
        )

    parser.set_defaults(run=run)
    return parser


def new_subparser(subparsers):
    """ Makes a new task """
    parser = subparsers.add_parser("new", help=new_subparser.__doc__)
    parser.add_argument(
        "path",
        help="The path where you want the task"
    )
    parser.add_argument(
        "--duration",
        help="The duration of the task in hours",
        type=float,
        required=True
    )

    parser.add_argument(
        "--due",
        help="When the task is due"
    )

    parser.add_argument(
        "--dependency",
        help="Comma seperated tasks that need to be completed before this one",
        action="append",
        default=[]
    )

    parser.add_argument(
        "--labels",
        help="Comma seperated labels to do with this task"
    )

    def run(args):
        path = args.path.split("/")
        folders = get_folders()
        target = find_folder(folders, path[:-1])
        name = path[-1]

        response = requests.post(
            baseurl + "tasks/",
            json={
                "name": name,
                "parent": target["id"],
                "duration": args.duration * 60 * 60,
                "due": parse_date(args.due) if args.due else None,
                "dependencies": args.dependency
            },
            headers=headers
        )
        return 0 if response.status_code == 201 else 1

    parser.set_defaults(run=run)
    return parser


def edit_subparser(subparsers):
    """ Edits a task """
    parser = subparsers.add_parser("edit", help=new_subparser.__doc__)
    parser.add_argument(
        "task",
        help="The id of the task you are referring to"
    )
    parser.add_argument(
        "--duration",
        help="The duration of the task in hours",
        type=float,
    )

    parser.add_argument(
        "--due",
        help="When the task is due"
    )

    parser.add_argument(
        "--dependencies",
        help="Comma seperated tasks that need to be completed before this one"
    )

    parser.add_argument(
        "--labels",
        help="Comma seperated labels to do with this task"
    )

    def run(args):
        patches = {}

        if args.duration:
            patches["duration"] = args.duration * 60 * 60

        if args.due:
            patches["due"] = parse_date(args.due)

        if args.dependencies:
            patches["dependencies"] = args.dependencies.split(",")

        response = requests.patch(
            baseurl + "tasks/" + args.task + "/",
            json=patches,
            headers=headers
        )

    parser.set_defaults(run=run)
    return parser


def todo_subparser(subparsers):
    """ Gives the tasks that need to be done in priority order """
    parser = subparsers.add_parser(
        "todo", help=todo_subparser.__doc__)

    def run(args):
        tasks = get_tasks()
        todo = get_todo(tasks)
        for task in todo:
            print("{} - {}".format(task["id"], task["name"]))
    parser.set_defaults(run=run)


def print_task(task):
    print("{} - {} ({})\nDuration: {} hours\nDue: {}\nDependencies:\n{}".format(
        task["id"],
        task["name"],
        "completed" if task["done"] else "not complete",
        task["duration"],
        task["due"] if task["due"] else "No Due date",
        "\n".join([" - " + dependency for dependency in task['dependencies']])
    ))


def print_subparser(subparsers):
    """ Print the task details """
    parser = subparsers.add_parser("print", help=print_subparser.__doc__)

    parser.add_argument(
        "task", help="the id of the task that you want to print")

    def run(args):
        tasks = get_tasks()
        for task in tasks:
            if task["id"] == args.task:
                print_task(task)
    parser.set_defaults(run=run)
    return parser


def get_hours(dur_string):
    return parse_timedelta(dur_string).total_seconds() / 60 / 60


def urgency_subparser(subparsers):
    """ Gets the urgency of all tasks on the list """
    parser = subparsers.add_parser("urgency", help=urgency_subparser.__doc__)

    def run(args):
        tasks = get_tasks()
        due_dates = get_due_dates(tasks)

        def get_due(task):
            return due_dates[task["id"]].timestamp()

        tasks_not_done = [
            task for task in tasks
            if (not task["done"]) and task["id"] in due_dates
        ]

        tasks_not_done.sort(key=get_due)

        last_due = datetime.now(timezone.utc)
        now = datetime.now(timezone.utc)
        extra_time = 0
        urgency = 0

        for task in tasks_not_done:
            current_due = due_dates[task["id"]]
            days_from_now = (
                current_due - now).total_seconds() / (60 * 60 * 24)
            if days_from_now < 0:
                print("Overdue_task: {}".format(task["name"]))
                urgency += float('inf')
            extra_days = (
                current_due - last_due).total_seconds() / (60 * 60 * 24)
            extra_time += extra_days * urgency

            time_left = max(0, get_hours(task["duration"]) - extra_time)
            extra_time = max(0, extra_time - get_hours(task["duration"]))
            urgency += time_left / days_from_now
            last_due = current_due
        print(urgency)

    parser.set_defaults(run=run)
    return parser


def main():
    """ Main method """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="sub-command help")
    list_subparser(subparsers)
    complete_subparser(subparsers)
    ls_subparser(subparsers)
    mkdir_subparser(subparsers)
    new_subparser(subparsers)
    todo_subparser(subparsers)
    print_subparser(subparsers)
    edit_subparser(subparsers)
    urgency_subparser(subparsers)

    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
