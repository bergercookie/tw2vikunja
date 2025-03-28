#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyperclip",
# ]
# ///


import argparse
import datetime
import sys
import json
import pyperclip


class BreaklinesFormatter(argparse.RawDescriptionHelpFormatter):
    """Prefix your help message with "R|" if you want to interpret line boundaries and \n characters."""

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()

        return argparse.HelpFormatter._split_lines(self, text, width)


def convert_date(date: str, convert_tz_to_local: bool = True) -> str:
    """
    Convert a Taskwarrior date to a Vikunja date.

    :param date: The Taskwarrior date to convert.
    :param correct_tz: Whether to convert the date to the local timezone or leave it it as is.

    Input date example: 20241210T222850Z
    Ouptut date example: 10/12/2024 at 22:28
    """

    # parse the datetime into a datetime object
    dt = datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ")
    dt = dt.replace(tzinfo=datetime.timezone.utc)

    if convert_tz_to_local:
        # get local timezone
        local_tz = datetime.datetime.now().astimezone().tzinfo
        dt = dt.astimezone(local_tz)

    vik_date = f'{dt.strftime("%m/%d/%Y")} at {dt.strftime("%H:%M")}'

    return vik_date


def main() -> int:
    # define argument parser ------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        (
            "Convert your Taskwarrior tasks to Vikunja tasks.\n"
            "Pipe the output of `task export` to this script to convert your "
            "tasks to Vikunja tasks, then copy paste them into Vikunja.\n"
            "Notes:\n\n"
            "  - You have to add the projects manually in vikunja for the "
            "+project part of the tasks to work.\n"
        ),
        formatter_class=BreaklinesFormatter,
    )
    parser.add_argument(
        "--skip-convert-tz",
        action="store_true",
        help="Skip converting the date to the local timezone.",
    )
    parser.add_argument(
        "--no-tags",
        action="store_true",
        help="Skip converting taskwarrior tags to vikunja tags",
    )
    parser.add_argument(
        "--exclude-tags",
        nargs="?",
        default=[],
        help="Specify a set of tags to not include in the vikunja outptut",
    )

    parser.add_argument(
        "--no-projects",
        action="store_true",
        help="Skip converting taskwarrior projects to vikunja projects",
    )

    # skip the date
    parser.add_argument(
        "--no-date",
        action="store_true",
        help="Skip converting taskwarrior due date to vikunja due date",
    )

    # read the filter from stdin
    parser.add_argument(
        "filter",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help=(
            "R|The filter to get the TW tasks to convert to Vikunja. \n"
            "Use `task export` to figure out the right filter parameters for your usecase. \n"
            "You can also pipe the output of `task export` to this script - e.g. for all pending tasks, `task status:pending export | tw2vikunja`."
        ),
    )

    # argument for automatically copying the output to the clipboard
    parser.add_argument(
        "--skip-copy",
        dest="skip_copy_to_clipboard",
        action="store_true",
        help="Skip copying the output to the clipboard.",
    )

    parser.epilog = (
        "Example usage:\n========\n\n"
        "\n* task status:pending  export | tw2vikunja"
        "\n* task pro:myproject   export | tw2vikunja"
        "\n* task pro:myproject   export | tw2vikunja --skip-convert-tz"
        "\n* task pro:myproject   export | tw2vikunja --skip-tags"
        "\n* task +mytag1 +mytag2 export | tw2vikunja --skip-project"
        "\n* task pro:myproject   export | tw2vikunja"
    )

    # parse arguments -------------------------------------------------------------------------
    parser_args = parser.parse_args()

    filter_ = parser_args.filter.read()
    skip_convert_tz = parser_args.skip_convert_tz
    skip_tags = parser_args.no_tags
    skip_projects = parser_args.no_projects
    skip_date = parser_args.no_date
    exclude_tags = parser_args.exclude_tags
    copy_to_clipboard = not parser_args.skip_copy_to_clipboard

    # convert tasks ---------------------------------------------------------------------------
    if not filter_:
        print("No tasks to convert.")
        return 0

    tasks = json.loads(filter_)

    commands = []
    for task in tasks:
        # description
        cmd = task["description"]

        # project
        if not skip_projects and (tw_project := task.get("project")):
            project = tw_project.split(".")[
                -1
            ]  # take only the last part of the project
            cmd += f" +{project}"

        # tags
        if not skip_tags:
            for tag in task.get("tags", []):
                if tag not in exclude_tags:
                    cmd += f" *{tag}"

        # due date
        if not skip_date and (due := task.get("due")):
            due = convert_date(due, convert_tz_to_local=not skip_convert_tz)
            cmd += f" {due}"

        print(cmd)
        commands.append(cmd)

    # copy to clipboard
    if copy_to_clipboard:
        pyperclip.copy("\n".join(commands))

    return 0


if __name__ == "__main__":
    sys.exit(main())
