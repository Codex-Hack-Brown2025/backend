import os
from your_translation_module import translate_text  # Replace with your translation logic

def apply_translations():
    # Define the target language (e.g., "es" for Spanish)
    target_language = "es"

    # Iterate through all files in the repository
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    lines = f.readlines()

                # Translate comments and write back to the file
                with open(filepath, "w") as f:
                    for line in lines:
                        if line.strip().startswith("#"):
                            # Translate the comment
                            translated_comment = translate_text(line.strip(), target_language)
                            f.write(f"# [{target_language}] {translated_comment}\n")
                        else:
                            f.write(line)

if __name__ == "__main__":
    apply_translations()
