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
| - config.toml
| - docker-compose.yml
\ - README.md
```
*Note: not all folders are expanded, Challenge_2 and 3 are expected to have the same (base) structure as Challenge_1*

#### checker.py
Checker.py is the command line utility for a challenge repository, it contains the functionality to check and build
the challenge docker compose ...? TODO: we need a solution here that works both with an instancer and fixed,
with fixed ports are statically allocated for each challenge.

#### docker-compose

#### config.toml
- challenge_server hostname
- discord webhook

tl;dr we want to keep the possibility for both instancer and without instancer.

The webhook is used for notifying failed builds.

## Challenge format
```commandline
Source/
Handout/
Tests/
README.md
```
#### Source
This directory contains all the source files for the challenge, this is where the Dockerfile and any other
server hosted code should be.

#### Handout
This is what gets given to the contestants, all files in this folder are zipped and then distributed.

#### Tests
This folder contains at least one file called `main.py`, which contains the following function
```python
def run_test(url, handout_path, secret):
    pass
```
This function should then check
1) If the challenge is in good working order
2) If the deployed flag and the stored flag (pass as function parameter) match
3) All required handout files are present
4) Assert that all credentials/flags in the handout files are invalid

Should any of this not be the case a string should be returned *explicitly* describing the issue. If the
returned string is empty (or none is returned) the challenge is assumed to be in good working order.

*Note: it is recommended to concatenate all the errors to a string, and then return this string. This lists all the
issues initially and prevents the program from having to be constantly rerun.*

#### README.md
The challenge README contains all essential information for the challenge

## Category format
```commandline
Banner.png
README.md
```
#### README.md

#### Banner.png

## Checker.py
Document checker.py usage