# TODO: have hooks that allow the script to work without the libraries installed
from termcolor import colored
import subprocess
import argparse
import re
import os


def isolate_markdown_category(lines, header):
    index = lines.index(header) + 1
    for line in lines[lines.index(header) + 1:]:
        if line.startswith("##"):
            return lines[lines.index(header) + 1:index]
        index += 1

    # Reached end of file
    return lines[lines.index(header) + 1:]


def parse_markdown_challenge(path):
    ret = {"url": "Null"}
    with open(path, "r") as f:
        lines = f.readlines()

    try:
        ret["description"] = ''.join(isolate_markdown_category(lines, "## Description\n"))
        challenge_information = isolate_markdown_category(lines, "## Challenge information\n")

        if not challenge_information:
            raise ValueError

        for line in challenge_information:
            try:
                key = line.split("|")[1].strip().lower()
            except IndexError:
                continue
            # We want to skip over the ------ line
            if key != len(key) * key[0]:
                ret[key] = line.split("|")[2].strip()
    except ValueError:
        pass
    if not all(x in ret.keys() for x in ["description", "flag", "points", "subcategory", "difficulty"]):
        print(colored(f"{path} doesn't contain all required challenge information, skipping", "red"))
        return {}

    return ret


def parse_markdown_category(path):
    ret = {}

    with open(path, "r") as f:
        lines = f.readlines()

    subcategories = [line for line in lines if "#### " in line]
    try:
        for category in subcategories:
            ret[category[5:].strip()] = "\n".join(isolate_markdown_category(lines, category))

        # Get main category description
        ret[path.split("/")[-2]] = "\n".join(isolate_markdown_category(lines, lines[0]))
    except ValueError:
        pass

    return ret, path.split("/")[-2]


def print_categories():
    for category in [x for x in os.listdir(f"./")
                     if os.path.isdir(f"./{x}")]:
        if os.path.exists(f"./{category}/README.md"):
            cat, name = parse_markdown_category(f"./{category}/README.md")
            print(colored(name, "magenta"))
            for subcat in cat:
                print("-", colored(subcat, "blue"), cat[subcat].rstrip())


def print_challenges():
    with open(f"README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            if challenge.endswith("README.md"):
                challenge = challenge.replace("%20", " ").replace("./", "")

                print(colored(challenge.split("/")[1], "magenta"))
                for k, v in parse_markdown_challenge(challenge).items():
                    print("-", colored(k, "blue"), v.rstrip())
                print("-", colored("Handout", "blue"), os.path.exists(challenge[:-9] + "Handout"))

            else:
                print(colored("Invalid challenge:", "red"), challenge)


def print_flags(output=True):
    flags = []
    with open(f"README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            try:
                if challenge.endswith("README.md"):
                    challenge = challenge.replace("%20", " ").replace("./", "")
                    if output:
                        print("{:40}".format(colored(challenge.split("/")[1], "magenta")),
                              parse_markdown_challenge(challenge)["flag"])
                    flags.append(parse_markdown_challenge(challenge)["flag"])
            except KeyError:
                print(colored("Invalid challenge:", "red"), challenge)
    return flags


def print_handouts():
    with open(f"README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            try:
                if challenge.endswith("README.md"):
                    challenge = challenge.replace("%20", " ").replace("./", "")

                    if os.path.exists(challenge[:-9] + "Handout"):
                        print(colored(challenge.split("/")[1], "magenta"))
            except KeyError:
                print(colored("Invalid challenge:", "red"), challenge)


def check():
    with (open(f"README.md") as f):
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            if challenge.endswith("README.md"):
                challenge = challenge.replace("%20", " ").replace("./", "")
                challenge_data = parse_markdown_challenge(challenge)
                if not os.path.exists('/'.join(challenge.split("/")[:-1]) + "/Writeup.md"):
                    print(colored("Missing writeup:", "red"), challenge)
                if challenge_data["subcategory"] not in \
                        parse_markdown_category(str('/'.join(challenge.split("/")[:-2]) + "/README.md"))[0]:
                    print(colored("Undefined subcategory:", "red"),
                          challenge_data["subcategory"], "in", colored(challenge, "blue"))
            else:
                print(colored("Invalid challenge:", "red"), challenge)

    # NOTE: here we assume that the number of files will not exceed POSIX ARG_MAX
    flags = print_flags(output=False)
    args = ['grep', '-r']
    for f in flags:
        args.append('-e')
        args.append(f)

    result = subprocess.run(args, capture_output=True, text=True, check=True)
    if "Handout" in result.stdout:
        print(colored("Warning: flag found in challenge handout", "red"), colored(result.stdout, "blue"))


def check_orphan():
    with open(f"README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for file in os.listdir("."):
            if file.endswith("README.md") and file not in matches and file != "README.md":
                print(colored("Orphaned challenge:", "red"), file)


def main():
    parser = argparse.ArgumentParser(description="Challenge sanity checker")

    parser.add_argument("--challenges", action="store_true", help="List challenges")
    parser.add_argument("--categories", action="store_true", help="List categories")
    parser.add_argument("--flags", action="store_true", help="Dump flags")
    parser.add_argument("--handouts", action="store_true", help="List challenges with handouts")
    parser.add_argument("--check", action="store_true", help="Validate challenges")
    parser.add_argument("--orphan", action="store_true", help="Check for dangling/orphaned challenges")

    args = parser.parse_args()

    if args.challenges:
        print_challenges()
    elif args.categories:
        print_categories()
    elif args.flags:
        print_flags()
    elif args.handouts:
        print_handouts()
    elif args.check:
        check()
    elif args.orphan:
        check_orphan()


if __name__ == "__main__":
    main()
