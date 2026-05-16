#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from gkernel_dev_cli.lib.git_helpers import save_repo

CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = CURRENT_DIR.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
GIT_DIR = str(RESOURCES_DIR / "git")
SCRIPTS_DIR = str(RESOURCES_DIR / "scripts")
GENTOO_REPO_DIR = str(PACKAGE_DIR / "gentoo_repository")
LINUX_PATCHES_REPO_DIR = str(PACKAGE_DIR / "linux-patches")




# download gentoo repository
save_repo("git+ssh://git@git.gentoo.org/repo/gentoo.git", GENTOO_REPO_DIR)
# copy git configurations to gentoo repository
shutil.copyfile(GIT_DIR+'/gentoo_repository_config',GENTOO_REPO_DIR+"/.git/config")
# start packages updating scripts
os.system(f"python {CURRENT_DIR / 'update_linux_patches.py'}")
os.system("python "+SCRIPTS_DIR+"rt_scraper.py")
os.system("python "+SCRIPTS_DIR+"vanilla_scraper.py")
os.system("python "+SCRIPTS_DIR+"git_scraper.py")
os.chdir(GENTOO_REPO_DIR)
git_not_yet_pushed_commits_short_logs=subprocess.getoutput("git log origin..HEAD")
git_not_yet_pushed_commits_detailed_logs=subprocess.getoutput("git log -p origin..HEAD")
os.chdir(CURRENT_DIR)
with open('commits/test_short', mode='w') as f:
    f.write(git_not_yet_pushed_commits_short_logs)
with open('commits/test_long', mode='w') as f:
    f.write(git_not_yet_pushed_commits_detailed_logs)
