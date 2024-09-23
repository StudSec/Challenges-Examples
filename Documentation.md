# Documentation
This file explains the standards used in this repository, as well as further tips and advice.

## Repository layout
The challenge repository contains the following layout
```
.
| - Category_1/
|   | - Subcategory_1/
|   |   | - Challenge_1/
|   |   |   | - Handout/
|   |   |   |   \ challenge.c
|   |   |   | - Source/
|   |   |   |   | - Dockerfile
|   |   |   |   \ - challenge.c
|   |   |   | - Tests/
|   |   |   |   \ main.py
|   |   |   \ - README.md
|   |   \ - README.md
|   | - Subcategory_2/
|   |   | - Challenge_2/
|   |   \ - README.md
|   | - Challenge_3/
| - checker.py
\ - README.md
```
*Note: not all folders are expanded, Challenge_2 and 3 are expected to have the same (base) structure as Challenge_1*

#### checker.py
Checker.py is the command line utility for a challenge repository, it contains the functionality to check and build
the challenge docker compose ...? TODO: we need a solution here that works both with an instancer and fixed,
with fixed ports are statically allocated for each challenge.

## Challenge format
```commandline
Source/
Handout/
Tests/
README.md
```
#### Source
This directory contains all the deployed source files for the challenge, this is where the Dockerfile and any other
server hosted code should be.

#### Handout
This is what gets given to the contestants, all files in this folder are zipped and then distributed.

#### Tests
This folder contains at least one file called `main.py`, which contains the following function
```python
def run_test(flag, connection_string=None, handout_path=None, deployment_path=None):
    pass
```
- flag: the flag registered in the system as the 'correct' one
- connection_string: Connection information for a deployed instance, as specified in the challenge README.md
- handout_path: path to a folder containing the handout
- deployment_path: path to a folder/mount containing the files deployed

This function should then check
1) If the challenge is in good working order (DEPLOYMENT_WORKING)
2) If the deployed flag and the stored flag (pass as function parameter) match (FLAG_CORRECT)
3) All required handout files are present, and match the deployment (HANDOUT_CORRECT)
4) Assert that all credentials/flags in the handout files are invalid (DUMMY_SECRET)

Once all tests are complete the function should return the following dictionary describing each test run and the result.
An empty result string is interpreted as the test passing. A non-empty result string is interpreted as a failing test,
and should be verbose enough to allow a user to solve the issue. If a key is not present, the checker will assume that
aspect was not tested.

An example return dictionary would be:
```python
return {
    "DEPLOYMENT_WORKING": "",
    "FLAG_CORRECT": "Flag does not match",
    "HANDOUT_CORRECT": "Missing rsa.pub",
    "DUMMY_SECRET": "Admin password in deployment"
}
```


#### README.md
The challenge README contains all essential information for the challenge, this includes:
- Name, the first line of the file starting with "## ". This is followed by a high level summary of the challenge
- Description, the description that will be presented to the CTF players.
- Challenge information, a markdown table that contains the following information: 
  - Difficulty (Easy, Medium, Hard)
  - Point count
  - Flag
  - Connection string, supports the following wildcards ({{IP}}, {{PORT}}, {{DNS}})

For example:
```markdown
## A medium PWN challenge
This part contains an unofficial description. Won't be displayed to the end user.

## Description
A decent pwn challenge. This description will be given to the user

## Challenge information
| Difficulty  | Medium                    |
|-------------|---------------------------|
| points      | 150                       |
| flag        | CTF{Medium_pwn_challenge} |
| url         | {{IP}}:{{PORT}}           |
```

## Category format
#### Main category
A main category contains the following files, in addition to challenges and subcategories.
```commandline
Banner.png
README.md
```

**README.md**
The README contains the category name on the first line starting with "## " and a mandatory description. For example:
```markdown
## PWN
The world of low level exploitation!
```

**Banner.png**
A 1024x1024 png image, used as the banner for the category.

#### Subcategory
A subcategory does not contain a `Banner.png`, but does contain a `README.md` in a simular format. For example:
```markdown
## Buffer overflows
<optional description>
```

subsubcategories are not supported.

## Checker.py
C
```txt
--challenges
--categories
--flags
--handouts
--check
--generate
```

#### Challenges
Lists all challenges present in the repository.

#### Categories
Lists all main and sub categories present in the repository.

#### flags
Lists all flags for all challenges present in the repository.

#### Handouts
Lists all handouts for all relevant challenges present in the repository.

#### Check
Ensures all challenges are properly formatted.

#### Generate
Generates the root level README.md which contains a link to all challenges grouped by (sub) category.