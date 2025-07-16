#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
import os
import sys
import subprocess

try_master = sys.argv[1]
try_username = sys.argv[2]
try_password = sys.argv[3]
try_who = sys.argv[4]
try_comment = sys.argv[5]

template_path = "options.jinja"
os.chdir("/home/arisut/gentoo_dev/linux-patches")
branch_name=subprocess.getoutput('git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3')
print("testing on branch "+branch_name)

templatedir = os.path.dirname(os.path.abspath(__file__))
templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template(template_path)
jobdict = {}
jobdict["branch_name"] = branch_name
jobdict["try_master"] = try_master
jobdict["try_username"] = try_username
jobdict["try_password"] = try_password
jobdict["try_who"] = try_who
jobdict["try_comment"] = try_comment
jobt = template.render(jobdict)
print("")
print(jobt)
# ./.buildbot/format.py "$git_branch" options.jinja > .buildbot/options

with open('.buildbot/options', mode='w') as f:
    f.write(jobt)
os.system("buildbot try --repository=https://anongit.gentoo.org/git/proj/linux-patches.git")
