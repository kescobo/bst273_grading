#!/usr/bin/env python

import argparse
import re
import pandas as pd
import os
import git
import logging
import filecmp
import shutil
from subprocess import call

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
    "--skip-input",
    action="store_true",
    help="Do not request user input for grades (useful for testing)",
    )

parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("-d", "--debug", help="set logging to debug", action="store_true")

parser.add_argument("-l", "--log",
    help="File path for log file")


args = parser.parse_args()

folder = os.path.abspath(args.project_folder)
if not os.path.isdir(folder):
    logger.error("Must pass a folder to --project-folder")
    raise IOError()

logpath = None
if args.log:
    logpath = os.path.abspath(args.log)
    if os.path.isdir(logpath):
        logpath = os.path.join(logpath, "grading.log")
else:
    logpath = (os.path.join(folder, "grading.log"))

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
fh = logging.FileHandler(logpath, mode="w")
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
    "name"             : ["out of"],
    "input"            : [4, 0],
    "output"           : [4, 0],
    "script"           : [10, 0],
    "repo"             : [2, 0],
    "repo_files"       : [6, 0],
    "repo_match"       : [2, 0],
    "rm_1"             : [1, 0],
    "rm_2"             : [1, 0],
    "rm_3"             : [2, 0],
    "rm_4"             : [1, 0],
    "rm_5"             : [2, 0],
    "rm_6"             : [2, 0],
    "rm_7"             : [2, 0],
    "rm_8"             : [1, 0],
    "rm_9"             : [1, 0],
    "ex_help"          : [4, 0],
    "ex_nostrat"       : [10, 0],
    "ex_nostrat_valid" : [20, 0],
    "ex_strat"         : [5, 0],
    "ex_strat_valid"   : [10, 0],
    "ex_axis"          : [2, 0],
    "ex_legend"        : [4, 0],
    "ex_default"       : [5, 0],
    "total"            : [100, 0]})


st_name = re.search(r"^([a-z]+)_?", os.path.basename(folder))
if st_name:
    st_name = st_name.group(1)
    logger.info("Starting to grade {}'s project".format(st_name))
    grades.at[1, "name"] = st_name
else:
    logger.error("Folder name invalid - must start with student name")
    raise IOError()

files = os.listdir(folder)
logger.debug("Files: {}".format(files))


## file testing

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
    grades.at[1, "script"] = 10
else:
    script = None

if find_file(files, r"^\w+.tsv$"):
    demo_input = os.path.join(folder, find_file(files, r"^\w+.tsv$"))
    logger.info("Found demo_input at {}".format(demo_input))
    grades.at[1, "input"] = 4
else:
    demo_input = None

if find_file(files, r"^\w+.(pdf|png)$"):
    demo_output = os.path.join(folder, find_file(files, r"^\w+.(pdf|png)$"))
    logger.info("Found demo_output at {}".format(demo_output))
    grades.at[1, "output"] = 4
else:
    demo_output = None

## README grading

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

if not args.skip_input:
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

        grades.at[1, "rm_{}".format(qn)] = score
else:
    logger.warning("Skipping README grading - complete manually")


## Execution testing

cmds = []
if 6 in readme_answers:
    for l in readme_answers[6].split('\n'):
        if re.search(r"python [ \w\-\.]+", l) and not re.search(r"python script_name\.py arguments", l):
            cmds.append(re.search(r"(python [ \w\-\.]+)", l).group(1).split())

if len(cmds) > 0:
    errors = False
    for cmd in cmds:
        c = call(cmd)
        if not c == 0:
            errors = True

    if errors:
        logger.warning("At least one listed command failed - check manually")
        logger.info("Commands: {}".format(cmds))
else:
    logger.warning("No demo commands found - check manually")

logger.debug(cmds)

if script:
    c = call(["python", script, "--help"])
    if c == 0:
        grades.at[1, "ex_help"] = 4

## Github

repo_path = os.path.join(folder, "git_repo")
if os.path.exists(repo_path):
    shutil.rmtree(repo_path)

os.mkdir(repo_path)

repo = git.Repo.init(repo_path)
origin = repo.create_remote("origin", "git@github.com:{}".format(repo_url))

if origin.exists():
    grades.at[1, "repo"] = 2

    repo.git.pull("origin", "master")

    repo_files = [f for f in map(lambda p: find_file(os.listdir(repo_path), p),
                        [r"(readme|README)", r"^\w+.py$", r"^\w+.tsv$", r"^\w+.(pdf|png)$"])]
    logger.debug(repo_files)
    repo_files_score = 6 * 4 / sum([f != None for f in repo_files])
    grades.at[1, "repo_files"] = repo_files_score

    diff = filecmp.cmpfiles(folder, repo_path, repo_files)
    logger.debug(diff)

    if diff[1] == repo_files:
        repo_match_score = 2
    else:
        repo_match_score = len(diff[1]) / sum([len(d) for d in diff])

    grades.at[1, "repo_match"] = repo_match_score

for g in list(grades):
    if grades.at[1, g] == 0 and not args.skip_input and not g == "total":
        score = input("What is the score for {}? : ".format(g))
        if type(score) == int:
            grades.at[1, g] = score
        else:
            logging.info("Score for {} staying 0".format(g))


logger.debug(grades)

grades.transpose(copy=True).to_csv(os.path.join(repo_path, "grades.tsv"), sep='\t')

if args.append and os.path.exists(args.class_grades):
    grades.to_csv(args.class_grades, mode="a", sep='\t', header=False)
else:
    grades.to_csv(args.class_grades, sep='\t')

if origin.exists():
    shutil.copy(logpath, os.path.join(repo_path, "grading.log"))
    repo.git.checkout("-b", "graded")

    repo.git.add(os.path.join(repo_path, "grades.tsv"))
    repo.git.add(os.path.join(repo_path, "grading.log"))
    repo.git.commit("-m", "add grades")
