# Documentation
This file explains the standards used in this repository, as well as further tips and advice.

## Repository layout
Here is an example challenge repository layout, all folder and filenames in this document are case-insensitive. 
However, it is recommended to follow the casing outlined here, should two paths be case-identical (eg Test/ and test/)
then it is not defined which will be chosen.
```
.
| - Category_1/
|   | - Subcategory_1/
|   |   | - Challenge_1/
|   |   |   | - Handout/
|   |   |   |   \ challenge.c
|   |   |   | - Source/
|   |   |   |   | - run.sh
|   |   |   |   | - destroy.sh
|   |   |   |   | - Dockerfile
|   |   |   |   \ - challenge.c
|   |   |   | - Tests/
|   |   |   |   \ main.py
|   |   |   | - Build/
|   |   |   |   \ build.sh
|   |   |   | - challenge.toml
|   |   |   | - Description.md
|   |   |   \ - README.md
|   |   | - Description.md  
|   |   | - category.toml
|   |   \ - README.md
|   | - Subcategory_2/
|   |   | - Challenge_2/
|   |   \ - README.md
|   | - Challenge_3/
|   | - Banner.png
|   \ - README.md
| - checker.py
| - config.toml
\ - README.md
```
*Note: not all folders are expanded, Challenge_2 and 3 are expected to have the same (base) structure as Challenge_1*

#### checker.py
Checker.py is the command line utility for a challenge repository, it contains the functionality to check the validity
of the challenges, list different aspects of all challenges, test challenges and run challenges.

#### config.toml
This file is optional, and is only required when not running the challenge from an instancer. This file should contain:
- The base name of the hosting server. This will be passed as the `{{IP}}` parameter in a challenge connection string.
- A slack-compatible webhook URL, this is optional but errors will be reported to this endpoint.

## Challenge format
```commandline
Source/
Handout/
Tests/
Build/
README.md
challenge.toml
Description.md
```
#### Source
This directory contains all the deployed source files for the challenge, this is where the Dockerfile and any other
server hosted code should be. This folder should contain a file `run.sh`, which starts the challenge container.

The file `run.sh` will be called as follows:
```shell
run.sh --hostname HOSTNAME --port PORT --flag FLAG --team TEAM_UUID
```
Here the HOSTNAME is the hostname that will be provided to the players, this may be an IP or DNS address. PORT is the
port where the challenge is to be run, the invoking script bears the responsibility of the port being available. 
However, `run.sh` is responsible for ensuring the port is accessible on the provided hostname. The FLAG parameter
is the desired flag (to support dynamic flags), run.sh should output the actual flag the instance is running with on 
stdout. The team parameter is optional, but may be used to deploy multiple instances of the same challenge.

The HOSTNAME and PORT arguments may be a comma separated list, should your challenge require multiple ports. For
example, the following challenge.

```toml
[621f2fc7-1ab9-4b50-914d-991be464e943]
name = "Hard challenge"
difficulty = "hard"
flag = {"CTF{A_Very_Hard_Challenge}" = 500}
url = ["http://{{IP}}:{{PORT}}/", "ssh root@{{IP}} -p {{PORT}}"]
```
Will result in `run.sh` being invoked with the following arguments. After which an HTTP service is expected to run on
`http://IP1:PORT1/` and an SSH service on `ssh root@IP2 -p PORT2`.
```shell
run.sh IP1,IP2 PORT1,PORT2
```

The folder should also contain a file `destroy.sh` that ensures the deployment is destroyed. The script
should exit silently with code 0 if a deployment is successfully destroyed, and print any
errors and information otherwise. The `destroy.sh` should also accept an optional team parameter, which can be
used to destroy a specific instance.

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

#### Build
This folder contains all files needed to build the challenge. The folder should contain at least a `build.sh` file
which takes two arguments `--source-path`, `--handout-path` and `--flag`. The script should build the challenge (eg, 
compile a binary) and place these at the `--source-path` and `--handout-path` location. Should this not be required
the script should just exit with status code `0`.

#### Tests
This folder contains at least one file called `main.py`, which is based on the following template
```python
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the test with specified arguments.")

    parser.add_argument("--flag", type=str, required=True, help="The flag to run the test.")
    parser.add_argument("--connection-string", type=str, required=True, action='append',
                        help="The connection string in the form: \"<ip/hostname> <port>\"" +
                        "an example includes: --connection-string \"localhost 1337\" or" +
                        "--connection-string \"172.18.0.1 6564\"")
    parser.add_argument("--handout-path", type=str, required=True, help="The path" +
    " the /Handout dir of the challenge.")
    parser.add_argument("--deployment-path", type=str, required=True, help="The " +
    "path to the /Source directory of this challenge.")

    parser.add_argument("--force-reusability", type=str, required=False, help="This " +
    "flag is used when testing the challenge before it is given to the player."
    "After test is run with this flag, no artifacts should be left around"
    "that can affect the players experience")
    args = parser.parse_args()

    print(json.dumps(
        run_test(
            flag=args.flag,
            connection_string=args.connection_string,
            handout_path=args.handout_path,
            deployment_path=args.deployment_path,
        )
    ))

```
- flag: the flag registered in the system as the 'correct' one
- connection_string: Connection information for a deployed instance, as specified in the challenge README.md
- handout_path: path to a folder containing the handout
- deployment_path: path to a folder/mount containing the files deployed
- force-reusability: a flag that can be set to indicate the challenge will be handed directly to the player after 
testing. This should mean that no unintended artifacts are left on the challenge.

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
The README contains an informal overview of the challenge, including any important deployment information, design notes
and other considerations. This may contain sensitive information.

#### Description.md
The Description is the **public** challenge information, it contains a short description of the challenge. It does not
have to contain any connection information, this is stored in the challenge.toml file. **This file should not contain
any sensitive information**

### challenge.toml
This file contains all the challenge metadata, including:
- UUIDv4 -> This is the header
- Challenge name
- Difficulty
- Flag -> This is a dictionary that includes the amount of points for that flag
- Connection string, supports the following wildcards ({{HOST}}, {{PORT}})
- if dynamic flags are supported (this is an optional field, the absence will be considered as "False")

Multiple connection strings are allowed, for more details see [Challenge format](#source)

Multiple challenges are allowed in the same challenge.toml file, in this case the challenges are seen as multiple
subchallenges (eg, first getting code execution and the getting root), here the order that the challenges are declared
is respected.

For example:
```toml
[621f2fc7-1ab9-4b50-914d-991be464e943]
name = "Easy pwn"
difficulty = "easy"
flag = {"CTF{Easy_pwn_challenge}" = 50}
url = ["{{IP}}:{{PORT}}"]
dynamic_flags = true

[e743afe9-44a7-482f-998d-0f4151acad64]
name = "Easy pwn revenge"
difficulty = "easy"
flag = {"CTF{Easy_easy_pwn_challenge}" = 50, "CTF{Revenge_pwn_challenge}" = 100}
url = ["{{IP}}:{{PORT}}"]
```

## Category format
A category contains at least the following files.
```commandline
README.md
Description.md
category.toml
Banner.png
```

#### README.md
The README contains an informal description of the (sub) category. For example:
```markdown
## PWN
The world of low level exploitation!
```

#### Description.md
The public description of the category, this is what players will see.

#### category.toml
Contains the following information:
- name
- uuid
- Path to banner image (optional)

An example toml file would be
```toml
name = "example category"
banner = "Banner.png"
uuid = "84c988fa-9f42-42c7-b28a-8202b0962798"
```

#### Banner.png
This is the banner image for the category, a 1024x1024 PNG image is recommended. The file name is not fixed, but
instead has to be pointed to by `category.toml`

## Checker.py
```txt
--challenges
--categories
--flags
--handouts
--check
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

#### Run
Takes an optional argument, if present it attempts to run a challenge by this name. If none is found the command
fails, if the challenge is found and successfully started it returns a connection string to the challenge.

If no arguments are present it attempts to run all challenges. No connection string is given in this case.

When running the challenges the port range `4000-4999` will be used to allocate ports to each challenge. The order
of port allocation is done sequentially, sorted by uuid.

#### Test
Exact same syntax as the `Run` command, however it will run tests on the provided challenge. If this no challenge
is specified all challenges will be tested. The results will be written to STDOUT.
