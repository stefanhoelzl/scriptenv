"""
Everything needed to create new releases.
"""
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, Generator, List

import fire

CategoryKeywords = {
    "Features": "feature",
    "Bugfixes": "bugfix",
    "Internal": "internal",
    "Tooling": "tooling",
}
ChangelogCategories = ["Features", "Bugfixes", "Internal"]
CommitMessageRegex = re.compile(
    rf"\[(?P<category>{'|'.join(CategoryKeywords.values())})\] (?P<message>.*)"
)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args]).decode("utf-8").strip()


def check_commit_messages() -> Generator[str, None, None]:
    """Checks if the all commit messages in the log are valid."""
    invalid_messages = [
        msg
        for msg in _git("log", "--pretty=%s").split("\n")
        if not re.match(CommitMessageRegex, msg)
    ]
    yield from (f"Invalid commit message: {msg}" for msg in invalid_messages)
    if invalid_messages:
        sys.exit(1)


def changelog() -> Generator[str, None, None]:
    """Creates a changelog from git history."""
    yield from _formatted_commits_by_category(_commits_by_category())


CommitsByCategory = Dict[str, List[str]]


def _commits_by_category() -> CommitsByCategory:
    commits_by_category = defaultdict(list)
    for msg in reversed(_git("log", "--pretty=%s").split("\n")):
        match = re.match(CommitMessageRegex, msg)
        if match:
            commits_by_category[match.group("category")].append(match.group("message"))
    return commits_by_category


def _formatted_commits_by_category(
    commits_by_category: CommitsByCategory,
) -> Generator[str, None, None]:
    for category, keyword in CategoryKeywords.items():
        if category in ChangelogCategories and len(commits_by_category[keyword]) > 0:
            yield f"* {category}"
            for message in commits_by_category[keyword]:
                yield f"  * {message}"


if __name__ == "__main__":
    fire.Fire()
