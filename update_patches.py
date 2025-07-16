#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from git.repo.base import Repo
import os
import toml
import sys
import shutil
import requests
import subprocess
from bs4 import BeautifulSoup
CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
GIT_DIR=os.path.dirname(os.path.realpath(__file__))+"/git/"
SCRIPTS_DIR=os.path.dirname(os.path.realpath(__file__))+"/scripts/"
GENTOO_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/gentoo_repository/"
LINUX_PATCHES_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/linux-patches/"
GENPATCHES_MISC_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/repos/genpatches-misc/"
COMMITS_DIR=CURRENT_DIR+"/commits/"


import git
from alive_progress import alive_bar


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
    OP_CODE_MAP = {
        getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES
    }

    def __init__(self) -> None:
        super().__init__()
        self.alive_bar_instance = None

    @classmethod
    def get_curr_op(cls, op_code: int) -> str:
        """Get OP name from OP code."""
        # Remove BEGIN- and END-flag and get op name
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

        # Start new bar on each BEGIN-flag
        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            self._dispatch_bar(title=self.curr_op)

        self.bar(cur_count / max_count)
        self.bar.text(message)

        # End progress monitoring on each END-flag
        if op_code & git.RemoteProgress.END:
            self._destroy_bar()

    def _dispatch_bar(self, title: str | None = "") -> None:
        """Create a new progress bar"""
        self.alive_bar_instance = alive_bar(manual=True, title=title)
        self.bar = self.alive_bar_instance.__enter__()

    def _destroy_bar(self) -> None:
        """Destroy an existing progress bar"""
        self.alive_bar_instance.__exit__(None, None, None)

def save (source, directory, git_branch="master"):
    if not os.path.exists(directory):
        Repo.clone_from(source, directory,  branch=git_branch, progress=GitRemoteProgress())
    else:
        repo = Repo(directory)
        repo.remotes[0].pull()

def get_links(branch):
    revision=0
    return_version=""
    versions=[]
    root_url='https://kernel.org'
    r = requests.get(root_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.findChildren('table')
    my_table = tables[2]
    tr_table = my_table.findChildren('tr')
    for i in tr_table:
        version_number = get_version_number(i)
        new_version_revision = find_new_version(version_number, branch)
        if new_version_revision is not None:
            break
    return(version_number)

# clean the html table and get the version number
def get_version_number(tr_html):
    # get list of td
    tr_html = tr_html.findChildren('td')
    # td 1 contains the kernel number
    tr_html = tr_html[1]
    # get the kernel number inside strong tag
    for node in tr_html.findAll('strong'):
        tr_html_number = ''.join(node.findAll(text=True))
    return tr_html_number

def find_new_version(version_number, argument_version):
    version = version_number.split('.', 2)
    # skip versions with no revisions
    # 6.2 (mainline) and use instead into 6.2.2 [stable]
    if int(len(version)) == 2:
        return None
    try:
        version = [version[0],version[1].split('-')[0]]
    except:
        pass
    try:
        version = version[0] + '.' + version[1]
        if version == argument_version:
            return version_number
        else:
            pass
    except:
        pass

# clean the html table and get the version number
def get_kernel(tr_html):
    # get list of td
    tr_html = tr_html.findChildren('td')
    # td 1 contains the kernel number
    version_html = tr_html[1]
    branch_html = tr_html[0]
    # get the kernel number inside strong tag
    for node in version_html.findAll('strong'):
        version_string = ''.join(node.findAll(text=True))
    branch_string=''.join(branch_html.findAll(text=True))
    return branch_string + " " + version_string


def get_branches():
    branches=[]
    kernel_string=[]
    root_url='https://kernel.org'
    r = requests.get(root_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.findChildren('table')
    my_table = tables[2]
    tr_table = my_table.findChildren('tr')
    for i in tr_table:
        kernel_string.append(get_kernel(i))
    for i in kernel_string:
        kernel_release=i.split(" ")[0]
        if kernel_release == "stable:" or kernel_release == "longterm:":
            branches.append(i.split(" ")[1].split(".")[0]+"."+i.split(" ")[1].split(".")[1])
    return(branches)

# load settings file
with open("./dev_settings.toml") as f:
    dev_settings = toml.load(f)

# {'gkernelci_try': {'try_master': '<url>:5555',
# 'try_username': 'Developer', 'try_password': 'example', 
# 'try_comment': 'testing', 'try_who': 'alicef'}}
gkernelci_try=dev_settings['gkernelci_try']

# download linux-patches repository
save("git+ssh://git@git.gentoo.org/proj/linux-patches.git", \
     LINUX_PATCHES_REPO_DIR)
# download genpatches repository
save("git+ssh://git@git.gentoo.org/proj/linux-patches.git", \
     GENPATCHES_MISC_REPO_DIR, git_branch="genpatches-misc")
# copy git configurations to gentoo repository
# shutil.copyfile(GIT_DIR+'/gentoo_repository_config',GENTOO_REPO_DIR+"/.git/config")
os.chdir(LINUX_PATCHES_REPO_DIR)
# update GkernelCI scripts
shutil.copytree(SCRIPTS_DIR+'linux-patches/buildbot/', LINUX_PATCHES_REPO_DIR+'/.buildbot/', dirs_exist_ok=True)
# get kernel branches from website
branches=get_branches()
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
        if i.startswith("10") or i.startswith("11") or i.startswith("12") or i.startswith("13") or i.startswith("14"):
            kernel_version=i.split("-")[1].split(".patch")[0]
            if web_branch == kernel_version:
                web_kernel=web_branch
    if web_kernel == 0:
        print("not found on linux-patches kernel.org version: " + web_branch)
        # start packages updating scripts
        os.system(SCRIPTS_DIR+"linux-patches/gkernel_up.sh")
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
        # explain what to do next
        print("check commits are ok and do: ")
        print("git checkout "+branch)
        print("git push origin "+branch)
        print("gpdorelease "+branch)
