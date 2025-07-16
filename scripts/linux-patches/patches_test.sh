#!/bin/bash

git_branch="$(git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3)"
echo "testing on branch $git_branch" 
./.buildbot/format.py "$git_branch" options.jinja > .buildbot/options
buildbot try --wait --repository=https://anongit.gentoo.org/git/proj/linux-patches.git

