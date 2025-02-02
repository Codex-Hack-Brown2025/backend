import os
import re

def revert_translations():
    # Define a regex pattern to detect translated comments
    translated_comment_pattern = re.compile(r"# \[.*\] .*")

    # Iterate through all files in the repository
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    lines = f.readlines()

                # Revert translated comments to English
                with open(filepath, "w") as f:
                    for line in lines:
                        if translated_comment_pattern.match(line):
                            # Replace the translated comment with the original
                            original_comment = line.split("] ")[1]
                            f.write(f"# {original_comment}")
                        else:
                            f.write(line)

if __name__ == "__main__":
    revert_translations()

