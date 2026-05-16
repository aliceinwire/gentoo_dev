from __future__ import annotations

from pathlib import Path

import git
from alive_progress import alive_bar
from git.repo.base import Repo


class GitRemoteProgress(git.RemoteProgress):
    OP_CODES = [
        "BEGIN",
        "CHECKING_OUT",
        "COMPRESSING",
        "COUNTING",
        "END",
        "FINDING_SOURCES",
        "RECEIVING",
        "RESOLVING",
        "WRITING",
    ]
    OP_CODE_MAP = {getattr(git.RemoteProgress, code): code for code in OP_CODES}

    def __init__(self) -> None:
        super().__init__()
        self.alive_bar_instance = None

    @classmethod
    def get_curr_op(cls, op_code: int) -> str:
        op_code_masked = op_code & cls.OP_MASK
        return cls.OP_CODE_MAP.get(op_code_masked, "?").title()

    def update(
        self,
        op_code: int,
        cur_count: str | float,
        max_count: str | float | None = None,
        message: str | None = "",
    ) -> None:
        cur_count = float(cur_count)
        max_count = float(max_count)

        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            self._dispatch_bar(title=self.curr_op)

        self.bar(cur_count / max_count)
        self.bar.text(message)

        if op_code & git.RemoteProgress.END:
            self._destroy_bar()

    def _dispatch_bar(self, title: str | None = "") -> None:
        self.alive_bar_instance = alive_bar(manual=True, title=title)
        self.bar = self.alive_bar_instance.__enter__()

    def _destroy_bar(self) -> None:
        self.alive_bar_instance.__exit__(None, None, None)


def save_repo(source: str, directory: str | Path, git_branch: str = "master") -> None:
    directory = str(directory)
    if not Path(directory).exists():
        Repo.clone_from(source, directory, branch=git_branch, progress=GitRemoteProgress())
    else:
        repo = Repo(directory)
        repo.remotes[0].pull()
