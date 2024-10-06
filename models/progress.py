from dataclasses import dataclass
from enum import Enum


Status = Enum(
    "Status",
    [
        "FETCHING",
        "FETCHED",
        "SAVING",
        "SAVED",
        "INSERTING",
        "INSERTED",
        "FINISHED",
        "ERROR",
    ],
)


@dataclass
class Progress:
    status: Status = None
    title: str = None
    page: int = None
    total: int = None
    current: int = None


def default_progress_handler(prog: Progress):
    sub_prog = (
        f" {prog.current}/{prog.total}"
        if prog.total is not None and prog.current is not None
        else ""
    )

    mesg = f"[{prog.status.name}{sub_prog}] {prog.title}"

    if prog.page is not None:
        mesg += f" Page {prog.page}"

    print(mesg)
