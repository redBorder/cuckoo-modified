#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os.path
import sys
import time

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from lib.cuckoo.core.database import Database, TASK_PENDING, TASK_RUNNING
from lib.cuckoo.core.database import TASK_COMPLETED, TASK_RECOVERED, TASK_REPORTED
from lib.cuckoo.core.database import TASK_FAILED_ANALYSIS, TASK_FAILED_PROCESSING, TASK_FAILED_REPORTING

def main():
    db = Database()

    states = (
        TASK_PENDING, TASK_RUNNING,
        TASK_COMPLETED, TASK_RECOVERED, TASK_REPORTED,
        TASK_FAILED_ANALYSIS, TASK_FAILED_PROCESSING, TASK_FAILED_REPORTING
    )
    
    print db.count_tasks(TASK_RUNNING)

if __name__ == "__main__":
    main()
