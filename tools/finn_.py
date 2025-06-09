
import os
import sys

def search_string_in_project(directory, search_string):
    excluded_dirs = {'venv', '.venv'}
    for root, dirs, files in os.walk(directory):
        # Fjern ekskluderte mapper fra søk
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if search_string in line:
                            print(f"{file_path}:{i}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Bruk: python finn.py <mappe> <søkeord>")
        sys.exit(1)

    search_path = sys.argv[1]
    query = sys.argv[2]
    search_string_in_project(search_path, query)
