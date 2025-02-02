import os

import subprocess

import re

import json

import sys

import urllib.request



def get_ignored_files():

    # Collect all files (excluding .git directory)

    file_paths = []

    for root, dirs, files in os.walk("."):

        if ".git" in dirs:

            dirs.remove(".git")  # Skip .git directory

        for file in files:

            rel_path = os.path.relpath(os.path.join(root, file))

            file_paths.append(rel_path)



    # Run git check-ignore with stdin

    encoding = sys.getfilesystemencoding()

    process = subprocess.Popen(

        ["git", "check-ignore", "--stdin"],

        stdin=subprocess.PIPE,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

    )



    # Send paths to stdin and capture output

    stdout, stderr = process.communicate(

        input="\n".join(file_paths).encode(encoding)

    )



    if process.returncode != 0 and len(stderr) > 0:

        raise RuntimeError(f"Error: {stderr.decode(encoding)}")



    ignored_files = stdout.decode(encoding).splitlines()



    return set(ignored_files)



def pre_translations():

    ignore_files = get_ignored_files()

    # Iterate through all files in the repository

    for root, _, files in os.walk("."):

        for file in files:

            if file.startswith("./.git"):

                continue

            if file.endswith(".py"):  # Only process Python files

                filepath = os.path.join(root, file)[2:]

                if filepath in ignore_files:

                    continue

                with open(filepath, "r") as f:

                    lines = f.readlines()

                # Revert translated comments to landmarks

                with open(filepath, "w") as f:

                    for line in lines:

                        matches = [

                            (match.group(1), match.start(1), match.end(1))

                            for match in re.finditer(r"%\^([A-Za-z0-9_-]+)\^%", line)

                        ]

                        if len(matches) > 0:

                            landmark, start, _ = matches[0]

                            f.write(f"{line[:start]}{landmark}^%\n")

                        else:

                            f.write(line)


if __name__ == "__main__":
    pre_translations()


