# Grading script for BST273

## Rubric

Section        | Component                 | Points
---------------|---------------------------|-------
Files included | Sample input              | 4
Files included | Sample output             | 4
Files included | script                    | 10
Github         | Github repo exists        | 2
Github         | Github includes all files | 6
Github         | Files match               | 2
README         | 1 - name/email/github     | 1
README         | 2 - experience            | 1
README         | 3 - description of script | 2
README         | 4 - module list           | 1
README         | 5 - description of input  | 2
README         | 6 - sample commands       | 2
README         | 7 - description of output | 2
README         | 8 - best part of class    | 1
README         | 9 - worst part of class   | 1
Execution      | Reasonable --help menu    | 4
Execution      | Can make no-strat plot    | 10
Execution      | Valid no-strat plot       | 20
Execution      | Can make strat plot       | 5
Execution      | Valid strat plot          | 10
Execution      | Axis labels included      | 2
Execution      | Legend in strat mode      | 4
Execution      | Default file name         | 4

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
    2. Can make plots
        1. No-strat -- +10
        2. Strat -- +5
    1. Default file name -- +4

## Manual inspection

1. Plots are valid
    1. No-strat -- +20
    2. Strat -- +10
1. Axis labels -- +2
1. Legend on strat -- +4
2. Any errors / points missed by script

## To run
