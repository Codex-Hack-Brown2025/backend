import os
import re
import json

def revert_translations():

    # Iterate through all files in the repository
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                filepath = os.path.join(root, file)
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
                            comment = line[end + 2:]
                            landmark2comments[landmark] = comment
                            f.write(f"{line[:start]}{landmark}^%")
                        else:
                            f.write(line)
                
                landmark_id_to_comments = dict()
                # Read landmark ids from corresponding comment file for each .py file
                comment_filepath = f"./comment_files/{filepath.replace("/", ".")}.comments.json"
                with open(comment_filepath, "r") as comment_json:
                    comment_data = json.load(comment_json)
                    for landmark, comment in landmark2comments.items():
                        if landmark not in comment_data:
                            landmark_id_to_comments[f"{landmark}@NEW"] = comment
                        else:
                            landmark_id_to_comments[comment_data[landmark]["landmark_id"]] = comment
                
                # TODO: call API


if __name__ == "__main__":
    revert_translations()

