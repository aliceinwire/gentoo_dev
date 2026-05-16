#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import toml
import sys
import shutil
import subprocess
from pathlib import Path
from gkernel_dev_cli.lib.git_helpers import save_repo
from gkernel_dev_cli.lib.kernel_org import get_branches, get_links
CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = CURRENT_DIR.parent
REPOROOT_DIR = CURRENT_DIR.parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
GIT_DIR = str(RESOURCES_DIR / "git")
SCRIPTS_DIR = str(RESOURCES_DIR / "scripts")
GENTOO_REPO_DIR = str(REPOROOT_DIR / "gentoo_repository")
LINUX_PATCHES_REPO_DIR = str(REPOROOT_DIR / "linux-patches")
print(LINUX_PATCHES_REPO_DIR )
GENPATCHES_MISC_REPO_DIR = str(REPOROOT_DIR / "repos/genpatches-misc")
COMMITS_DIR = str(REPOROOT_DIR / "commits") + "/"

def resolve_dev_settings_path():
    xdg_config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return xdg_config_home / "gkernel-dev" / "dev_settings.toml"

def check_git_push(branch, web_branch):
    pass
    # run the git push command
    process = subprocess.Popen(["git", "push", "origin", branch], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

# load settings file
dev_settings_path = resolve_dev_settings_path()
with open(dev_settings_path) as f:
    dev_settings = toml.load(f)

# {'gkernelci_try': {'try_master': '<url>:5555',
# 'try_username': 'Developer', 'try_password': 'example', 
# 'try_comment': 'testing', 'try_who': 'alicef'}}
gkernelci_try=dev_settings['gkernelci_try']

# download linux-patches repository
save_repo("git+ssh://git@git.gentoo.org/proj/linux-patches.git", \
     LINUX_PATCHES_REPO_DIR)
# download genpatches repository
save_repo("git+ssh://git@git.gentoo.org/proj/linux-patches.git", \
     GENPATCHES_MISC_REPO_DIR, git_branch="genpatches-misc")

# copy git configurations to gentoo repository
# shutil.copyfile(GIT_DIR+'/gentoo_repository_config',GENTOO_REPO_DIR+"/.git/config")
os.chdir(LINUX_PATCHES_REPO_DIR)
# update GkernelCI scripts
shutil.copytree(SCRIPTS_DIR+'/linux-patches/buildbot/', LINUX_PATCHES_REPO_DIR+'/.buildbot/', dirs_exist_ok=True)
# get kernel branches from website
branches=get_branches()
# Remove EOL branch
branches.remove('6.19')
## Add branch
## branches.append('6.19')
print(branches)
# During the merging efforts the two Kconfig options were abandoned in the
# v5.4.3-rt1 release and since then there is only PREEMPT_RT which enables
# the full features set (as PREEMPT_RT_FULL did in earlier releases).
# https://github.com/torvalds/linux/commit/6829061315065c7af394d556a887fbf847e4e708
# update gentoo repo
for branch in branches:
    web_kernel=0
    os.system("git checkout --quiet "+branch)
    os.system("git pull")
    # for testing keeping testing version
    #os.system("git pull --quiet")
    web_branch = get_links(branch)
    print("web branch= "+web_branch)
    for i in os.listdir(LINUX_PATCHES_REPO_DIR):
        if i.startswith("10") or i.startswith("11") or i.startswith("12") or i.startswith("13"):
            kernel_version=i.split("-")[1].split(".patch")[0]
            if web_branch == kernel_version:
                web_kernel=web_branch
    if web_kernel == 0:
        print("not found on linux-patches kernel.org version: " + web_branch)
        # start packages updating scripts
        os.system(SCRIPTS_DIR+"/linux-patches/gkernel_up.sh")
        # test changes on gkernelci
        os.system("python .buildbot/format.py"\
                  + " " + gkernelci_try["try_master"]\
                  + " " + gkernelci_try["try_username"]\
                  + " " + gkernelci_try["try_password"]\
                  + " " + gkernelci_try["try_comment"]\
                  + " " + gkernelci_try["try_who"]\
                  )
        # add commits logs in the commits folders
        git_not_yet_pushed_commits_short_logs=subprocess.getoutput("git log origin..HEAD")
        git_not_yet_pushed_commits_detailed_logs=subprocess.getoutput("git log -p origin..HEAD")
        with open(COMMITS_DIR+'linux_patches_short-'+branch, mode='w') as f:
            f.write(git_not_yet_pushed_commits_short_logs)
        with open(COMMITS_DIR+'linux_patches_long-'+branch, mode='w') as f:
            f.write(git_not_yet_pushed_commits_detailed_logs)
        # push incr patch commit
        check_git_push(branch, web_branch)
        # explain what to do next
        print("check commits are ok and do: ")
        print("git checkout "+branch)
        print("gpdorelease "+branch)
