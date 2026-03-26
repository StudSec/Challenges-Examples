# Repository layout

**TODO: needs to be updated**

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
