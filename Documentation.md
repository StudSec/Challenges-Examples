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
|   |   |   |   | - run.sh
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
Checker.py is the command line utility for a challenge repository, it contains the functionality to check the validity
of the challenges, list different aspects of all challenges, test challenges and run challenges.

## Challenge format
```commandline
Source/
Handout/
Tests/
README.md
```
#### Source
This directory contains all the deployed source files for the challenge, this is where the Dockerfile and any other
server hosted code should be. This folder should contain a file `run.sh`, which starts the challenge container.

The file `run.sh` will be called as follows:
```shell
run.sh HOSTNAME PORT
```
Here the HOSTNAME is the hostname that will be provided to the players, this may be an IP or DNS address. PORT is the
port where the challenge is to be run, the invoking script bears the responsibility of the port being available. 
However, `run.sh` is responsible for ensuring the port is accessible on the provided hostname.

The HOSTNAME and PORT arguments may be a comma seperated list, should your challenge require multiple ports. For
example, the following challenge information table
```markdown
## Challenge information
| Difficulty  | Medium                     |
|-------------|----------------------------|
| points      | 150                        |
| flag        | CTF{test_flag}             |
| url         | http://{{IP}}:{{PORT}}/    |
| url         | ssh root@{{IP}} -p {{PORT}}|
```
Will result in `run.sh` being invoked with the following arguments. After which an HTTP service is expected to run on
`http://IP1:PORT1/` and an SSH service on `ssh root@IP2 -p PORT2`.
```shell
run.sh IP1,IP2 PORT1,PORT2
```

**Things to keep in mind when creating challenge deployments:**
- Use Docker for challenge deployment, under no circumstances should challenge code be run in the same user space as the 
host operating system.
- Resource limitations, try to limit the resources available to your Docker container to the minimum needed. For 
information on how to do this see https://docs.docker.com/engine/containers/resource_constraints/
- Use Docker compose, this is easier to read than an entire docker commandline.
- Avoid persistent data, if you use Docker volumes please mount them as read only (RO). Better yet, don't use Docker
volumes and simply copy the files into the container when building them.
- Limit the networks your Docker container has access to, not doing so can lead to unintended solutions in other
challenges. For more information on limiting the networks of a Docker container see 
https://docs.docker.com/engine/network/

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

Multiple connection strings are allowed, for more details see [Challenge format](#source)

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

A nesting level deeper than subcategories is not supported.

## Checker.py
```txt
--challenges
--categories
--flags
--handouts
--check
--generate
--run
--test
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

#### Run
Takes an optional argument, if present it attempts to run a challenge by this name. If none is found the command
fails, if the challenge is found and successfully started it returns a connection string to the challenge.

If no arguments are present it attempts to run all challenges. No connection string is given in this case.

#### Test
Exact same syntax as the `Run` command, however it will run tests on the provided challenge. If this no challenge
is specified all challenges will be tested. The results will be written to STDOUT.