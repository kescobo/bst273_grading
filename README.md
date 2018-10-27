# Grading script for BST273

## Rubric

index            | Section        | Component                 | Points
-----------------|----------------|---------------------------|-------
input            | Files included | Sample input              | 4
output           | Files included | Sample output             | 4
script           | Files included | script                    | 10
repo             | Github         | Github repo exists        | 2
repo_files       | Github         | Github includes all files | 6
repo_match       | Github         | Files match               | 2
rm_1             | README         | 1 - name/email/github     | 1
rm_2             | README         | 2 - experience            | 1
rm_3             | README         | 3 - description of script | 2
rm_4             | README         | 4 - module list           | 1
rm_5             | README         | 5 - description of input  | 2
rm_6             | README         | 6 - sample commands       | 2
rm_7             | README         | 7 - description of output | 2
rm_8             | README         | 8 - best part of class    | 1
rm_9             | README         | 9 - worst part of class   | 1
ex_help          | Execution      | Reasonable --help menu    | 4
ex_nostrat       | Execution      | Can make no-strat plot    | 10
ex_nostrat_valid | Execution      | Valid no-strat plot       | 20
ex_strat         | Execution      | Can make strat plot       | 5
ex_strat_valid   | Execution      | Valid strat plot          | 10
ex_axis          | Execution      | Axis labels included      | 2
ex_legend        | Execution      | Legend in strat mode      | 4
ex_default       | Execution      | Default file name         | 4

## Script tests

1. Files included
    1. Is there a `scatter.py` file? -- +10
    2. Is there a sample input (`*.tsv`)? -- +4
    3. Is there a sample output (`*.png` or `*.pdf`)? -- +4
2. README File
    1. Attempt to extract sample commands to test `Execution`
    2. Does it include name, e-mail and github link? -- +1
    3. Answers to all questions? +13
3. Github
    1. Assuming a git url was found, clone it. On success -- +2
    2. Check files included as in `#1` -- +6
    1. Files match -- +2
1. Execution
    1. Help menu -- +4
    2. scripts run without errors

## Manual inspection

1. Can make plots
    1. No-strat -- +10
    2. Strat -- +5
2. Default file name -- +4
3. Plots are valid
    1. No-strat -- +20
    2. Strat -- +10
4. Axis labels -- +2
5. Legend on strat -- +4
6. Any errors / points missed by script

## To run
