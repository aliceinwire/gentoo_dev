#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import sys
from pathlib import Path

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
ROOT_DIR=os.path.dirname(os.path.realpath(__file__))+"/../"
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from gkernel_dev_cli.lib.git_helpers import save_repo
KPATCH_DIR=ROOT_DIR+"repos/kpatch/"
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
G_KPATCH_DIR=CURRENT_DIR+"/../"+"gentoo_repository/sys-kernel/kpatch/"
print("change dir to kpatch")


# download gentoo repository
save_repo("git@github.com:dynup/kpatch.git", KPATCH_DIR)

os.chdir(KPATCH_DIR)
os.system("git branch --show")
