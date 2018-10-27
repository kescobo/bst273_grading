#!/usr/bin/env python

import argparse
import pandas as pd
import os
import git
import logging

parser = argparse.ArgumentParser(description="A script to grade bst273 final projects")

parser.add_argument(
    "-i", "--project-folder",
    type=str, help="path to student folder",
    )

parser.add_argument(
    "-o", "--class-grades",
    type=str, help="grades table",
    )

parser.add_argument(
    "--append",
    action="store_true",
    help="append grade to table",
    )

parser.add_argument("-v", "--verbose", help="Display debug status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("--debug", help="set logging to debug", action="store_true")

parser.add_argument("-l", "--log",
    help="File path for log file")


args = parser.parse_args()

logpath = None
if args.log:
    logpath = os.path.abspath(args.log)
    if os.path.isdir(logpath):
        logpath = os.path.join(logpath, "grading.log")
else:
    logpath = ("grading.log")

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
fh = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
sh.setFormatter(formatter)
fh.setFormatter(formatter)

# set level based on args
if args.debug:
    sh.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
elif args.verbose:
    sh.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
elif args.quiet:
    sh.setLevel(logging.ERROR)
    fh.setLevel(logging.ERROR)
else:
    sh.setLevel(logging.WARNING)
    fh.setLevel(logging.WARNING)

logger.addHandler(sh) # add handler to logger
logger.addHandler(fh)

grades = pd.DataFrame({
    "name"             : "",
    "input"            : [0],
    "output"           : [0],
    "script"           : [0],
    "repo"             : [0],
    "repo_files"       : [0],
    "repo_match"       : [0],
    "rm_basic"         : [0],
    "rm_exp"           : [0],
    "rm_script"        : [0],
    "rm_modules"       : [0],
    "rm_input"         : [0],
    "rm_cmd"           : [0],
    "rm_output"        : [0],
    "rm_best"          : [0],
    "rm_worst"         : [0],
    "ex_help"          : [0],
    "ex_nostrat"       : [0],
    "ex_nostrat_valid" : [0],
    "ex_strat"         : [0],
    "ex_strat_valid"   : [0],
    "ex_axis"          : [0],
    "ex_legend"        : [0],
    "ex_default"       : [0],
    })

files = os.listdir(args.project_folder)
logging.debug("Files: {}".format(files))
