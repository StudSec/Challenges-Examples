from termcolor import colored
import subprocess
import traceback
import argparse
import pathlib
import json
import toml
import os

HOSTNAME = "127.0.0.1"

def allocate_port_generator():
    current = 4000
    while current < 5000:
        yield current
        current += 1
    raise Exception("Exhausted all ports.")
allocate_port = allocate_port_generator()


class Challenge:
    def __init__(self, path):
        self.path = path
        config = toml.load(path + "/challenge.toml")
        self.name = config["name"]
        self.uuid = config["uuid"]
        self.difficulty = config["difficulty"]
        self.flag = config["flag"]
        self.url = config["url"]
        self.points = config["points"]
        self.dynamic_flags = config.get("dynamic_flags", False)
        self.handouts = []

        self.port = 0
        if os.path.exists(self.path + "/Source/run.sh") or os.path.exists(self.path + "/Source/destroy.sh"):
            self.hosted = True
        else:
            self.hosted = False

        if self.hosted and args.check:
            if not os.path.exists(path + "/Source/destroy.sh"):
                print(self.name, colored("destroy.sh not found", "red"))
            if not os.path.exists(path + "/Source/run.sh"):
                print(self.name, colored("run.sh not found", "red"))

        for dirpath, dirnames, filenames in os.walk(path + "/Handout"):
            for filename in filenames:
                relative_path = os.path.relpath(str(os.path.join(dirpath, filename)), path + "/Handout")
                self.handouts.append(relative_path)

    def allocate_port(self):
        if self.hosted:
            self.port = str(next(allocate_port))


    def run(self):
        if not self.hosted:
            return

        if self.port == 0:
            self.port = str(next(allocate_port))
        subprocess.run(['/bin/sh', self.path + "/Source/run.sh",
                        "--hostname", HOSTNAME,
                        "--port", self.port,
                        "--flag", self.flag],
                       cwd=self.path + "/Source/",
                       capture_output=True)

    def test(self):
        if HOSTNAME == "0.0.0.0":
            host = '127.0.0.1'
        else:
            host = HOSTNAME

        result = subprocess.run(["python3", self.path + "/Tests/main.py",
                        "--flag", self.flag,
                        "--handout-path", self.path + "/Handout",
                        "--deployment-path", self.path + "/Source"
                        ] + [
            elem for item in self.url for elem in
            ("--connection-string", item.replace('{{PORT}}', self.port).replace('{{IP}}', host))
        ],
                       capture_output=True, text=True, cwd=self.path + "/Tests")
        if result.stderr:
            print(colored(f"Error while running tests for {self.name}", "red"))
            print(result.stderr)

        result = json.loads(str(result.stdout))

        output = ""
        all_ok = True
        for test in result:
            if not result[test] and not args.silent:
                output += test + " " + colored("OK", "green") + "\n"
            if result[test]:
                output += test + " " + colored(result[test], "red") + "\n"
                all_ok = False
        if all_ok:
            print(colored(self.name, "blue"), colored("OK", "green"))
            print(output, end="")
        else:
            print(colored(self.name, "blue"), colored("BAD", "red"))
            print(output, end="")


    def stop(self):
        if not self.hosted:
            return

        subprocess.run(['/bin/sh', self.path + "/Source/destroy.sh"], cwd=self.path + "/Source/",
                       capture_output=True)


class Category:
    def __init__(self, path):
        self.path = path
        config = toml.load(path + "/category.toml")
        self.challenges = []
        self.subcategories = []
        self.uuid = config["uuid"]
        self.banner = config.get("banner", "")
        self.name = config["name"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Challenge sanity checker")

    parser.add_argument("--challenges", action="store_true", help="List challenges")
    parser.add_argument("--categories", action="store_true", help="List categories")
    parser.add_argument("--check", action="store_true", help="Validate all challenges")
    parser.add_argument("--silent", action="store_true", help="Only print failing tests")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Interface to run challenges on")
    parser.add_argument("--flags", type=str, const="*", nargs='?', help="Dump flag(s)")
    parser.add_argument("--handouts", type=str, const="*", nargs='?', help="List handout(s) of challenge(s)")
    parser.add_argument("--run", type=str, const="*", nargs='?', help="run challenge(s)")
    parser.add_argument("--stop", type=str, const="*", nargs='?', help="stop challenge(s)")
    parser.add_argument("--test", type=str, const="*", nargs='?', help="test challenge(s)")

    args = parser.parse_args()
    HOSTNAME = args.host

    challenges = {}
    categories = {}
    for dirpath, dirnames, filenames in os.walk(pathlib.Path(__file__).parent.resolve()):
        # We don't want to try to parse challenge source, though this might be a bit overly aggressive
        if any(folder in dirpath for folder in ["/Source/", "/Handout/", "/Tests/"]):
            continue
        try:
            if "challenge.toml" in filenames:
                uuid = toml.load(dirpath + "/challenge.toml")["uuid"]

                if uuid in challenges.keys() or uuid in categories.keys():
                    if args.check:
                        print(colored(f"Duplicate uuid found: {uuid}", "red"))
                    continue

                challenges[uuid] = Challenge(dirpath)

                # Link to category
                category_uuid = toml.load(dirpath + "/../category.toml")["uuid"]
                categories[category_uuid].challenges.append(challenges[uuid])
            if "category.toml" in filenames:
                uuid = toml.load(dirpath + "/category.toml")["uuid"]

                if uuid in list(challenges.keys()) or uuid in list(categories.keys()):
                    if args.check:
                        print(colored(f"Duplicate uuid found: {uuid}", "red"))
                    continue

                categories[uuid] = Category(dirpath)

                # Link to upper category, if exists
                if os.path.isfile(dirpath + "/../category.toml"):
                    category_uuid = toml.load(dirpath + "/../category.toml")["uuid"]
                    categories[category_uuid].challenges.append(categories[uuid])
        except Exception as e:
            if args.check:
                print(colored(f"Error with {dirpath}", "red"))
                print(traceback.format_exc())

    # Allocate port in order of uuid
    for uuid in sorted(challenges.keys()):
        challenges[uuid].allocate_port()

    if args.challenges:
        for uuid in challenges:
            print(f"- {colored(uuid, 'blue')} {colored(challenges[uuid].name, 'white')}")
    if args.categories:
        for uuid in categories:
            print(f"- {colored(uuid, 'blue')} {colored(categories[uuid].name, 'white')}")
    if args.flags:
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.flags.split(",")) or args.flags == "*"):
                continue

            print(f"- {colored(challenges[uuid].name, 'blue')} {colored(challenges[uuid].flag, 'white')}")
    if args.handouts:
        for uuid in challenges:
            challenge = challenges[uuid]
            if not (any(item in challenge.name for item in args.handouts.split(",")) or args.handouts == "*"):
                continue

            if len(challenge.handouts):
                print(colored(challenge.name, "blue"))
                for file in challenge.handouts:
                    print(f"- {colored(file, 'white')}")
    if args.test:   # Add filter
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.test.split(",")) or args.test == "*"):
                continue
            challenges[uuid].run()
            challenges[uuid].test()
            challenges[uuid].stop()
    if args.run:    # Add filter
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.run.split(",")) or args.run == "*"):
                continue
            challenges[uuid].run()
    if args.stop:   # Add filter
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.stop.split(",")) or args.stop == "*"):
                continue
            challenges[uuid].stop()
