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

parser.add_argument(
    "--skip-readme",
    action="store_true",
    help="Do not attempt grade README file (useful for testing)",
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
    "rm_1"             : [0],
    "rm_2"             : [0],
    "rm_3"             : [0],
    "rm_4"             : [0],
    "rm_5"             : [0],
    "rm_6"             : [0],
    "rm_7"             : [0],
    "rm_8"             : [0],
    "rm_9"             : [0],
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
    logger.error("Must pass a folder to --project-folder")
    raise IOError()

st_name = re.search(r"^([a-z]+)_?", os.path.basename(folder))
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
        m = re.search(pattern, f)
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

    parsed = re.compile(r"^(\d+)\.", re.MULTILINE).split(readme_content)
    answers = {}
    for i in range(len(parsed)):
        if re.search(r"^\d+$", parsed[i]):
            n = int(parsed[i])
            if n in answers:
                logging.warning("Two answers for README.md question {}. Skipping".format(n))
            else:
                a = parsed[i+1]
                m = re.search("ANSWER:([\S\s]+)", a)
                if m:
                    answers[n] = m.group(1)
                else:
                    answers[n] = a

    return answers

readme_answers = parse_readme(readme)
logger.debug(readme_answers)

q1 = readme_answers[1]
logger.debug(q1)
email = re.search(r"\b([\w\-\.]+@([\w\-]+\.)+[\w-]{2,4})\b", q1)
if email:
    email = email.group(1)
else:
    logger.warning("Couldn't find e-mail address")
    email = None

repo_url = re.search(r"github.com\/(\w+\/\w+(\.git)?)\b", q1)
if repo_url:
    repo_url = repo_url.group(1)
else:
    logger.warning("Couldn't find github repo url")
    repo_url = None

logger.debug(email)
logger.debug(repo_url)

if not args.skip_readme:
    for q in range(9):
        qn = q+1
        score = 0
        if qn in readme_answers:
            good = input(
                "\n ## Is the following answer reasonable for README Question {}? y/[n]\n{}: ".format(
                    qn, readme_answers[qn]))
            if good.lower() == "y" or good.lower() == "yes":
                if qn in [3,5,6,7]:
                    score = 2
                else:
                    score = 1
        else:
            logger.warning("Readme answer {} not found".format(qn))

        grades.at[0, "rm_{}".format(qn)] = score
else:
    logging.warning("Skipping README grading - complete manually")

logger.debug(grades)
