# Challenges

Below, we go through the challenge format, including the structure of the challenge, the expected files, and the
expected content of these files.

## Challenge Format

A challenge should have at least the following files and directories:

* [`challenge.toml`](#challengetoml) is a TOML file that contains all the metadata for the challenge.
* [`README.md`](#readmemd) is a markdown file that contains an informal overview of the challenge;
* [`Source/`](#source-directory), which contains all the source files for the challenge;
* [`Handout/`](#handout-directory), which contains all the files that are given to the contestants;

Additionally, `Tests/` and/or `Build/` directories may be present, where the [`Tests/`](#tests-directory) directory
contains any tests for the challenge, and the [`Build/`](#build-directory) directory contains any build scripts for the
challenge.

The challenge directory itself should be put in a category directory of the desired category, see
[Categories](repo.md) for more detail.

### challenge.toml

The `challenge.toml` file describes all the needed metadata for the challenge, for both the running and presenting of
the challenge. The following fields are supported in the `challenge.toml` file:

##### UUID

The first line of the `challenge.toml` file should be a UUIDv4, as this is used to uniquely identify the challenge. On
linux, you can generate a random UUIDv4 with the command `uuidgen`.

```toml
[5da55141-2f35-4822-91b5-fd28e1686d09]
# rest of file
```

##### Name

The name of the challenge, this is what will be displayed to the contestants on the CTF platform.

```toml
name = "Example Challenge"
```

##### Flag

The flag for the challenge, with an assigned static point value.

```toml
flag = { "FLAG{example_flag}" = 100 }
```

##### Difficulty

The difficulty of the challenge, usually limited to "easy", "medium", and "hard".

```toml
difficulty = "medium"
```

##### Description

The description of the challenge, this is what will be displayed to the contestants on the CTF platform.

```toml
description = """Example description line1
Example description line 2"""
# or
description = """Example description single line"""
```

##### URL

The connection string of the challenge, as e.g. `http://{{IP}}:{{PORT}}` or `nc {{IP}} {{PORT}}`. It should contain
`{{IP}}` and `{{PORT}}` placeholders that will be replaced with the actual IP or URL and port when the challenge is run.

**Optional** The URL field should be omitted if the challenge doesn't need to be run.

```toml
url = "http://{{IP}}:{{PORT}}"
```

##### Instanced

A boolean value indicating whether the challenge is instanced.

**Optional** This field should be omitted if the challenge is not instanced, and and defaults to `false`.
challenge is instanced.

```toml
instanced = true
```

##### Hints

A list of hints for the challenge with their point cost, shown on the CTF platform.

**Optional** If omitted, no hints will be shown for the challenge.

```toml
hints = { "Example hint 1" = 10, "Example hint 2" = 20 }
```

##### Hidden

A boolean value indicating whether the challenge is hidden. Hidden challenges are not shown to contestants on the CTF platform,
but are still deployed.

**Optional** This field should be omitted if the challenge is not hidden, and defaults to `false`.

```toml
hidden = true
```

##### Dynamic Flag

TODO

**Optional** Defaults to `false`.

```toml
dynamic_flag = true
```

##### Tags

A list of tags for the challenge, shown on the CTF platform.

**Optional** If omitted, no tags will be shown for the challenge.

```toml
tags = ["example"]
```

#### Example challenge.toml

```toml
[1457f303-0894-42c9-bd06-484e92d8fc5d]
name = "Example"
flag = { "FLAG{example_flag}" = 100 }
difficulty = "medium"
description = '''
This is an example challenge.
'''
url = "nc {{IP}} {{PORT}}"
instanced = true
hints = { "Try harder" = 10 }
# hidden, dynamic_flag, and tags are omitted in this example
```

### README.md

The README contains an informal overview of the challenge, including any important deployment information, design notes,
high-level solution, and other considerations. This may contain sensitive information.

### Source Directory

This directory contains all the needed source files for the challenge, this is where the Dockerfile and any other server
hosted code should be.

#### Default Deployment

By default, the `checker.py` program will attempt to build, run, and destroy the challenge purely off the Dockerfile in
the source folder. This means that, if your challenge has a `Dockerfile` that works with a simple `docker build` and
`docker run` command, you don't need to add any additional scripts to the source folder, and the `checker.py` will
handle the deployment for you based on the format specified in the `challenge.toml`.

Of course, as specified in the [challenge.toml](#challengetoml) section, if your challenge doesn't need to be run then
you just omit the `url` field in the `challenge.toml` file.

#### Additional deployment configuration

However, if you require additional deployment configuration, you can add two scripts to the source folder, `run.sh` and
`destroy.sh`.

##### run.sh

The `run.sh` should be a shell script that handles the running of the challenge. The `run.sh` script is called as
follows:

```shell
run.sh --hostname HOSTNAME --port PORT --flag FLAG --registry REGISTRY
```

###### HOSTNAME

`HOSTNAME` is the hostname that will be provided to the players, this may be an IP or DNS address.

###### PORT

`PORT` is the port where the challenge is to be run. Note that, whilst the invoking `checker.py` bears the
responsibility of the port being available, `run.sh` is responsible for ensuring the port is accessible on the provided
hostname.

###### FLAG

`FLAG` is an optional argument that passes the flag specified in the `challenge.toml` to the `run.sh` script, this can
be used to deploy dynamic flags. If your challenge does not support dynamic flags, you can simply ignore this argument
and deploy the static flag as specified in the `challenge.toml`.

###### REGISTRY

`REGISTRY` is a docker registry that should be used to push any built images to, in case docker service is supported.

#### destroy.sh

The `destroy.sh` is a shell script that ensures the deployment is destroyed. The script should exit silently with code 0
if a deployment is successfully destroyed, and print any errors and throw a tantrum otherwise.

### Handout Directory

This is what gets given to the contestants, all files in this folder are zipped and then distributed.

### Build Directory

TODO

### Tests Directory

TODO
