#!/usr/bin/env python

import argparse
import re
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

parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("-d", "--debug", help="set logging to debug", action="store_true")

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
    logger.setLevel(logging.DEBUG)
elif args.verbose:
    logger.setLevel(logging.INFO)
elif args.quiet:
    logger.setLevel(logging.ERROR)
else:
    logger.setLevel(logging.WARNING)

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

folder = os.path.abspath(args.project_folder)
if not os.path.isdir(folder):
    logger.error("Must pass a folder name to --project-folder")
    raise IOError()

st_name = re.match(r"^([a-z]+)_?", os.path.basename(folder))
if st_name:
    st_name = st_name.group(1)
    logger.info("Starting to grade {}'s project".format(st_name))
    grades.at[0, "name"] = st_name
else:
    logger.error("Folder name invalid - must start with student name")
    raise IOError()

files = os.listdir(folder)
logger.debug("Files: {}".format(files))


# file testing
def find_file(file_list, pattern):
    for f in file_list:
        m = re.match(pattern, f)
        if m:
            return f

    return None


if find_file(files, r"(readme|README)"):
    readme = os.path.join(folder, find_file(files, r"(readme|README)"))
    logger.info("Found README at {}".format(readme))
else:
    logger.error("No README found in {}. Must check manually".format(folder))
    raise ValueError()

if find_file(files, r"^\w+.py$"):
    script = os.path.join(folder, find_file(files, r"^\w+.py$"))
    logger.info("Found script at {}".format(script))
    grades.at[0, "script"] = 10
else:
    script = None

if find_file(files, r"^\w+.tsv$"):
    demo_input = os.path.join(folder, find_file(files, r"^\w+.tsv$"))
    logger.info("Found demo_input at {}".format(demo_input))
    grades.at[0, "input"] = 4
else:
    demo_input = None

if find_file(files, r"^\w+.(pdf|png)$"):
    demo_output = os.path.join(folder, find_file(files, r"^\w+.(pdf|png)$"))
    logger.info("Found demo_output at {}".format(demo_output))
    grades.at[0, "output"] = 4
else:
    demo_output = None


def parse_readme(readme_path):
    with open(readme_path) as rm:
        readme_content = rm.read()

    parsed = re.compile(r"\n(\d+)\.").split(readme_content)
    answers = {}
    for i in range(len(parsed)):
        if re.match(r"^\d+$", parsed[i]):
            n = int(parsed[i])
            if n in answers:
                logging.warning("Two answers for README.md question {}. Skipping".format(n))
            else:
                a = parsed[i+1]
                m = re.match("ANSWER:([\S\s]+)")
                answers[n] = m.captures[1]

    return answers

readme_answers = parse_readme(readme)



logger.debug(grades)
