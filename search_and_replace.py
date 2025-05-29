import os
import sys


def search_and_optionally_replace(directory, target, replacement):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py") or filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except UnicodeDecodeError:
                    print(f"[IGNORED] {file_path} (encoding issue)")
                    continue

                updated_lines = []
                changed = False
                for idx, line in enumerate(lines):
                    if target in line:
                        print(f"\n[FOUND] {file_path}, line {idx + 1}:")
                        print(f"    {line.strip()}")
                        new_line = line.replace(target, replacement)
                        print(f"--> {new_line.strip()}")
                        confirm = input("Apply change? (y/n): ").lower()
                        if confirm == "y":
                            updated_lines.append(new_line)
                            changed = True
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)

                if changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(updated_lines)
                    print(f"[UPDATED] {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python search_and_replace.py <target_string> <replacement_string>")
        sys.exit(1)

    target_str = sys.argv[1]
    replacement_str = sys.argv[2]

    print(f"Searching for '{target_str}' and replacing with '{replacement_str}' if approved.")
    search_and_optionally_replace(".", target_str, replacement_str)
