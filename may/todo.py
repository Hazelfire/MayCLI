import requests
from dateutil.parser import parse
from datetime import timedelta, datetime, timezone
import pytz


def get_due_dates(tasks):
    due_dates = {}
    propagation_count = 1
    while propagation_count > 0:
        propagation_count = 0
        for task in tasks:
            if task["due"]:
                if not task["id"] in due_dates:
                    due_dates[task["id"]] = parse(task["due"])

            if not task["done"] and task["id"] in due_dates:
                for dependency in task["dependencies"]:
                    due = due_dates[task["id"]]
                    if dependency not in due_dates or due_dates[dependency] > due:
                        due_dates[dependency] = due
                        propagation_count += 1
    return due_dates


def parse_timedelta(dur_string):
    h, m, s = dur_string.split(":")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s))


def is_aware(d):
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None


def get_urgency(task, due):
    if due:
        now = datetime.now(pytz.utc)
        if now < due:
            return parse_timedelta(task["duration"]).total_seconds() / (due - now).total_seconds() * 24
        else:
            return float('inf')
    else:
        return 0


def urgency(task):
    return task[1]


def get_todo(tasks):
    due_dates = get_due_dates(tasks)

    tasks_not_done = [task for task in tasks if (
        not task["done"]) and task["id"] in due_dates]

    urgencies = {task["id"]: get_urgency(
        task, due_dates[task["id"]]) for task in tasks_not_done}
    chained_urgencies = dict(urgencies)

    indexed_tasks = {task["id"]: task for task in tasks_not_done}

    def flow_urgency(task, urgency):
        chained_urgencies[task["id"]] += urgency
        for dependency in task["dependencies"]:
            if dependency in indexed_tasks:
                flow_urgency(indexed_tasks[dependency], urgency)

    for task in tasks_not_done:
        flow_urgency(task, urgencies[task["id"]])

    sorted_urgencies = [(key, value)
                        for key, value in chained_urgencies.items()]
    sorted_urgencies.sort(key=urgency, reverse=True)
    tasks_ordered = [indexed_tasks[key] for key, value in sorted_urgencies]
    return tasks_ordered
