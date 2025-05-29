import os
import sys

def search_string_in_project(search_term, directory=".", extensions=(".py", ".json")):
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if search_term in line:
                                matches.append((file_path, i, line.strip()))
                except (UnicodeDecodeError, FileNotFoundError):
                    continue

    if matches:
        print(f"\nSøkeresultater for '{search_term}':")
        for path, line_no, content in matches:
            print(f"{path} (linje {line_no}): {content}")
    else:
        print(f"\nIngen treff for '{search_term}' i .py eller .json filer.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bruk: python search_project.py <søkeord>")
    else:
        search_term = sys.argv[1]
        search_string_in_project(search_term)
