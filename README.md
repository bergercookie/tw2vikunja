# `tw2vikunja`

Easily convert your [`Taskwarrior`](https://taskwarrior.org/) tasks to
[`Vikunja`](https://vikunja.io) tasks.

## Installation

This script is currently not available on PyPi (PRs to convert it to a proper
package and upload to PyPI are more than welcome). To install it, just download
the `tw2vikunja` script somewhere locally and, assuming you have
[`uv`](https://github.com/astral-sh/uv) installed locally, just execute the
script

```sh
/path/to/tw2vikunja
```

This will install any dependencies of the `tw2vikunja` script (at the time of
writing only the `pyperclip` package), in a dedicated virtual environment and
will execute the script in that environment.

Alternatively, you can also install the dependencies manually and execute the
script directly:

```sh
pip install pyperclip
python3 -m /path/to/tw2vikunja
```

## Usage

You can find some usage examples by running the script with the `--help` flag:

- Get all the tasks from the pending `taskwarrior` database and convert them to
  `Vikunja` tasks (doesn't include `+WAITING` tasks):

  ```sh
  task status:pending export | tw2vikunja"
  ```

- Get all the tasks from the `myproject` project and convert them to `Vikunja`

  ```sh
  task pro:myproject export | tw2vikunja"
  ```

- Get all the tasks from the `myproject` project and convert them to `Vikunja`,
  but skip converting to the local timezone:

  ```sh
  task pro:myproject export | tw2vikunja --skip-convert-tz"
  ```

- Get all the tasks from the `myproject` project and convert them to `Vikunja`,
  but skip adding any tags:

  ```sh
  task pro:myproject export | tw2vikunja --skip-tags"
  ```

Commands like the above (unless a relevant filter is applied) should create a
formatted output, one line per task, which can be copy-pasted in the `Vikunja` task
addition prompt so that the tasks are added to the `Vikunja` database. To
facilitate the pasting, the said output is automatically added to the clipboard
(unless the `--skip-copy` flag is set).

### Example output

```sh
task pro:run export | tw2vikunja
```

The above should create an output similar to the following, with `taskwarrior` tags
converted to `*{tag}` and `taskwarrior` projects converted to `+{project}`.
Dates are written as `DD/MM/YYYY` and times as `at HH:MM`:

```txt
How many days to stay there? +paris *remindme 30/01/2024 at 00:00
Book travel tickets +paris *remindme 30/01/2024 at 00:00
Book for holiday on Thursday, Friday and Monday +paris
Book airbnb +paris *remindme 30/01/2024 at 00:00
Register for marathon 30/01/2024 at 14:00 +paris
```

The output can be copy-pasted to the `Vikunja` prompt:

![Vikunja prompt](/share/images/vikunja-prompt-copy-paste.png)

### Notes

- Projects specified in the `Vikunja` prompt have to exist beforehand in `Vikunja`
  otherwise this information is discarded.
