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

grade_fields = ["student_id", "subid", "input","output","script",
                "repo","repo_files","repo_match",
                "rm_1","rm_2","rm_3","rm_4","rm_5","rm_6","rm_7","rm_8","rm_9",
                "ex_help","ex_nostrat","ex_nostrat_valid","ex_strat","ex_strat_valid","ex_axis","ex_legend","ex_default",
                "total"]
grade_values = [0,0,4,4,10,2,
                6,2,1,
                1,2,1,2,2,2,1,1,
                4,10,20,5,10,2,4,5,
                100]


grades = pd.DataFrame(grade_values, columns=["outof"], index=grade_fields)

parse_folder = re.search(r"^([a-z]+)_(late_)?(\d+)_(\d+)", os.path.basename(folder))
logger.debug(parse_folder.groups)
if parse_folder:
    st_name = parse_folder.group(1)
    sid = int(parse_folder.group(3))
    subid = int(parse_folder.group(4))

    late = False
    if parse_folder.group(2):
        late = True

    logger.info("Starting to grade {}'s project".format(st_name))
    grades[st_name] = [0 for _ in range(len(grade_values))]
    grades.at["student_id", st_name] = sid
    grades.at["subid", st_name] = subid
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

if find_file(files, r"^[\w\.]+.py$"):
    script = os.path.join(folder, find_file(files, r"^[\w\.]+.py$"))
    logger.info("Found script at {}".format(script))
    grades.at["script", st_name] = 10
else:
    script = None

if find_file(files, r"^[\w\.]+.tsv$"):
    demo_input = os.path.join(folder, find_file(files, r"^[\w\.]+.tsv$"))
    logger.info("Found demo_input at {}".format(demo_input))
    grades.at["input", st_name] = 4
else:
    demo_input = None

if find_file(files, r"^[\w\.]+.(pdf|png)$"):
    demo_output = os.path.join(folder, find_file(files, r"^[\w\.]+.(pdf|png)$"))
    logger.info("Found demo_output at {}".format(demo_output))
    grades.at["output", st_name] = 4
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

        grades.at["rm_{}".format(qn), st_name] = score
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
        grades.at["ex_help", st_name] = 4

## Github

repo_path = os.path.join(folder, "git_repo")
if os.path.exists(repo_path):
    shutil.rmtree(repo_path)

os.mkdir(repo_path)

repo = git.Repo.init(repo_path)
origin = repo.create_remote("origin", "git@github.com:{}".format(repo_url))

if origin.exists():
    grades.at["repo", st_name] = 2

    repo.git.pull("origin", "master")

    repo_files = [f for f in map(lambda p: find_file(os.listdir(repo_path), p),
                        [r"(readme|README)", r"^[\w\.]+.py$", r"^[\w\.]+.tsv$", r"^[\w\.]+.(pdf|png|jpg)$"])]
    logger.debug(repo_files)
    repo_files_score = 6 * 4 / sum([f != None for f in repo_files])
    grades.at["repo_files", st_name] = repo_files_score

    repo_readme = os.path.join(repo_path, repo_files[0])
    repo_script = os.path.join(repo_path, repo_files[1])
    logger.debug(repo_readme)
    logger.debug(repo_script)

    repo_match_score = 0
    if filecmp.cmp(repo_readme, readme):
        repo_match_score += 1

    if filecmp.cmp(repo_script, script):
        repo_match_score += 1

    grades.at["repo_match", st_name] = repo_match_score

for g in grades.index:
    if grades.at[g, st_name] == 0 and not args.skip_input and not g == "total":
        score = input("What is the score for {} (out of {})? : ".format(g, grades.at[g, "outof"]))
        if score:
            score = int(score)
        else:
            score = 0
            logging.info("Leaving score for {} at 0".format(g))
        logger.debug(type(score))
        grades.at[g, st_name] = score

grades.at["total", st_name] = sum(grades.loc[grade_fields[2:-1], st_name])

logger.debug(grades)

grades.to_csv(os.path.join(repo_path, "grades.tsv"), sep='\t')

if args.append and os.path.exists(args.class_grades):
    gradesfile = pd.read_csv(args.class_grades, sep='\t')
    gradesfile[st_name] = grades[st_name]
    gradesfile.to_csv(args.class_grades, sep='\t')
else:
    grades.to_csv(args.class_grades, sep='\t')

if origin.exists():
    shutil.copy(logpath, os.path.join(repo_path, "grading.log"))
    repo.git.checkout("-b", "graded")

    repo.git.add(os.path.join(repo_path, "grades.tsv"))
    repo.git.add(os.path.join(repo_path, "grading.log"))
    repo.git.commit("-m", "add grades")
