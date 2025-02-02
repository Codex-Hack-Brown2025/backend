from dotenv import load_dotenv
load_dotenv()

import os
import subprocess
import re
import json
import requests
import sys

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

    if process.returncode != 0:
        raise RuntimeError(f"Error: {stderr.decode(encoding)}")

    ignored_files = stdout.decode(encoding).splitlines()

    return set(ignored_files)

def revert_translations():

    ignore_files = get_ignored_files()
    # Iterate through all files in the repository
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                filepath = os.path.join(root, file).lstrip("./")
                if filepath in ignore_files:
                    continue

                comment_filepath = f"./comment_files/{filepath.lstrip("./").replace("/", ".")}.comments.json"
                with open(comment_filepath, "r") as comment_json:
                    comment_data = json.load(comment_json)

                with open(filepath, "r") as f:
                    lines = f.readlines()

                landmark_ids = []
                for line in lines:
                    matches = [
                        match.group(1) for match in re.finditer(r"%\^([A-Za-z0-9_-]+)\^%", line)
                    ]
                    if len(matches) > 0:
                        landmark = matches[0]
                        landmark_ids.append(comment_data[landmark]['landmark_id'])
                
                r = requests.post(os.environ["TRANSLATION_BACKEND_URL"] + "/get_translations",
                            data = json.dumps({
                                "landmark_ids": landmark_ids,
                                "target_language": "chinese"}),
                            headers = {
                                "Content-Type": "application/json"
                            })
                
                if r.status_code != 200:
                    print(r.text)
                    print(r.status_code)
                    raise Exception("Request error")
                result = r.json()

                for landmark_id in result:
                    landmark = landmark_id.split("@")[0]
                    comment_data[landmark]["comment"] = result[landmark_id]

