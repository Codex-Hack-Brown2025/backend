import os

import subprocess

import re

import json

import sys

import urllib3



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



def convert_landmarks(user_name):

    

    lang_preference = "english"

    if user_name is not None:

        try:

            http = urllib3.PoolManager()
            url = "http://54.90.74.38/api/get_user_preference"
            data = json.dumps({"user_name": user_name}).encode("utf-8")
            headers = {"Content-Type": "application/json"}

            response = http.request("POST", url, body=data, headers=headers)

            if (response.status == 200):

                result = json.loads(response.data.decode("utf-8")) 

                lang_preference = result["language"]

        except:

            pass



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



                landmark2comments = dict()

                # Revert translated comments to landmarks and store new comments

                with open(filepath, "w") as f:

                    for line in lines:

                        matches = [

                            (match.group(1), match.start(1), match.end(1))

                            for match in re.finditer(r"%\^([A-Za-z0-9_-]+)\^%", line)

                        ]

                        if len(matches) > 0:

                            landmark, start, end = matches[0]

                            comment = line[end + 2:].rstrip()

                            landmark2comments[landmark] = comment

                            f.write(f"{line[:start]}{landmark}^%\n")

                        else:

                            f.write(line)

                

                landmark_id_to_comments = dict()

                # process the corresponding comment file for each .py file

                comment_filepath = f"./comment_files/{filepath.replace('/', '.')}.comments.json"

                if not os.path.isfile(comment_filepath):

                    open(comment_filepath, 'a').close()

                with open(comment_filepath, "r") as comment_json:

                    try:

                        comment_data = json.load(comment_json)

                    except:

                        comment_data = dict()

                    for landmark, comment in landmark2comments.items():

                        if landmark not in comment_data:

                            landmark_id_to_comments[f"{landmark}@NEW"] = comment

                        else:

                            landmark_id_to_comments[comment_data[landmark]["landmark_id"]] = comment

                

                http = urllib3.PoolManager()
                url = "http://54.90.74.38/api/update_translations"
                data = json.dumps({
                  "landmark_id_to_comments": landmark_id_to_comments,
                  "current_language": lang_preference
                }).encode("utf-8")

                headers = {"Content-Type": "application/json"}

                response = http.request("POST", url, body=data, headers=headers)

                if response.status != 200:

                    raise Exception("Request error")
                result = result = json.loads(response.data.decode("utf-8"))
                with open(comment_filepath, "w") as comment_json:

                    json.dump(result, comment_json)





if __name__ == "__main__":

    user_name = None

    if len(sys.argv) == 2:

        user_name = sys.argv[1]

    convert_landmarks(user_name)


