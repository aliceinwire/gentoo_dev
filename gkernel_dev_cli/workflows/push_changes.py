#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from git.repo.base import Repo
import os
import shutil
import subprocess
from pathlib import Path
CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = CURRENT_DIR.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
GIT_DIR = str(RESOURCES_DIR / "git")
SCRIPTS_DIR = str(RESOURCES_DIR / "scripts")
GENTOO_REPO_DIR = str(PACKAGE_DIR / "gentoo_repository")
LINUX_PATCHES_REPO_DIR = str(PACKAGE_DIR / "linux-patches")
IRC_DIR = str(RESOURCES_DIR / "irc_bot")


def check_git_push():
    # run the git push command with the --dry-run option
    process = subprocess.Popen(["git", "push", "--dry-run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # check if there are any commits that need to be pushed
    if "Everything up-to-date" in error.decode("utf-8"):
        os.system('echo "No changes to push" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ output.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ error.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        print("Nothing to push!")
        return True
    else:
        os.system('echo "The following commits need to be pushed:" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ output.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ error.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')

    # run the git push command
    process = subprocess.Popen(["pkgdev", "push", "--pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # check if the command was successful
    if process.returncode == 0:
        print("Git push was successful!")
        os.system('echo "'+ output.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ error.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "pushed changes" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        return True
    else:
        print("Error occurred during git push:")
        print(error.decode("utf-8").strip())
        os.system('echo "'+ output.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "'+ error.decode("utf-8").strip() +'" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        os.system('echo "ERROR on pushing changes" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
        return False


# copy git configurations to gentoo repository
shutil.copyfile(GIT_DIR+'/gentoo_repository_config',GENTOO_REPO_DIR+"/.git/config")
os.chdir(GENTOO_REPO_DIR)
# send changes
check_git_push()
