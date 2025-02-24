from termcolor import colored
import subprocess
import traceback
import argparse
import requests
import pathlib
import json
import toml
import sys
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
    def __init__(self, path, uuid):
        self.path = path
        config = toml.load(path + "/challenge.toml")
        self.name = config[uuid]["name"]
        self.uuid = uuid
        self.difficulty = config[uuid]["difficulty"]
        self.flag = config[uuid]["flag"]
        self.url = config[uuid]["url"]
        self.dynamic_flags = config.get("dynamic_flags", False)
        self.handouts = []

        self.port = None
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
        subprocess.run(['/bin/bash', self.path + "/Source/run.sh",
                        "--hostname", HOSTNAME,
                        "--port", self.port] +
                        sum([['--flag', z] for z in self.flag.keys()], []),
                       cwd=self.path + "/Source/",
                       stdout=sys.stdout,
                       stderr=sys.stderr)

    def test(self):
        if HOSTNAME == "0.0.0.0":
            host = '127.0.0.1'
        else:
            host = HOSTNAME

        result = subprocess.run(["python3", self.path + "/Tests/main.py"] + sum([['--flag', z] for z in self.flag.keys()], []) + ["--handout-path", self.path + "/Handout",
                        "--deployment-path", self.path + "/Source"
                        ] + [
            elem for item in self.url for elem in
            ("--connection-string", item.replace('{{PORT}}', self.port).replace('{{IP}}', host))
        ], capture_output=True, text=True, cwd=self.path + "/Tests")
        if result.stderr:
            print(colored(f"Error while running tests for {self.name}", "red"))
            print(result.stderr)

        result = json.loads(str(result.stdout))

        output = ""
        all_ok = True
        if not result:
            print(colored("MISSING", "red"), "missing tests")
            return
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

        subprocess.run(['/bin/bash', self.path + "/Source/destroy.sh"], cwd=self.path + "/Source/",
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


def CTFD_upload_challenge(challenge, URL, session, category_name=None):
    headers = {"Authorization": f"Token {session}"}

    if len(challenge.flag.keys()) > 1:
        part = 0
    else:
        part = None

    for flag in challenge.flag:
        if part is not None:
            part += 1
        with open(challenge.path + "/Description.md", "r") as f:
            description = f.read()
        if challenge.hosted:
            description += "\n\n "
            description += ''.join([
                elem for item in challenge.url for elem in
                ("\n\n", item.replace('{{PORT}}', challenge.port).replace('{{IP}}', HOSTNAME).replace('{{HOST}}', HOSTNAME))
            ])

        challenge_data = {
            "name": challenge.name + f" p{str(part)}" if part else challenge.name,
            "category": category_name if category_name else "",
            "description": description,
            "value": challenge.flag[flag],
            "type": "standard",
            "state": "hidden"
        }

        response = requests.post(f"{URL}/api/v1/challenges", json=challenge_data, headers=headers)
        if response.status_code == 200:
            print(colored(f"Uploaded challenge {challenge.name}", "green"))
        else:
            print(response.text)
            print(colored(f"Failed to upload challenge {challenge.name}", "red"))
            continue


        challenge_id = response.json()["data"]["id"]

        flag_data = {
            "challenge_id": challenge_id,
            "content": flag,
            "type": "static",
            "data": "",
        }
        flag_response = requests.post(f"{URL}/api/v1/flags", json=flag_data, headers=headers)
        if flag_response.status_code == 200:
            print(colored(f"    - Uploaded flag for {challenge.name}", "green"))
        else:
            print(flag_response.text)
            print(colored(f"    - Failed to upload flag for {challenge.name}", "red"))
            continue

        if not os.path.exists(challenge.path + "/Handout"):
            continue
        for filename in os.listdir(challenge.path + "/Handout"):
            file_path = os.path.join(challenge.path + "/Handout", filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    files = {
                        'file': (filename, file)
                    }
                    file_response = requests.post(f"{URL}/api/v1/files", headers=headers, files=files,
                                                  data={"challenge_id": challenge_id, "type": "challenge"})
                    if file_response.status_code != 200:
                        print(f"     - Error uploading {filename}:", file_response.json())
                    else:
                        print(f"     - Uploaded {filename} successfully.")


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
    parser.add_argument("--CTFd", type=str, const="*", nargs='?', help="Upload challenges to a specified CTFd instance. Provide the URL and API key as arguments (e.g., --CTFd <url> <key>).")

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
                uuids = toml.load(dirpath + "/challenge.toml").keys()
                for uuid in uuids:
                    if uuid in challenges.keys() or uuid in categories.keys():
                        if args.check:
                            print(colored(f"Duplicate uuid found: {uuid}", "red"))
                        continue

                    challenges[uuid] = Challenge(dirpath, uuid)

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
    allocated_ports = {}
    for uuid in sorted(challenges.keys()):
        if challenges[uuid].path in allocated_ports.keys():
            challenges[uuid].port = allocated_ports[challenges[uuid].path]
        else:
            challenges[uuid].allocate_port()
            if challenges[uuid].port:
                allocated_ports[challenges[uuid].path] = challenges[uuid].port

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
    if args.test:
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.test.split(",")) or args.test == "*"):
                continue
            print(challenges[uuid].name)
            challenges[uuid].run()
            challenges[uuid].test()
            challenges[uuid].stop()
    if args.run:
        deployed = []
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.run.split(",")) or args.run == "*"):
                continue
            if challenges[uuid].path not in deployed:
                challenges[uuid].run()
                deployed.append(challenges[uuid].path)
    if args.stop:
        for uuid in challenges:
            if not (any(item in challenges[uuid].name for item in args.stop.split(",")) or args.stop == "*"):
                continue
            challenges[uuid].stop()
    if args.CTFd:
        ctfd_url, ctfd_token = args.CTFd.split()

        for uuid, category in categories.items():
            for challenge in category.challenges:
                CTFD_upload_challenge(challenge, ctfd_url, ctfd_token, category_name=category.name)